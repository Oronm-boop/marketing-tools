from .schemas import CopywritingRequest, SeoKeywordRequest


SYSTEM_PROMPT = (
    "你是一个中文增长营销与SEO专家，擅长根据业务信息生成可直接用于运营的结构化内容。"
    "只输出严格 JSON，不输出 Markdown、解释、注释或推理过程。"
)


def build_seo_user_prompt(payload: SeoKeywordRequest) -> str:
    engines = "、".join(payload.search_engines)
    return f"""
用户业务：{payload.business_description}
产品特点：{payload.product_features}

请生成 {payload.keyword_count} 个关键词，覆盖短尾词、长尾词、问题词。
针对搜索引擎：{engines} 的搜索习惯优化。

输出严格 JSON 对象，且只包含 items 字段。
items 是数组，每个对象必须包含：
- keyword：生成的真实关键词
- search_volume_est：预估搜索量，例如 100-500 或 1k-3k
- difficulty：低、中、高 三选一

要求：
1. items 数量必须等于 {payload.keyword_count}。
2. keyword 不要重复，不要为空。
3. search_volume_est 使用合理估算区间。
4. difficulty 使用中文：低、中、高。
5. 不要输出字段说明，不要输出示例值。
""".strip()


def build_copywriting_user_prompt(payload: CopywritingRequest) -> str:
    platforms = "、".join(payload.platform_styles)
    return f"""
为关键词“{payload.keyword}”撰写社媒文案，关键词需在每篇正文中自然出现 {payload.keyword_repeat_count} 次。
平台风格参考：{platforms}。
每篇字数 150-200 个中文字符。
生成 {payload.article_count} 篇不同切入点的文案。

输出严格 JSON 对象，且只包含 items 字段。
items 是数组，每个对象必须包含：
- title：真实文案标题
- platform：从用户给定的平台风格中选择一个
- angle：真实切入点
- content：真实正文

要求：
1. items 数量必须等于 {payload.article_count}。
2. 每篇 angle 不同，避免套话和重复表达。
3. content 只写正文，不要包含编号、Markdown 或额外说明。
4. platform 从用户给定的平台风格中选择。
5. 不要输出“文案标题”“平台风格”“切入点”“正文”等占位词。
""".strip()
