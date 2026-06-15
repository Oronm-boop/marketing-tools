from typing import Any

import httpx

from .config import Settings


class QwenClientError(RuntimeError):
    pass


class QwenClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def chat_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        if self.settings.qwen_api_key is None:
            raise QwenClientError("缺少 QWEN_API_KEY，请在后端环境变量或后端 .env 中配置百炼 API Key")

        endpoint = self.settings.qwen_base_url.rstrip("/") + "/chat/completions"
        payload: dict[str, Any] = {
            "model": self.settings.qwen_model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if self.settings.qwen_enable_thinking:
            payload["enable_thinking"] = True
        headers = {
            "Authorization": f"Bearer {self.settings.qwen_api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            message = _extract_provider_error(exc.response)
            raise QwenClientError(f"Qwen API 请求失败：{message}") from exc
        except httpx.HTTPError as exc:
            raise QwenClientError(f"Qwen API 网络请求失败：{exc}") from exc

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise QwenClientError("Qwen API 返回结构异常") from exc


def _extract_provider_error(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text[:500]

    error = data.get("error")
    if isinstance(error, dict):
        return str(error.get("message") or error.get("code") or data)
    return str(data)[:500]
