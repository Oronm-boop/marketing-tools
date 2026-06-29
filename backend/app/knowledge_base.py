from datetime import datetime
from typing import Any
from urllib.parse import quote
from uuid import uuid4

import httpx
from fastapi import UploadFile

from .config import Settings
from .schemas import KnowledgeBase, KnowledgeBaseDocument, KnowledgeBaseReference


class KnowledgeBaseServiceError(RuntimeError):
    pass


class KnowledgeBaseClient:
    def __init__(self, settings: Settings):
        self.base_url = settings.knowledge_base_url.rstrip("/")
        self.timeout = settings.knowledge_base_timeout_seconds

    async def list_knowledge_bases(self) -> list[KnowledgeBase]:
        payload = await self._request("GET", "/collections")
        collections = _extract_list(payload, ("collections", "items"))
        knowledge_bases: list[KnowledgeBase] = []

        for item in collections:
            collection_name = _extract_collection_name(item)
            if not collection_name:
                continue
            documents = await self.list_documents(collection_name)
            latest_uploaded_at = max((document.uploadedAt for document in documents), default=0)
            updated_at = _extract_collection_updated_at(item) or _format_date(latest_uploaded_at)
            knowledge_bases.append(
                KnowledgeBase(
                    id=collection_name,
                    name=collection_name,
                    documentCount=len(documents),
                    updatedAt=updated_at,
                    documents=documents,
                )
            )

        return knowledge_bases

    async def create_knowledge_base(self, collection_name: str) -> KnowledgeBase:
        await self._request(
            "POST",
            "/collections/create",
            json={"collection_name": collection_name},
        )
        return KnowledgeBase(
            id=collection_name,
            name=collection_name,
            documentCount=0,
            updatedAt=_format_date(_now_ms()),
            documents=[],
        )

    async def delete_knowledge_base(self, collection_name: str) -> None:
        await self._request(
            "DELETE",
            f"/collections/{quote(collection_name, safe='')}",
            params={"delete_kg": "true", "delete_files": "true"},
        )

    async def list_documents(self, collection_name: str) -> list[KnowledgeBaseDocument]:
        payload = await self._request(
            "GET",
            "/parsed/files",
            params={"collection_name": collection_name},
        )
        files = _extract_list(payload, ("files", "items", "documents", "parsed_files"))
        documents = [_normalize_document(item) for item in files]
        documents = [document for document in documents if document is not None]
        documents.sort(key=lambda document: document.uploadedAt, reverse=True)
        return documents

    async def upload_documents(
        self,
        collection_name: str,
        files: list[UploadFile],
    ) -> list[KnowledgeBaseDocument]:
        for file in files:
            file_id = uuid4().hex
            await file.seek(0)
            await self._request(
                "POST",
                "/process-all",
                data={"collection_name": collection_name, "file_id": file_id},
                files={
                    "file": (
                        file.filename or f"{file_id}.dat",
                        file.file,
                        file.content_type or "application/octet-stream",
                    )
                },
                allow_completed_temp_lock_error=True,
            )

        return await self.list_documents(collection_name)

    async def delete_document(self, collection_name: str, file_id: str) -> list[KnowledgeBaseDocument]:
        resolved_file_id = await self.resolve_document_id(collection_name, file_id)
        await self._request(
            "DELETE",
            f"/files/{quote(resolved_file_id, safe='')}",
            params={
                "collection_name": collection_name,
                "delete_from_kg": "true",
                "delete_local_files": "true",
            },
        )
        documents = await self.list_documents(collection_name)
        if any(document.id == resolved_file_id for document in documents):
            raise KnowledgeBaseServiceError(f"文件 {file_id} 删除后仍存在，请稍后刷新后重试")
        return documents

    async def resolve_document_id(self, collection_name: str, file_id_or_name: str) -> str:
        candidate = file_id_or_name.strip()
        if not candidate:
            raise KnowledgeBaseServiceError("缺少要删除的文件 ID")

        documents = await self.list_documents(collection_name)
        for document in documents:
            if candidate in {document.id, document.name, f"{document.id}.json"}:
                return document.id

        normalized_candidate = _file_id_from_filename(candidate)
        for document in documents:
            if normalized_candidate and normalized_candidate == document.id:
                return document.id

        return normalized_candidate or candidate

    async def retrieve_context(
        self,
        knowledge_base: KnowledgeBaseReference | None,
        query: str,
    ) -> str:
        if knowledge_base is None:
            return ""

        payload = await self._request(
            "POST",
            "/query",
            json={
                "query": query,
                "collection_name": knowledge_base.id,
                "top_k": 6,
                "rerank_top_k": 6,
                "use_kg": False,
                "use_reranking": True,
            },
        )
        return _format_query_context(knowledge_base, payload)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        allow_completed_temp_lock_error: bool = False,
        **kwargs: Any,
    ) -> Any:
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                response = await client.request(method, path, **kwargs)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise KnowledgeBaseServiceError(f"知识库服务请求超时：{self.base_url}{path}") from exc
        except httpx.HTTPStatusError as exc:
            if allow_completed_temp_lock_error and _is_completed_temp_lock_error(exc.response):
                return _read_response_json(exc.response)
            message = _extract_response_error(exc.response)
            raise KnowledgeBaseServiceError(f"知识库服务请求失败：{message}") from exc
        except httpx.HTTPError as exc:
            message = str(exc).strip() or f"无法连接到 {self.base_url}"
            raise KnowledgeBaseServiceError(f"知识库服务网络请求失败：{message}") from exc

        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError as exc:
            raise KnowledgeBaseServiceError("知识库服务返回了非 JSON 内容") from exc


def _extract_list(payload: Any, keys: tuple[str, ...]) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []

    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return value

    for nested_key in ("result", "data"):
        nested = payload.get(nested_key)
        if isinstance(nested, list):
            return nested
        if isinstance(nested, dict):
            nested_result = _extract_list(nested, keys)
            if nested_result:
                return nested_result

    return []


def _extract_collection_name(item: Any) -> str:
    if isinstance(item, str):
        return item.strip()
    if not isinstance(item, dict):
        return ""
    for key in ("name", "collection_name", "collectionName", "id"):
        value = item.get(key)
        if value:
            return str(value).strip()
    return ""


def _extract_collection_updated_at(item: Any) -> str:
    if not isinstance(item, dict):
        return ""
    for key in ("updatedAt", "updated_at", "updated", "created_at", "createdAt"):
        timestamp = _to_timestamp_ms(item.get(key))
        if timestamp:
            return _format_date(timestamp)
    return ""


def _normalize_document(item: Any) -> KnowledgeBaseDocument | None:
    if isinstance(item, str):
        file_id = _file_id_from_filename(item)
        return KnowledgeBaseDocument(id=file_id, name=item, size=0, uploadedAt=0) if file_id else None
    if not isinstance(item, dict):
        return None

    metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
    stored_filename = _first_text(
        item,
        metadata,
        ("file_id", "fileId", "filename", "file_name", "file_path", "id"),
    )
    display_name = _first_text(
        item,
        metadata,
        ("original_filename", "originalFilename", "source_filename", "sourceFilename", "name", "filename", "file_name"),
    )
    file_id = _first_text(item, metadata, ("file_id", "fileId", "id"))
    if not file_id:
        file_id = _file_id_from_filename(stored_filename)
    if not file_id:
        return None

    display_name = display_name or file_id
    size = _first_int(item, metadata, ("size", "file_size", "fileSize", "bytes"))
    uploaded_at = _first_timestamp(
        item,
        metadata,
        (
            "uploadedAt",
            "uploaded_at",
            "createdAt",
            "created_at",
            "updatedAt",
            "updated_at",
            "modifiedAt",
            "modified_at",
            "mtime",
            "timestamp",
        ),
    )

    return KnowledgeBaseDocument(
        id=file_id,
        name=display_name,
        size=size,
        uploadedAt=uploaded_at,
    )


def _format_query_context(knowledge_base: KnowledgeBaseReference, payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""

    context = payload.get("context")
    if isinstance(context, str) and context.strip():
        return "\n".join(
            [
                f"知识库：{knowledge_base.name or knowledge_base.id}",
                _trim_text(context, 6000),
            ]
        )

    results = _extract_list(payload, ("reranked_results", "vector_results", "results", "items"))
    sections = [f"知识库：{knowledge_base.name or knowledge_base.id}"]
    for index, item in enumerate(results[:6], start=1):
        if not isinstance(item, dict):
            continue
        text = str(item.get("text") or item.get("content") or "").strip()
        if not text:
            continue
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        source = _first_text(item, metadata, ("filename", "source", "file_name", "original_filename"))
        score = item.get("score")
        source_line = f"来源：{source}" if source else "来源：知识库片段"
        score_line = f"相关度：{score}" if score is not None else ""
        sections.append(
            "\n".join(
                part
                for part in [
                    f"{index}. {source_line}",
                    score_line,
                    f"内容：{_trim_text(text, 900)}",
                ]
                if part
            )
        )

    return "\n\n".join(sections) if len(sections) > 1 else ""


def _first_text(
    primary: dict[str, Any],
    secondary: dict[str, Any],
    keys: tuple[str, ...],
) -> str:
    for source in (primary, secondary):
        for key in keys:
            value = source.get(key)
            if value:
                return str(value).strip()
    return ""


def _first_int(
    primary: dict[str, Any],
    secondary: dict[str, Any],
    keys: tuple[str, ...],
) -> int:
    for source in (primary, secondary):
        for key in keys:
            try:
                return max(0, int(float(source.get(key))))
            except (TypeError, ValueError):
                continue
    return 0


def _first_timestamp(
    primary: dict[str, Any],
    secondary: dict[str, Any],
    keys: tuple[str, ...],
) -> int:
    for source in (primary, secondary):
        for key in keys:
            timestamp = _to_timestamp_ms(source.get(key))
            if timestamp:
                return timestamp
    return 0


def _to_timestamp_ms(value: Any) -> int:
    if value is None or value == "":
        return 0
    if isinstance(value, (int, float)):
        number = int(value)
        return number if number > 10_000_000_000 else number * 1000
    if isinstance(value, str):
        text = value.strip()
        try:
            number = float(text)
        except ValueError:
            number = 0
        if number:
            return _to_timestamp_ms(number)
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return 0
        return int(parsed.timestamp() * 1000)
    return 0


def _file_id_from_filename(filename: str) -> str:
    if not filename:
        return ""
    name = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    if name.endswith(".json"):
        name = name[:-5]
    for prefix in ("chunks_", "kg_"):
        if name.startswith(prefix):
            name = name[len(prefix) :]
    return name.strip()


def _format_date(timestamp_ms: int) -> str:
    if not timestamp_ms:
        return ""
    return datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d")


def _now_ms() -> int:
    return int(datetime.now().timestamp() * 1000)


def _trim_text(value: str, limit: int) -> str:
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def _extract_response_error(response: httpx.Response) -> str:
    data = _read_response_json(response)
    if data is None:
        return response.text[:500] or f"HTTP {response.status_code}"

    if isinstance(data, dict):
        message = _extract_payload_message(data)
        if message:
            return message[:500]
    return str(data)[:500]


def _read_response_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def _extract_payload_message(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("detail", "error", "message"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, dict):
                nested = _extract_payload_message(value)
                if nested:
                    return nested
        return ""
    return str(payload or "").strip()


def _extract_process_log(payload: Any) -> list[Any]:
    if not isinstance(payload, dict):
        return []
    process_log = payload.get("process_log")
    if isinstance(process_log, list):
        return process_log
    detail = payload.get("detail")
    if isinstance(detail, dict):
        return _extract_process_log(detail)
    return []


def _is_completed_temp_lock_error(response: httpx.Response) -> bool:
    payload = _read_response_json(response)
    message = _extract_payload_message(payload)
    if "WinError 32" not in message and "另一个程序正在使用此文件" not in message:
        return False
    normalized_message = message.replace("/", "\\")
    if "temp\\" not in normalized_message:
        return False

    process_log = _extract_process_log(payload)
    if not process_log:
        return False
    return all(isinstance(step, dict) and step.get("status") == "completed" for step in process_log)
