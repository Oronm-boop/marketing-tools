import logging

from pydantic import TypeAdapter, ValidationError

from .config import Settings
from .json_utils import JSONExtractionError, extract_json_payload
from .local_model_client import LocalModelClient, LocalModelClientError
from .prompts import SYSTEM_PROMPT, build_copywriting_user_prompt, build_seo_user_prompt
from .schemas import (
    CopywritingItem,
    CopywritingRequest,
    CopywritingResponse,
    SeoKeywordItem,
    SeoKeywordRequest,
    SeoKeywordResponse,
)


logger = logging.getLogger(__name__)

MAX_RAW_PREVIEW = 2000


class GenerationServiceError(RuntimeError):
    pass


class GenerationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = LocalModelClient(settings)

    async def generate_seo_keywords(self, payload: SeoKeywordRequest) -> SeoKeywordResponse:
        content = await self._call_model(
            build_seo_user_prompt(payload),
            temperature=0.6,
            max_tokens=min(self.settings.local_model_max_tokens, 2048),
            api_mode="completions",
        )
        raw_items = _extract_items(content, label="SEO 关键词")

        try:
            items = TypeAdapter(list[SeoKeywordItem]).validate_python(raw_items)
        except ValidationError as exc:
            raise GenerationServiceError(f"SEO 关键词 JSON 字段校验失败：{exc}") from exc

        return SeoKeywordResponse(items=items[: payload.keyword_count], model=self.settings.local_model_name)

    async def generate_copywriting(self, payload: CopywritingRequest) -> CopywritingResponse:
        content = await self._call_model(
            build_copywriting_user_prompt(payload),
            temperature=0.5,
            max_tokens=max(self.settings.local_model_max_tokens, 3072),
            api_mode="chat",
        )
        raw_items = _extract_items(content, label="宣传文案")

        for item in raw_items:
            if isinstance(item, dict):
                item["actual_keyword_count"] = str(item.get("content", "")).count(payload.keyword)

        try:
            items = TypeAdapter(list[CopywritingItem]).validate_python(raw_items)
        except ValidationError as exc:
            raise GenerationServiceError(f"宣传文案 JSON 字段校验失败：{exc}") from exc

        return CopywritingResponse(items=items[: payload.article_count], model=self.settings.local_model_name)

    async def _call_model(
        self,
        user_prompt: str,
        temperature: float,
        max_tokens: int | None = None,
        api_mode: str = "completions",
    ) -> str:
        try:
            return await self.client.complete_json(
                SYSTEM_PROMPT,
                user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                api_mode=api_mode,
            )
        except LocalModelClientError as exc:
            raise GenerationServiceError(str(exc)) from exc


def _extract_items(content: str, label: str = "模型输出") -> list[dict]:
    try:
        payload = extract_json_payload(content)
    except JSONExtractionError as exc:
        logger.warning("%s 解析失败，原始内容预览：%s", label, content[:MAX_RAW_PREVIEW])
        raise GenerationServiceError(str(exc)) from exc

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]

    raise GenerationServiceError("模型返回 JSON 中缺少 items 数组")
