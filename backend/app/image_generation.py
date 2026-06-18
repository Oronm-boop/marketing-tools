from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from random import randint
from typing import Any
from uuid import uuid4

import httpx

from .config import Settings
from .schemas import (
    GeneratedImageFile,
    ImageGenerationRequest,
    ImageGenerationStatusResponse,
    ImageGenerationTaskResponse,
)


class ImageGenerationServiceError(RuntimeError):
    pass


@dataclass(frozen=True)
class GeneratedImageContent:
    content: bytes
    media_type: str
    etag: str
    cache_hit: bool


COMFYUI_WORKFLOW: dict[str, Any] = {
    "1": {
        "inputs": {
            "unet_name": "z_image_turbo_bf16.safetensors",
            "weight_dtype": "default",
        },
        "class_type": "UNETLoader",
        "_meta": {"title": "UNet加载器"},
    },
    "2": {
        "inputs": {
            "clip_name": "qwen_3_4b.safetensors",
            "type": "qwen_image",
            "device": "default",
        },
        "class_type": "CLIPLoader",
        "_meta": {"title": "加载CLIP"},
    },
    "3": {
        "inputs": {"vae_name": "ae.safetensors"},
        "class_type": "VAELoader",
        "_meta": {"title": "加载VAE"},
    },
    "4": {
        "inputs": {
            "seed": 184420318989244,
            "steps": 10,
            "cfg": 1,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 1,
            "model": ["1", 0],
            "positive": ["5", 0],
            "negative": ["6", 0],
            "latent_image": ["7", 0],
        },
        "class_type": "KSampler",
        "_meta": {"title": "K采样器"},
    },
    "5": {
        "inputs": {
            "text": ["17", 0],
            "clip": ["2", 0],
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "CLIP文本编码"},
    },
    "6": {
        "inputs": {"conditioning": ["5", 0]},
        "class_type": "ConditioningZeroOut",
        "_meta": {"title": "条件零化"},
    },
    "7": {
        "inputs": {
            "width": 1920,
            "height": 1080,
            "batch_size": 1,
        },
        "class_type": "EmptyLatentImage",
        "_meta": {"title": "空Latent图像"},
    },
    "8": {
        "inputs": {
            "samples": ["4", 0],
            "vae": ["3", 0],
        },
        "class_type": "VAEDecode",
        "_meta": {"title": "VAE解码"},
    },
    "10": {
        "inputs": {
            "filename_prefix": "MDTMarketing",
            "images": ["8", 0],
        },
        "class_type": "SaveImage",
        "_meta": {"title": "保存图像"},
    },
    "17": {
        "inputs": {"prompt": ""},
        "class_type": "CR Prompt Text",
        "_meta": {"title": "⚙ CR Prompt Text"},
    },
}


class ComfyUIImageGenerationService:
    def __init__(self, settings: Settings):
        self.base_url = settings.comfyui_base_url.rstrip("/")
        self.timeout = settings.comfyui_timeout_seconds
        self.cache_dir = settings.generated_image_cache_dir
        self.cache_max_age_seconds = settings.generated_image_cache_max_age_seconds

    async def submit_task(
        self,
        payload: ImageGenerationRequest,
    ) -> ImageGenerationTaskResponse:
        workflow = self._build_workflow(payload)
        request_body = {
            "client_id": str(uuid4()),
            "prompt": workflow,
        }
        data = await self._request_json("POST", "/prompt", json=request_body)

        node_errors = data.get("node_errors")
        if isinstance(node_errors, dict) and node_errors:
            raise ImageGenerationServiceError(f"绘图任务下发失败：{node_errors}")

        prompt_id = str(data.get("prompt_id") or "").strip()
        if not prompt_id:
            raise ImageGenerationServiceError("绘图任务下发成功但未返回 prompt_id")

        return ImageGenerationTaskResponse(prompt_id=prompt_id)

    async def get_task_status(self, prompt_id: str) -> ImageGenerationStatusResponse:
        data = await self._request_json("GET", f"/history/{prompt_id}")
        task = self._resolve_history_entry(data, prompt_id)

        if task is None:
            return ImageGenerationStatusResponse(prompt_id=prompt_id, status="pending")

        status = task.get("status") if isinstance(task, dict) else {}
        status_str = str(status.get("status_str") or "").lower() if isinstance(status, dict) else ""
        completed = bool(status.get("completed")) if isinstance(status, dict) else False
        message = self._extract_status_message(status)

        if status_str in {"error", "failed"}:
            return ImageGenerationStatusResponse(
                prompt_id=prompt_id,
                status="failed",
                message=message or "图片生成失败",
            )

        image = self._extract_first_image(task)
        if image:
            return ImageGenerationStatusResponse(
                prompt_id=prompt_id,
                status="success",
                image=image,
            )

        if completed:
            return ImageGenerationStatusResponse(
                prompt_id=prompt_id,
                status="failed",
                message=message or "任务已完成但未找到生成图片",
            )

        return ImageGenerationStatusResponse(prompt_id=prompt_id, status="running")

    async def read_image(
        self,
        filename: str,
        image_type: str,
        subfolder: str,
        preview: str,
        channel: str,
    ) -> GeneratedImageContent:
        params = {
            "filename": filename,
            "type": image_type,
            "subfolder": subfolder,
            "preview": preview,
            "channel": channel,
        }
        cache_key = self._build_image_cache_key(params)
        cached_image = self._read_cached_image(cache_key)
        if cached_image:
            content, media_type = cached_image
            return GeneratedImageContent(
                content=content,
                media_type=media_type,
                etag=self._build_etag(cache_key),
                cache_hit=True,
            )

        content, media_type = await self._fetch_image_from_comfyui(params)
        self._write_cached_image(cache_key, content, media_type)
        return GeneratedImageContent(
            content=content,
            media_type=media_type,
            etag=self._build_etag(cache_key),
            cache_hit=False,
        )

    async def _fetch_image_from_comfyui(self, params: dict[str, str]) -> tuple[bytes, str]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/view", params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ImageGenerationServiceError(f"读取图片失败：{exc}") from exc

        media_type = response.headers.get("content-type") or "image/png"
        return response.content, media_type

    def _read_cached_image(self, cache_key: str) -> tuple[bytes, str] | None:
        image_path = self._cache_image_path(cache_key)
        if not image_path.exists():
            return None

        try:
            content = image_path.read_bytes()
            media_type = self._read_cached_image_media_type(cache_key)
        except OSError:
            return None

        return content, media_type

    def _write_cached_image(self, cache_key: str, content: bytes, media_type: str) -> None:
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            image_path = self._cache_image_path(cache_key)
            meta_path = self._cache_meta_path(cache_key)

            image_tmp_path = image_path.with_name(f"{image_path.name}.{uuid4().hex}.tmp")
            meta_tmp_path = meta_path.with_name(f"{meta_path.name}.{uuid4().hex}.tmp")

            image_tmp_path.write_bytes(content)
            image_tmp_path.replace(image_path)

            meta_tmp_path.write_text(
                json.dumps({"media_type": media_type}, ensure_ascii=False),
                encoding="utf-8",
            )
            meta_tmp_path.replace(meta_path)
        except OSError:
            return

    def _read_cached_image_media_type(self, cache_key: str) -> str:
        meta_path = self._cache_meta_path(cache_key)
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return "image/png"

        media_type = meta.get("media_type") if isinstance(meta, dict) else None
        return str(media_type) if media_type else "image/png"

    def _cache_image_path(self, cache_key: str) -> Path:
        return self.cache_dir / f"{cache_key}.bin"

    def _cache_meta_path(self, cache_key: str) -> Path:
        return self.cache_dir / f"{cache_key}.json"

    @staticmethod
    def _build_image_cache_key(params: dict[str, str]) -> str:
        payload = json.dumps({"version": 1, **params}, ensure_ascii=False, sort_keys=True)
        return sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _build_etag(cache_key: str) -> str:
        return f'"{cache_key}"'

    def _build_workflow(self, payload: ImageGenerationRequest) -> dict[str, Any]:
        workflow = deepcopy(COMFYUI_WORKFLOW)
        workflow["4"]["inputs"]["seed"] = randint(1, 2**48 - 1)
        workflow["7"]["inputs"]["width"] = payload.width
        workflow["7"]["inputs"]["height"] = payload.height
        workflow["7"]["inputs"]["batch_size"] = payload.batch_size
        workflow["10"]["inputs"]["filename_prefix"] = "MDTMarketing"
        workflow["17"]["inputs"]["prompt"] = payload.prompt
        return workflow

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, f"{self.base_url}{path}", json=json)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise ImageGenerationServiceError(f"ComfyUI 接口调用失败：{exc}") from exc
        except ValueError as exc:
            raise ImageGenerationServiceError("ComfyUI 返回了无法解析的 JSON") from exc

        if not isinstance(data, dict):
            raise ImageGenerationServiceError("ComfyUI 返回结构不是 JSON 对象")
        return data

    @staticmethod
    def _resolve_history_entry(
        data: dict[str, Any],
        prompt_id: str,
    ) -> dict[str, Any] | None:
        direct = data.get(prompt_id)
        if isinstance(direct, dict):
            return direct

        if len(data) == 1:
            only_value = next(iter(data.values()))
            if isinstance(only_value, dict):
                return only_value

        return None

    @staticmethod
    def _extract_first_image(task: dict[str, Any]) -> GeneratedImageFile | None:
        outputs = task.get("outputs")
        if not isinstance(outputs, dict):
            return None

        for output in outputs.values():
            if not isinstance(output, dict):
                continue
            images = output.get("images")
            if not isinstance(images, list):
                continue

            for image in images:
                if not isinstance(image, dict):
                    continue
                filename = str(image.get("filename") or "").strip()
                if filename:
                    return GeneratedImageFile(
                        filename=filename,
                        subfolder=str(image.get("subfolder") or ""),
                        type=str(image.get("type") or "output"),
                    )

        return None

    @staticmethod
    def _extract_status_message(status: Any) -> str:
        if not isinstance(status, dict):
            return ""

        messages = status.get("messages")
        if isinstance(messages, list):
            flattened: list[str] = []
            for item in messages:
                if isinstance(item, (list, tuple)):
                    flattened.extend(str(part) for part in item if part)
                elif item:
                    flattened.append(str(item))
            return "；".join(flattened[-3:])

        return str(status.get("status_str") or "")
