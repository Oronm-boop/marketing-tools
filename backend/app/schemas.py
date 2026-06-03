from typing import Annotated, Any

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


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

    model_config = ConfigDict(populate_by_name=True)

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


class CopywritingItem(BaseModel):
    title: str = ""
    platform: str = ""
    angle: str = ""
    content: NonEmptyString
    actual_keyword_count: int = 0


class CopywritingResponse(BaseModel):
    items: list[CopywritingItem]
    model: str


class ProviderErrorResponse(BaseModel):
    detail: str


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

