from typing import Any

import httpx

from .config import Settings


class LocalModelClientError(RuntimeError):
    pass


class LocalModelClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        # ollama provider 使用单独的 base_url / model_name
        if settings.model_provider == "ollama":
            self._base_url = settings.ollama_base_url
            self._model_name = settings.ollama_model
        else:
            self._base_url = settings.local_model_base_url
            self._model_name = settings.local_model_name

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        api_mode: str = "completions",
    ) -> str:
        if api_mode == "chat":
            endpoint = self._base_url.rstrip("/") + "/chat/completions"
            payload = self._build_chat_payload(system_prompt, user_prompt, temperature, max_tokens)
        else:
            endpoint = self._base_url.rstrip("/") + "/completions"
            payload = self._build_completions_payload(system_prompt, user_prompt, temperature, max_tokens)

        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise LocalModelClientError(
                f"本地模型请求超时，当前超时时间 {self.settings.request_timeout_seconds} 秒"
            ) from exc
        except httpx.HTTPStatusError as exc:
            message = _extract_provider_error(exc.response)
            raise LocalModelClientError(f"本地模型请求失败：{message}") from exc
        except httpx.HTTPError as exc:
            raise LocalModelClientError(f"本地模型网络请求失败：{exc}") from exc

        data = response.json()
        try:
            content = _extract_completion_text(data)
        except (KeyError, IndexError, TypeError) as exc:
            raise LocalModelClientError("本地模型返回结构异常") from exc
        if not content.strip():
            raise LocalModelClientError("本地模型返回空内容")
        return content

    def _build_completions_payload(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int | None,
    ) -> dict[str, Any]:
        return {
            "model": self._model_name,
            "prompt": build_completion_prompt(system_prompt, user_prompt),
            "max_tokens": max_tokens or self.settings.local_model_max_tokens,
            "temperature": temperature,
            "top_p": self.settings.local_model_top_p,
            "stream": False,
        }

    def _build_chat_payload(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self._model_name,
            "messages": build_chat_messages(system_prompt, user_prompt),
            "max_tokens": max_tokens or self.settings.local_model_max_tokens,
            "temperature": temperature,
            "top_p": self.settings.local_model_top_p,
            "stream": False,
        }
        # 仅对局域网AI一体机禁用思考模式（Ollama 不支持该参数）
        if self.settings.model_provider != "ollama":
            payload["enable_thinking"] = False
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        return payload


def build_chat_messages(system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
    strict_system_prompt = f"{system_prompt}\n只输出一个 JSON 对象，不要输出解释。"
    return [
        {"role": "system", "content": strict_system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_completion_prompt(system_prompt: str, user_prompt: str) -> str:
    return f"""/no_think
系统指令：
{system_prompt}
禁止输出 <think>、推理过程、Markdown、解释、注释或任何非 JSON 内容。完成 JSON 后立刻停止。

用户任务：
{user_prompt}

请直接输出一个满足要求的 JSON 对象，不要输出 Markdown、解释、注释或推理过程。
JSON：
""".strip()


def _extract_completion_text(data: dict[str, Any]) -> str:
    choice = data["choices"][0]
    candidates: list[Any] = []

    message = choice.get("message")
    if isinstance(message, dict):
        candidates.append(message.get("content"))
        candidates.append(message.get("reasoning_content"))

    candidates.append(choice.get("text"))
    candidates.append(choice.get("content"))

    verbose = data.get("__verbose")
    if isinstance(verbose, dict):
        candidates.append(verbose.get("content"))

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate

    if any(isinstance(candidate, str) for candidate in candidates):
        return ""

    raise KeyError("choices[0].text")


def _extract_provider_error(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text[:500]

    error = data.get("error")
    if isinstance(error, dict):
        return str(error.get("message") or error.get("code") or data)
    return str(data)[:500]
