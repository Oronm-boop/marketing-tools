import logging

from pydantic import TypeAdapter, ValidationError

from .config import Settings
from .json_utils import JSONExtractionError, extract_json_payload
from .knowledge_base import KnowledgeBaseClient, KnowledgeBaseServiceError
from .local_model_client import LocalModelClient, LocalModelClientError, build_chat_messages
from .prompts import (
    SYSTEM_PROMPT,
    build_copywriting_user_prompt,
    build_publish_image_prompts_user_prompt,
    build_seo_user_prompt,
)
from .qwen_client import QwenClient, QwenClientError
from .schemas import (
    CopywritingItem,
    CopywritingRequest,
    CopywritingResponse,
    KnowledgeBaseReference,
    PublishImagePromptItem,
    PublishImagePromptRequest,
    PublishImagePromptResponse,
    SeoKeywordItem,
    SeoKeywordRequest,
    SeoKeywordResponse,
)
from .web_search import (
    TavilySearchClient,
    WebSearchError,
    build_copywriting_search_query,
    build_seo_search_query,
    format_web_context,
)


logger = logging.getLogger(__name__)

MAX_RAW_PREVIEW = 2000


class GenerationServiceError(RuntimeError):
    pass


class GenerationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = settings.model_provider
        if self.provider == "bailian":
            self.client = QwenClient(settings)
        else:
            self.client = LocalModelClient(settings)
        self.search_client = TavilySearchClient(settings)
        self.knowledge_base_client = KnowledgeBaseClient(settings)

    @property
    def model_name(self) -> str:
        """当前生效的模型名称，用于返回给前端展示。"""
        if self.provider == "bailian":
            return self.settings.qwen_model
        if self.provider == "ollama":
            return self.settings.ollama_model
        return self.settings.local_model_name

    async def generate_seo_keywords(self, payload: SeoKeywordRequest) -> SeoKeywordResponse:
        query = build_seo_search_query(payload)
        web_context = await self._search_web_context(query)
        knowledge_context = await self._retrieve_knowledge_context(payload.knowledge_base, query)
        content = await self._call_model(
            build_seo_user_prompt(payload, web_context, knowledge_context),
            temperature=0.6,
            max_tokens=2048,
        )
        raw_items = _extract_items(content, label="SEO 关键词")

        try:
            items = TypeAdapter(list[SeoKeywordItem]).validate_python(raw_items)
        except ValidationError as exc:
            raise GenerationServiceError(f"SEO 关键词 JSON 字段校验失败：{exc}") from exc

        return SeoKeywordResponse(items=items[: payload.keyword_count], model=self.model_name)

    async def generate_copywriting(self, payload: CopywritingRequest) -> CopywritingResponse:
        target_count = max(payload.article_count, len(payload.platform_styles))
        allowed_platforms = set(payload.platform_styles)
        query = build_copywriting_search_query(payload)
        web_context = await self._search_web_context(query)
        knowledge_context = await self._retrieve_knowledge_context(payload.knowledge_base, query)
        content = await self._call_model(
            build_copywriting_user_prompt(payload, web_context, knowledge_context),
            temperature=0.5,
            max_tokens=min(12000, max(2048, 2048 + target_count * 1600)),
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

        return CopywritingResponse(items=items[:target_count], model=self.model_name)

    async def generate_publish_image_prompts(
        self,
        payload: PublishImagePromptRequest,
    ) -> PublishImagePromptResponse:
        content = await self._call_model(
            build_publish_image_prompts_user_prompt(payload),
            temperature=0.45,
            max_tokens=4096,
        )
        raw_items = _extract_items(content, label="发布配图描述词")

        try:
            items = TypeAdapter(list[PublishImagePromptItem]).validate_python(raw_items)
        except ValidationError as exc:
            raise GenerationServiceError(f"发布配图描述词 JSON 字段校验失败：{exc}") from exc

        if len(items) < 3:
            raise GenerationServiceError(f"发布配图描述词数量不足：期望 3 条，实际 {len(items)} 条")

        return PublishImagePromptResponse(items=items[:3], model=self.model_name)

    async def _search_web_context(self, query: str) -> str:
        try:
            results = await self.search_client.search(query)
        except WebSearchError as exc:
            raise GenerationServiceError(str(exc)) from exc
        return format_web_context(query, results)

    async def _retrieve_knowledge_context(
        self,
        knowledge_base: KnowledgeBaseReference | None,
        query: str,
    ) -> str:
        if knowledge_base is None:
            return ""
        try:
            return await self.knowledge_base_client.retrieve_context(knowledge_base, query)
        except KnowledgeBaseServiceError as exc:
            raise GenerationServiceError(str(exc)) from exc

    async def _call_model(
        self,
        user_prompt: str,
        temperature: float,
        max_tokens: int | None = None,
    ) -> str:
        if self.provider == "bailian":
            return await self._call_bailian(user_prompt, temperature, max_tokens)
        return await self._call_local(user_prompt, temperature, max_tokens)

    async def _call_bailian(
        self,
        user_prompt: str,
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        messages = build_chat_messages(SYSTEM_PROMPT, user_prompt)
        try:
            return await self.client.chat_json(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except QwenClientError as exc:
            raise GenerationServiceError(str(exc)) from exc

    async def _call_local(
        self,
        user_prompt: str,
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        try:
            return await self.client.complete_json(
                SYSTEM_PROMPT,
                user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                api_mode="chat",
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
