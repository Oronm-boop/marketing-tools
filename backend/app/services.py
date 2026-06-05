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
        target_count = max(payload.article_count, len(payload.platform_styles))
        allowed_platforms = set(payload.platform_styles)
        content = await self._call_model(
            build_copywriting_user_prompt(payload),
            temperature=0.5,
            max_tokens=max(self.settings.local_model_max_tokens, min(12000, 2048 + target_count * 1600)),
            api_mode="chat",
        )
        raw_items = _extract_items(content, label="宣传文案")

        try:
            items = TypeAdapter(list[CopywritingItem]).validate_python(raw_items)
        except ValidationError as exc:
            raise GenerationServiceError(f"宣传文案 JSON 字段校验失败：{exc}") from exc

        items = [item for item in items if item.platform in allowed_platforms]
        for item in items:
            item.content = _ensure_exact_keyword_count(
                item.content,
                payload.keyword,
                payload.keyword_repeat_count,
            )
            item.actual_keyword_count = item.content.count(payload.keyword)

        if len(items) < target_count:
            logger.warning(
                "宣传文案返回数量不足：期望 %s 篇，过滤未选择平台后剩余 %s 篇，允许平台：%s",
                target_count,
                len(items),
                "、".join(payload.platform_styles),
            )

        return CopywritingResponse(items=items[:target_count], model=self.settings.local_model_name)

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


def _ensure_exact_keyword_count(content: str, keyword: str, target_count: int) -> str:
    if not keyword:
        return content

    current_count = content.count(keyword)
    if current_count > target_count:
        content = _replace_excess_keyword_occurrences(content, keyword, target_count)
    elif current_count < target_count:
        content = _append_missing_keyword_occurrences(content, keyword, target_count - current_count)

    final_count = content.count(keyword)
    if final_count > target_count:
        content = _replace_excess_keyword_occurrences(content, keyword, target_count)

    return content


def _replace_excess_keyword_occurrences(content: str, keyword: str, target_count: int) -> str:
    parts = content.split(keyword)
    if len(parts) == 1:
        return content

    result = [parts[0]]
    replacement = "这类内容"
    for index, part in enumerate(parts[1:], start=1):
        result.append(keyword if index <= target_count else replacement)
        result.append(part)
    return "".join(result)


def _append_missing_keyword_occurrences(content: str, keyword: str, missing_count: int) -> str:
    if missing_count <= 0:
        return content

    additions = [
        f"正在对比{keyword}的话，可以先收藏这篇。",
        f"想看更多{keyword}清单，评论区告诉我你的预算和使用场景。",
        f"#{keyword}",
    ]
    while len(additions) < missing_count:
        additions.append(f"{keyword}也是这篇内容的重点参考词。")

    suffix = "\n".join(additions[:missing_count])
    return f"{content.rstrip()}\n\n{suffix}"
