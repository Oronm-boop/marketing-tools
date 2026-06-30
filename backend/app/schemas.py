from typing import Annotated, Any, Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
CopyLength = Literal["短", "中", "长"]


class KnowledgeBaseReference(BaseModel):
    id: NonEmptyString
    name: str = ""

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: Any) -> str:
        return str(value or "").strip()


class SeoKeywordRequest(BaseModel):
    business_description: NonEmptyString = Field(
        validation_alias=AliasChoices("business_description", "business", "业务描述")
    )
    product_features: NonEmptyString = Field(
        validation_alias=AliasChoices("product_features", "features", "特点", "产品特点")
    )
    keyword_count: int = Field(
        default=10,
        ge=1,
        le=100,
        validation_alias=AliasChoices("keyword_count", "keywordCount", "数量"),
    )
    search_engines: list[str] = Field(
        default_factory=lambda: ["百度", "360搜索", "必应"],
        validation_alias=AliasChoices("search_engines", "searchEngines", "搜索引擎"),
    )
    knowledge_base: KnowledgeBaseReference | None = Field(
        default=None,
        validation_alias=AliasChoices("knowledge_base", "knowledgeBase"),
    )

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("search_engines")
    @classmethod
    def validate_search_engines(cls, value: list[str]) -> list[str]:
        normalized = _clean_string_list(value)
        if not normalized:
            raise ValueError("search_engines 至少选择一个搜索引擎")
        if len(normalized) > 6:
            raise ValueError("search_engines 最多支持 6 个搜索引擎")
        return normalized


class SeoKeywordItem(BaseModel):
    keyword: NonEmptyString
    search_volume_est: str = "未知"
    difficulty: str = "中"

    @field_validator("search_volume_est", "difficulty", mode="before")
    @classmethod
    def stringify_value(cls, value: Any) -> str:
        if value is None:
            return "未知"
        return str(value)


class SeoKeywordResponse(BaseModel):
    items: list[SeoKeywordItem]
    model: str


class CopywritingRequest(BaseModel):
    business_description: str = Field(
        default="",
        validation_alias=AliasChoices("business_description", "business", "业务描述", "我是做什么的"),
    )
    product_features: str = Field(
        default="",
        validation_alias=AliasChoices("product_features", "features", "特点", "产品特点"),
    )
    keyword: NonEmptyString
    keyword_repeat_count: int = Field(
        default=1,
        ge=0,
        le=10,
        validation_alias=AliasChoices("keyword_repeat_count", "keywordRepeatCount", "keywordOccurrences", "次数"),
    )
    article_count: int = Field(
        default=3,
        ge=1,
        le=20,
        validation_alias=AliasChoices("article_count", "articleCount", "篇数"),
    )
    platform_styles: list[str] = Field(
        default_factory=lambda: ["小红书"],
        validation_alias=AliasChoices("platform_styles", "platformStyles", "platform_style", "platforms", "platform"),
    )
    copy_length: CopyLength = Field(
        default="中",
        validation_alias=AliasChoices("copy_length", "copyLength", "length", "文案长度"),
    )
    knowledge_base: KnowledgeBaseReference | None = Field(
        default=None,
        validation_alias=AliasChoices("knowledge_base", "knowledgeBase"),
    )

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("business_description", "product_features", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> str:
        return str(value or "").strip()

    @field_validator("platform_styles", mode="before")
    @classmethod
    def normalize_platform_styles(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            value = [value]
        normalized = _clean_string_list(value)
        if not normalized:
            raise ValueError("platform_styles 至少选择一个平台风格")
        if len(normalized) > 8:
            raise ValueError("platform_styles 最多支持 8 个平台风格")
        return normalized

    @field_validator("copy_length", mode="before")
    @classmethod
    def normalize_copy_length(cls, value: Any) -> str:
        text = str(value or "").strip()
        length_aliases = {
            "短": "短",
            "中": "中",
            "长": "长",
        }
        if text not in length_aliases:
            raise ValueError("copy_length 必须为 短、中、长")
        return length_aliases[text]


class CopywritingItem(BaseModel):
    title: str = ""
    platform: str = ""
    angle: str = ""
    content: NonEmptyString
    actual_keyword_count: int = 0


class CopywritingResponse(BaseModel):
    items: list[CopywritingItem]
    model: str


class PublishImagePromptRequest(BaseModel):
    title: NonEmptyString
    content: NonEmptyString
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        return _clean_string_list(value)[:10]


class PublishImagePromptItem(BaseModel):
    title: str = ""
    description: NonEmptyString
    keywords: list[str] = Field(default_factory=list)

    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, value: list[str]) -> list[str]:
        return _clean_string_list(value)[:8]


class PublishImagePromptResponse(BaseModel):
    items: list[PublishImagePromptItem]
    model: str


class ImageGenerationRequest(BaseModel):
    prompt: NonEmptyString
    width: int = Field(default=768, ge=256, le=4096)
    height: int = Field(default=1024, ge=256, le=4096)
    batch_size: int = Field(default=1, ge=1, le=4)


class ImageGenerationTaskResponse(BaseModel):
    prompt_id: NonEmptyString
    status: Literal["queued"] = "queued"


class GeneratedImageFile(BaseModel):
    filename: NonEmptyString
    subfolder: str = ""
    type: str = "output"
    url: str = ""


class ImageGenerationStatusResponse(BaseModel):
    prompt_id: NonEmptyString
    status: Literal["pending", "running", "success", "failed"]
    message: str = ""
    image: GeneratedImageFile | None = None


class KnowledgeBaseDocument(BaseModel):
    id: NonEmptyString
    name: NonEmptyString
    size: int = Field(default=0, ge=0)
    uploadedAt: int = Field(default=0, ge=0)


class KnowledgeBase(BaseModel):
    id: NonEmptyString
    name: NonEmptyString
    documentCount: int = Field(default=0, ge=0)
    updatedAt: str = ""
    documents: list[KnowledgeBaseDocument] = Field(default_factory=list)


class KnowledgeBaseCreateRequest(BaseModel):
    name: NonEmptyString = Field(
        validation_alias=AliasChoices("name", "collection_name", "collectionName")
    )

    model_config = ConfigDict(populate_by_name=True)


class KnowledgeBaseDocumentsResponse(BaseModel):
    documents: list[KnowledgeBaseDocument]


class ProviderErrorResponse(BaseModel):
    detail: str


class ModelSettingsRead(BaseModel):
    """返回给前端的当前模型配置（API Key 脱敏显示）。"""

    provider: str

    local_model_base_url: str
    local_model_name: str

    ollama_base_url: str
    ollama_model: str

    qwen_api_key: str
    qwen_base_url: str
    qwen_model: str

    comfyui_base_url: str
    comfyui_video_base_url: str

    knowledge_base_url: str
    browser_automation_show_window: bool


class ModelSettingsWrite(BaseModel):
    """前端提交的模型配置更新请求。"""

    provider: str = Field(pattern=r"^(local|ollama|bailian)$")

    local_model_base_url: str | None = None
    local_model_name: str | None = None

    ollama_base_url: str | None = None
    ollama_model: str | None = None

    qwen_api_key: str | None = None
    qwen_base_url: str | None = None
    qwen_model: str | None = None

    comfyui_base_url: str | None = None
    comfyui_video_base_url: str | None = None

    knowledge_base_url: str | None = None
    browser_automation_show_window: bool | None = None


def _clean_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("字段必须是字符串数组")
    result: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item).strip()
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result

