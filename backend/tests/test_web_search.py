from app.prompts import build_copywriting_user_prompt, build_seo_user_prompt
from app.schemas import CopywritingRequest, SeoKeywordRequest
from app.web_search import WebSearchResult, format_web_context


def test_format_web_context_contains_query_and_sources():
    context = format_web_context(
        "智能手表 SEO 关键词",
        [
            WebSearchResult(
                title="智能手表选购指南",
                url="https://example.com/watch",
                content="心率监测、GPS 和续航是用户最常比较的维度。",
                published_date="2026-06-01",
            )
        ],
    )

    assert "联网搜索查询：智能手表 SEO 关键词" in context
    assert "标题：智能手表选购指南" in context
    assert "来源：https://example.com/watch" in context
    assert "发布时间：2026-06-01" in context


def test_seo_prompt_includes_web_context():
    prompt = build_seo_user_prompt(
        SeoKeywordRequest(
            business_description="智能手表",
            product_features="支持心率监测和 GPS",
            keyword_count=3,
            search_engines=["百度"],
        ),
        "真实用户常搜索续航、运动记录和防水。",
    )

    assert "联网搜索上下文（来自 Tavily）" in prompt
    assert "真实用户常搜索续航、运动记录和防水。" in prompt


def test_copywriting_prompt_includes_web_context():
    prompt = build_copywriting_user_prompt(
        CopywritingRequest(
            keyword="智能手表推荐",
            keyword_repeat_count=1,
            article_count=1,
            platform_styles=["小红书"],
        ),
        "近期内容讨论集中在健康监测和轻量化佩戴。",
    )

    assert "联网搜索上下文（来自 Tavily）" in prompt
    assert "近期内容讨论集中在健康监测和轻量化佩戴。" in prompt


def test_copywriting_prompt_defines_xiaohongshu_title_counting_rule():
    prompt = build_copywriting_user_prompt(
        CopywritingRequest(
            keyword="AI营销工具",
            keyword_repeat_count=1,
            article_count=1,
            platform_styles=["小红书"],
        ),
        "真实用户关注标题完整展示。",
    )

    assert "小红书标题硬性规则" in prompt
    assert "半角英文字母/数字/空格/符号每2个算1个字符" in prompt
    assert "理想长度是16-18字符，绝对不能超过20字符" in prompt
    assert "输出前必须自检每个小红书 title" in prompt
