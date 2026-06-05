from .schemas import CopywritingRequest, SeoKeywordRequest


PLATFORM_STYLE_RULES = {
    "小红书": "小红书: 活泼、种草、生活化、有情绪价值，标题可使用emoji和符号,正文200-400字，多用短句、emoji、分隔线、清单感、真实体验感，正文避免‘家人们、谁懂啊、姐妹们’等强人群绑定或过度网感表达，末尾必须包含4-7 #标签",
    "微信公众号": "深度+人格化，像老朋友写信。开头金句钩子，正文逻辑缜密，适合2000-3000字深度阅读。排版讲究留白、引用、加粗，文末强引导关注/在看，可适当使用动图。",
    "知乎": "专业+盐选感，像领域专家开讲。回答需有'先说结论'、'分点论证'结构，强排版（目录/引用块/加粗），推崇万字长文深度，文末可放'防走失'引流钩子，反感夸张标题党。",
    "抖音": "爆点前置+快节奏，像3秒定生死的舞台。前3秒必须抛出痛点或冲突，话术密集、反转多，常用'别划走/你知道吗'，评论区强互动（神评论/楼中楼），字幕要大且重点变色。必须包含 4-8 个 #标签。",
    "快手": "老铁文化+真实接地，像邻里唠嗑。封面标题要吸睛但朴实，语言节奏快、喊麦式口播，信任感来自'真性情'人设，常用'双击666/老铁们'，剧情号强反转，注重私域引流。必须包含 4-8 个 #标签。",
    "视频号": "社交裂变+温情感，像朋友圈里的爆款视频。标题克制不夸张，内容强调正能量、知识、生活洞察，强依赖点赞推荐给好友，适合30秒-1分钟中视频，结尾引导点亮爱心/转发。必须包含 4-8 个 #标签。",
    "微博": "短平快+蹭热点，像大型吃瓜现场。140字碎片化表达，常用双#话题#引流、@熟人裂变，情绪要外放(怒赞/泪目/裂开)，娱乐八卦、社会热点发酵地，包容各种‘发疯文学’。必须包含 4-8 个 #标签。",
    "B站": "玩梗+真诚，像Z世代的兴趣部落。标题常用反差、玩梗，封面讲究'B站起标题学'，内容要么极致专业(硬核科普)，要么极致真诚(Vlog式陪伴)，弹幕文化是灵魂，严禁生硬营销。",
    "百度": "SEO+结构化，像给机器和老人看的说明书。标题精准匹配搜索词，正文首段必须出关键词，排版用H2/H3层级分明，少玩梗多平实描述，内容强调时效性(实时热点)和权威性。",
}



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
    platform_rules = "\n".join(_get_platform_rule(platform) for platform in payload.platform_styles)
    target_count = max(payload.article_count, len(payload.platform_styles))
    return f"""
你是一名资深 SEO 内容营销专家和新媒体文案策划。

请围绕 SEO 关键词“{payload.keyword}”，为以下平台生成可以直接发布的成品文案：
{platforms}

生成数量：{target_count} 篇。
平台覆盖规则：
- 先为用户给定的每个平台至少生成 1 篇。
- 如果生成数量多于平台数量，再为已给定平台补充不同切入点的文案。
- platform 字段必须从用户给定的平台名称中选择，并保持原文一致。
- 只允许生成以上已给定平台的文案；未勾选的平台一律不要生成。

关键词使用规则：
- 完整关键词“{payload.keyword}”必须在每篇 content 中精确出现 {payload.keyword_repeat_count} 次；前端会按完整字符串匹配统计次数。
- 如果次数为 0，则 content 中不要出现完整关键词“{payload.keyword}”。
- 不要生硬堆词，不要把关键词连续重复。

内容质量要求：
- 每篇必须是可直接发布的完整成品文案，不要写大纲、思路、示例、节选或占位文本。
- 每个平台的标题、正文长度、语气、结构、符号、标签数量必须明显不同，不能只改标题。
- content 必须包含完整正文、结尾引导和 #标签；结尾引导和标签也写在 content 里。
- 使用真实创作者口吻，避免 AI 味、模板感、空话和泛泛而谈。

平台风格和长度要求：
{platform_rules}

输出严格 JSON 对象，且只包含 items 字段。
items 是数组，每个对象必须包含：
- title：真实文案标题
- platform：从用户给定的平台风格中选择一个
- angle：真实切入点
- content：真实正文

要求：
1. items 数量必须等于 {target_count}。
2. 每篇 angle 不同，避免套话和重复表达。
3. content 只写可发布内容，不要包含“正文节选”“以下是”“示例”等说明性话术。
4. platform 从用户给定的平台风格中选择。
5. 不要输出“文案标题”“平台风格”“切入点”“正文”等占位词。
6. content 是 JSON 字符串；如果需要换行，请使用 \\n。
""".strip()


def _get_platform_rule(platform: str) -> str:
    return PLATFORM_STYLE_RULES.get(
        platform,
        f"{platform}：根据平台名称推断用户场景，只生成适合“{platform}”发布的成品文案，并包含标题感正文、结尾引导和 #标签。",
    )
