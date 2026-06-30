from app.prompts import build_copywriting_user_prompt, build_seo_user_prompt
from app.schemas import CopywritingRequest, SeoKeywordRequest
from app.web_search import WebSearchResult, build_copywriting_search_query, format_web_context


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


def test_seo_prompt_includes_knowledge_context():
    prompt = build_seo_user_prompt(
        SeoKeywordRequest(
            business_description="智能手表",
            product_features="支持心率监测和 GPS",
            keyword_count=3,
            search_engines=["百度"],
        ),
        "真实用户常搜索续航、运动记录和防水。",
        "知识库：产品文档库\n核心卖点：企业级运动健康数据。",
    )

    assert "知识库上下文（来自用户选择的知识库）" in prompt
    assert "企业级运动健康数据" in prompt


def test_copywriting_prompt_includes_web_context():
    prompt = build_copywriting_user_prompt(
        CopywritingRequest(
            business_description="高端智能家居设备厂商",
            product_features="支持语音控制，兼容米家和苹果 HomeKit",
            keyword="智能手表推荐",
            keyword_repeat_count=1,
            article_count=1,
            platform_styles=["小红书"],
            copy_length="中",
        ),
        "近期内容讨论集中在健康监测和轻量化佩戴。",
    )

    assert "联网搜索上下文（来自 Tavily）" in prompt
    assert "近期内容讨论集中在健康监测和轻量化佩戴。" in prompt
    assert "我是做什么的：高端智能家居设备厂商" in prompt
    assert "产品特点：支持语音控制，兼容米家和苹果 HomeKit" in prompt
    assert "必须优先围绕用户业务和产品特点展开" in prompt


def test_copywriting_prompt_includes_knowledge_context():
    prompt = build_copywriting_user_prompt(
        CopywritingRequest(
            business_description="高端智能家居设备厂商",
            product_features="支持语音控制，兼容米家和苹果 HomeKit",
            keyword="智能家居推荐",
            keyword_repeat_count=1,
            article_count=1,
            platform_styles=["小红书"],
            copy_length="中",
        ),
        "近期内容讨论集中在全屋智能。",
        "知识库：产品文档库\n内部资料：安装只需要15分钟。",
    )

    assert "知识库上下文（来自用户选择的知识库）" in prompt
    assert "安装只需要15分钟" in prompt
    assert "不得和知识库资料冲突" in prompt


def test_copywriting_search_query_includes_product_context():
    query = build_copywriting_search_query(
        CopywritingRequest(
            business_description="高端智能家居设备厂商",
            product_features="支持语音控制，兼容米家和苹果 HomeKit",
            keyword="智能家居推荐",
            keyword_repeat_count=1,
            article_count=1,
            platform_styles=["小红书"],
            copy_length="中",
        )
    )

    assert "智能家居推荐" in query
    assert "高端智能家居设备厂商" in query
    assert "支持语音控制，兼容米家和苹果 HomeKit" in query
    assert "小红书" in query


def test_copywriting_search_query_focuses_on_product_recommendation_evidence():
    query = build_copywriting_search_query(
        CopywritingRequest(
            business_description="智能手表",
            product_features="语音操控，记录心率和运动记录",
            keyword="2026年高性价比智能手表",
            keyword_repeat_count=1,
            article_count=1,
            platform_styles=["小红书"],
            copy_length="中",
        )
    )

    assert "具体型号" in query
    assert "品牌" in query
    assert "价格" in query
    assert "横向对比" in query
    assert "选购清单" in query


def test_copywriting_prompt_requires_specific_products_for_recommendation_intent():
    prompt = build_copywriting_user_prompt(
        CopywritingRequest(
            business_description="智能手表",
            product_features="语音操控，记录心率和运动记录",
            keyword="2026年高性价比智能手表",
            keyword_repeat_count=1,
            article_count=1,
            platform_styles=["小红书"],
            copy_length="中",
        ),
        "荣耀手表 6Plus 国补后 1019.15 元起，支持 AI 跑步教练；华为 WATCH GT5 主打轻薄商务和鸿蒙生态；Apple Watch SE 适合 iPhone 用户。",
    )

    assert "当前关键词已判定为推荐/选购意图：是" in prompt
    assert "每篇 content 必须包含一个“具体推荐”或“推荐清单”段落" in prompt
    assert "每篇 content 必须从联网搜索上下文中提到至少 2 款具体产品" in prompt
    assert "严禁用“这款表”“这款产品”“热门款”“旗舰体验”等词替代具体产品名" in prompt
    assert "正文前半部分就要出现具体型号" in prompt


def test_copywriting_prompt_defines_xiaohongshu_title_counting_rule():
    prompt = build_copywriting_user_prompt(
        CopywritingRequest(
            keyword="AI营销工具",
            keyword_repeat_count=1,
            article_count=1,
            platform_styles=["小红书"],
            copy_length="短",
        ),
        "真实用户关注标题完整展示。",
    )

    assert "小红书标题硬性规则" in prompt
    assert "半角英文字母/数字/空格/符号每2个算1个字符" in prompt
    assert "理想长度是16-18字符，绝对不能超过20字符" in prompt
    assert "输出前必须自检每个小红书 title" in prompt


def test_copywriting_prompt_includes_xiaohongshu_traffic_copy_rules():
    prompt = build_copywriting_user_prompt(
        CopywritingRequest(
            keyword="AI营销工具",
            keyword_repeat_count=1,
            article_count=1,
            platform_styles=["小红书"],
            copy_length="短",
        ),
        "真实用户关注标题钩子和内容转化。",
    )

    assert "小红书流量文案策略" in prompt
    assert "轻度对立站队、痛点警醒、认知反转、反差猎奇、真实叙事" in prompt
    assert "不要挑动性别、地域、年龄、贫富、职业等群体攻击" in prompt
    assert "正文第一句必须直接抛出冲突、痛点、反差或结论" in prompt


def test_copywriting_prompt_includes_xiaohongshu_symbol_rules():
    prompt = build_copywriting_user_prompt(
        CopywritingRequest(
            keyword="AI营销工具",
            keyword_repeat_count=1,
            article_count=1,
            platform_styles=["小红书"],
            copy_length="短",
        ),
        "真实用户关注清单结构和重点提示。",
    )

    assert "小红书符号与排版硬性规则" in prompt
    assert "必须同时包含“序号/列表符号”和“标题/强调符号”两类元素" in prompt
    assert "1️⃣ 2️⃣ 3️⃣、① ② ③、▪️ ▫️ ◾、⭐ ✨" in prompt
    assert "‼️ ❗ ⚡、☁️、⚠️ ➡️ ✔️ ❌" in prompt
    assert "content 第一行必须以一个标题/强调符号开头" in prompt
    assert "content 正文中必须至少出现一处连续列表结构" in prompt
    assert "不要整段堆满 emoji" in prompt
    assert "不能为了加符号导致 title 超过20字符" in prompt
    assert "不满足时不要输出该 item，先重写" in prompt


def test_copywriting_prompt_uses_frontend_copy_length():
    prompt = build_copywriting_user_prompt(
        CopywritingRequest(
            keyword="智能手表推荐",
            keyword_repeat_count=1,
            article_count=1,
            platform_styles=["微信公众号", "知乎", "微博", "视频号"],
            copy_length="长",
        ),
        "真实用户关注续航。",
    )

    assert "用户在前端选择的文案长度：长" in prompt
    assert "短=100-300字，中=300-500字，长=500-800字" in prompt
    assert "平台风格要求" in prompt
    assert "平台风格和长度要求" not in prompt
    assert "2000-3000" not in prompt
    assert "万字" not in prompt
    assert "140字" not in prompt
    assert "30秒-1分钟" not in prompt


def test_copywriting_request_accepts_copy_length_alias():
    payload = CopywritingRequest.model_validate(
        {
            "keyword": "智能手表推荐",
            "keyword_repeat_count": 1,
            "article_count": 1,
            "platform_styles": ["小红书"],
            "copyLength": "短",
        }
    )

    assert payload.copy_length == "短"
