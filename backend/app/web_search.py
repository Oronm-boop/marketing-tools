from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import httpx

from .config import HARDCODED_TAVILY_API_KEY, Settings
from .copywriting_intent import has_recommendation_intent
from .schemas import CopywritingRequest, SeoKeywordRequest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEARCH_LOG_PATH = PROJECT_ROOT / "travily-results.log"


class WebSearchError(RuntimeError):
    pass


@dataclass(frozen=True)
class WebSearchResult:
    title: str
    url: str
    content: str
    published_date: str = ""


class TavilySearchClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def search(self, query: str) -> list[WebSearchResult]:
        api_key = self._api_key
        if not api_key:
            raise WebSearchError("缺少 TAVILY_API_KEY，请在后端环境变量或后端 .env 中配置 Tavily API Key")

        endpoint = self.settings.tavily_base_url.rstrip("/") + "/search"
        payload: dict[str, Any] = {
            "query": query,
            "search_depth": self.settings.tavily_search_depth,
            "max_results": self.settings.tavily_max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.tavily_timeout_seconds) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise WebSearchError(f"Tavily 搜索请求超时，当前超时时间 {self.settings.tavily_timeout_seconds} 秒") from exc
        except httpx.HTTPStatusError as exc:
            message = _extract_search_error(exc.response)
            raise WebSearchError(f"Tavily 搜索请求失败：{message}") from exc
        except httpx.ConnectError as exc:
            message = _format_network_error(exc, endpoint)
            raise WebSearchError(f"Tavily 搜索网络请求失败：{message}") from exc
        except httpx.HTTPError as exc:
            message = _format_network_error(exc, endpoint)
            raise WebSearchError(f"Tavily 搜索网络请求失败：{message}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise WebSearchError("Tavily 搜索返回了非 JSON 内容") from exc

        results = data.get("results")
        if not isinstance(results, list) or not results:
            raise WebSearchError("Tavily 搜索没有返回可用结果")

        normalized = [_normalize_result(item) for item in results if isinstance(item, dict)]
        normalized = [item for item in normalized if item.content]
        if not normalized:
            raise WebSearchError("Tavily 搜索结果缺少可用于生成的摘要内容")

        _append_search_log(query, normalized)
        return normalized

    @property
    def _api_key(self) -> str:
        return HARDCODED_TAVILY_API_KEY.strip()


def build_seo_search_query(payload: SeoKeywordRequest) -> str:
    engines = " ".join(payload.search_engines)
    return (
        f"{payload.business_description} {payload.product_features} "
        f"{engines} 用户搜索需求 选购指南 常见问题 竞品对比 热门问题 {date.today().year}"
    )


def build_copywriting_search_query(payload: CopywritingRequest) -> str:
    platforms = " ".join(payload.platform_styles)
    product_context = " ".join(
        part for part in [payload.business_description, payload.product_features] if part
    )
    if has_recommendation_intent(
        payload.keyword,
        payload.business_description,
        payload.product_features,
    ):
        intent_terms = "高性价比推荐 具体型号 品牌 价格 参数 核心卖点 优缺点 适合人群 横向对比 选购清单 购买建议"
    else:
        intent_terms = "最新趋势 用户痛点 热门话题 购买决策 真实体验 口碑对比 竞品卖点 用户评价"
    return (
        f"{payload.keyword} {product_context} {platforms} {intent_terms} {date.today().year}"
    )


def format_web_context(query: str, results: list[WebSearchResult]) -> str:
    sections = [f"联网搜索查询：{query}", "联网搜索结果："]
    for index, item in enumerate(results, start=1):
        published = f"\n发布时间：{item.published_date}" if item.published_date else ""
        sections.append(
            "\n".join(
                [
                    f"{index}. 标题：{item.title}",
                    f"来源：{item.url}",
                    f"摘要：{_trim_text(item.content, 600)}{published}",
                ]
            )
        )
    return "\n\n".join(sections)


def _normalize_result(item: dict[str, Any]) -> WebSearchResult:
    return WebSearchResult(
        title=_trim_text(str(item.get("title") or "未命名来源"), 120),
        url=str(item.get("url") or "").strip(),
        content=_trim_text(str(item.get("content") or ""), 900),
        published_date=str(item.get("published_date") or "").strip(),
    )


def _append_search_log(query: str, results: list[WebSearchResult]) -> None:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    lines = [
        "=" * 80,
        f"时间：{timestamp}",
        f"查询：{query}",
        f"结果数量：{len(results)}",
        "",
    ]

    for index, item in enumerate(results, start=1):
        lines.extend(
            [
                f"{index}. 标题：{item.title}",
                f"来源：{item.url}",
                f"摘要：{_trim_text(item.content, 800)}",
            ]
        )
        if item.published_date:
            lines.append(f"发布时间：{item.published_date}")
        lines.append("")

    try:
        if not SEARCH_LOG_PATH.exists():
            SEARCH_LOG_PATH.write_text("Tavily 搜索结果日志\n", encoding="utf-8")
        with SEARCH_LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write("\n".join(lines).rstrip() + "\n")
    except OSError as exc:
        raise WebSearchError(f"写入 Tavily 搜索日志失败：{exc}") from exc


def _trim_text(value: str, limit: int) -> str:
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def _extract_search_error(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text[:500]

    detail = data.get("detail")
    if detail:
        return str(detail)[:500]

    error = data.get("error")
    if isinstance(error, dict):
        return str(error.get("message") or error.get("code") or data)[:500]
    if error:
        return str(error)[:500]
    return str(data)[:500]


def _format_network_error(exc: httpx.HTTPError, endpoint: str) -> str:
    detail = str(exc).strip()
    if detail:
        return detail

    return (
        f"无法连接到 {endpoint}，请检查当前网络、代理/VPN 或 DNS "
        "是否允许访问 api.tavily.com"
    )
