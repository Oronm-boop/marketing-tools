from .copywriting_intent import has_recommendation_intent
from .schemas import CopywritingRequest, PublishImagePromptRequest, SeoKeywordRequest


PLATFORM_STYLE_RULES = {
    "小红书": "小红书: 真实、有钩子、有反差、有情绪价值，像真人创作者在分享具体经历，而不是品牌通稿。title 字段必须按小红书后台规则计数：汉字、中文标点、#话题各算1个字符，半角英文字母/数字/空格/符号每2个算1个字符，emoji算2个字符。标题目标控制在16-18字符，绝对不能超过20字符；如果含英文品牌词或emoji，必须主动缩短中文部分。标题优先使用反差、悬念、认知刷新、具体数字或真实结果，例如“原来不是我不努力”“花小钱也能有质感”“用了3天才懂”。正文要有开场钩子、具体场景、个人观察、可执行建议和结尾互动，避免‘家人们、谁懂啊、姐妹们’等强人群绑定或过度网感表达，末尾必须包含4-7 #标签",
    "公众号": "深度+人格化，像老朋友写信。开头金句钩子，正文逻辑缜密，排版讲究留白、引用、加粗，文末强引导关注/在看，可适当使用动图。",
    "微信公众号": "深度+人格化，像老朋友写信。开头金句钩子，正文逻辑缜密，排版讲究留白、引用、加粗，文末强引导关注/在看，可适当使用动图。",
    "知乎": "专业+盐选感，像领域专家开讲。回答需有'先说结论'、'分点论证'结构，强排版（目录/引用块/加粗），强调深度论证，文末可放'防走失'引流钩子，反感夸张标题党。",
    "抖音": "爆点前置+快节奏，像3秒定生死的舞台。前3秒必须抛出痛点或冲突，话术密集、反转多，常用'别划走/你知道吗'，评论区强互动（神评论/楼中楼），字幕要大且重点变色。必须包含 4-8 个 #标签。",
    "快手": "老铁文化+真实接地，像邻里唠嗑。封面标题要吸睛但朴实，语言节奏快、喊麦式口播，信任感来自'真性情'人设，常用'双击666/老铁们'，剧情号强反转，注重私域引流。必须包含 4-8 个 #标签。",
    "视频号": "社交裂变+温情感，像朋友圈里的爆款视频。标题克制不夸张，内容强调正能量、知识、生活洞察，强依赖点赞推荐给好友，结尾引导点亮爱心/转发。必须包含 4-8 个 #标签。",
    "微博": "短平快+蹭热点，像大型吃瓜现场。碎片化表达，常用双#话题#引流、@熟人裂变，情绪要外放(怒赞/泪目/裂开)，娱乐八卦、社会热点发酵地，包容各种‘发疯文学’。必须包含 4-8 个 #标签。",
    "B站": "玩梗+真诚，像Z世代的兴趣部落。标题常用反差、玩梗，封面讲究'B站起标题学'，内容要么极致专业(硬核科普)，要么极致真诚(Vlog式陪伴)，弹幕文化是灵魂，严禁生硬营销。",
    "百度": "SEO+结构化，像给机器和老人看的说明书。标题精准匹配搜索词，正文首段必须出关键词，排版用H2/H3层级分明，少玩梗多平实描述，内容强调时效性(实时热点)和权威性。",
}



SYSTEM_PROMPT = (
    "你是一个中文增长营销与SEO专家，擅长根据业务信息生成可直接用于运营的结构化内容。"
    "只输出严格 JSON，不输出 Markdown、解释、注释或推理过程。"
)


XIAOHONGSHU_TRAFFIC_COPY_RULES = """
小红书流量文案策略（仅当 platform 是“小红书”时适用）：
- 不要写成官方宣传稿；要像真人创作者基于真实场景、真实困惑、真实试用后的分享。
- 每篇至少选择一种爆款切入：轻度对立站队、痛点警醒、认知反转、反差猎奇、真实叙事。
- 轻度对立站队：只制造观点分歧或选择分歧，例如“贵的不一定更好”“新手最该先放弃这个执念”；不要挑动性别、地域、年龄、贫富、职业等群体攻击。
- 痛点警醒：可以点出用户正在浪费时间、花冤枉钱、做无效努力，但必须给出具体解决办法；不要恐吓、羞辱或夸大后果。
- 认知反转：标题和开头要先打破一个常见误区，再给出可信理由，避免空喊“真相”“作弊系统”。
- 反差猎奇：用具体数字、预算、时间、前后变化制造好奇，例如“看着像花了1万，其实只改了3处”；正文必须兑现标题。
- 真实叙事：加入细节场景、第一人称观察、踩坑过程或决策瞬间，让内容有“人味”。
- 标题要口语化、短促、有画面感；正文第一句必须直接抛出冲突、痛点、反差或结论，不要铺垫背景。
- 互动引导要自然，不要用生硬营销口号。
""".strip()


XIAOHONGSHU_SYMBOL_COPY_RULES = """
小红书符号与排版硬性规则（仅当 platform 是“小红书”时适用）：
- 每篇小红书 content 必须同时包含“序号/列表符号”和“标题/强调符号”两类元素。
- 序号/列表符号用于步骤说明、清单罗列、避坑提示、对比总结或建议拆解，至少使用一种连续编号或项目符号：1️⃣ 2️⃣ 3️⃣、① ② ③、▪️ ▫️ ◾、⭐ ✨；也可使用 ✅ 📌 📝 等小红书常见清单符号。
- 标题/强调符号用于 title 前缀、段落小标题或重点内容提示，至少使用一种：‼️ ❗ ⚡、☁️、⚠️ ➡️ ✔️ ❌；也可使用 🔥 💡 🎯 🌟 💥 🧡 等小红书常见强调符号。
- 符号必须自然服务内容结构，不要整段堆满 emoji；每个段落最多 1-2 个重点符号，避免像符号清单。
- 如果 title 使用 emoji，必须遵守小红书标题计数规则并主动缩短中文部分，不能为了加符号导致 title 超过20字符。
- 输出 JSON 前必须逐篇自检：凡是 platform 为“小红书”的 item，如果 content 缺少上述任一类符号，必须先重写 content，再输出。
""".strip()


def build_seo_user_prompt(
    payload: SeoKeywordRequest,
    web_context: str,
    knowledge_context: str = "",
) -> str:
    engines = "、".join(payload.search_engines)
    knowledge_context_section = _build_knowledge_context_section(knowledge_context)
    return f"""
用户业务：{payload.business_description}
产品特点：{payload.product_features}

联网搜索上下文（来自 Tavily）：
{web_context}{knowledge_context_section}

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
5. 关键词要结合联网搜索上下文里的真实搜索意图、用户痛点、竞品表达和热门问题。
6. 如果提供了知识库上下文，优先结合其中的业务资料、产品资料和用户已有文档表述。
7. 不要编造具体来源中没有的确定性数据；search_volume_est 只能做区间估算。
8. 不要输出字段说明，不要输出示例值。
""".strip()


def build_copywriting_user_prompt(
    payload: CopywritingRequest,
    web_context: str,
    knowledge_context: str = "",
) -> str:
    platforms = "、".join(payload.platform_styles)
    platform_rules = "\n".join(_get_platform_rule(platform) for platform in payload.platform_styles)
    xiaohongshu_traffic_rules = (
        f"\n\n{XIAOHONGSHU_TRAFFIC_COPY_RULES}" if "小红书" in payload.platform_styles else ""
    )
    xiaohongshu_symbol_rules = (
        f"\n\n{XIAOHONGSHU_SYMBOL_COPY_RULES}" if "小红书" in payload.platform_styles else ""
    )
    target_count = max(payload.article_count, len(payload.platform_styles))
    business_description = payload.business_description or "未提供"
    product_features = payload.product_features or "未提供"
    recommendation_rules = _build_product_recommendation_rules(payload)
    knowledge_context_section = _build_knowledge_context_section(knowledge_context)
    return f"""
你是一名资深 SEO 内容营销专家和新媒体文案策划。

请围绕 SEO 关键词“{payload.keyword}”，为以下平台生成可以直接发布的成品文案：
{platforms}

用户业务与产品信息：
- 我是做什么的：{business_description}
- 产品特点：{product_features}

联网搜索上下文（来自 Tavily）：
{web_context}{knowledge_context_section}

{recommendation_rules}

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

文案长度选择：
- 用户在前端选择的文案长度：{payload.copy_length}。
- 按该选择决定正文详略：短=精炼直接，中=信息完整，长=充分展开。

小红书标题硬性规则：
- 如果 platform 是“小红书”，title 必须按小红书后台规则计数：汉字、中文标点、#话题各算1个字符，半角英文字母/数字/空格/符号每2个算1个字符，emoji算2个字符。
- 小红书 title 的理想长度是16-18字符，绝对不能超过20字符。
- 如果小红书 title 包含英文品牌词、数字或emoji，必须减少中文词数量，避免看起来短但后台计数超限。
- 小红书 title 不要放 #话题，#标签只放在 content 末尾。
- 输出前必须自检每个小红书 title 的后台计数字符数；超过20字符就重写短标题。

内容质量要求：
- 每篇必须是可直接发布的完整成品文案，不要写大纲、思路、示例、节选或占位文本。
- 必须优先围绕用户业务和产品特点展开，把产品卖点、目标用户、使用场景写具体；不要只基于关键词写泛行业套话。
- 如果提供了知识库上下文，必须优先吸收其中的产品事实、业务素材、已有资料和专有名词；不得和知识库资料冲突。
- 如果用户业务或产品特点为"未提供"，不要自行编造搜索结果中没有的品牌、功能、价格、销量、资质或承诺。
- 当关键词具有推荐、选购、对比、性价比、榜单、清单等意图时，必须从联网搜索上下文中提取并引用具体的产品型号、品牌名称、关键参数和价格信息，自然融入文案正文；不要泛泛而谈只写品类，要让读者看到具体的产品推荐。
- 如果搜索上下文提供了多个产品，推荐/选购类文案至少要具体提及 2-3 款产品，包括型号名称和核心卖点差异。
- 不要因为联网了而刻意强调当前的年份。
- 每个平台的标题、语气、结构、符号、标签数量必须明显不同，不能只改标题。
- content 必须包含完整正文、结尾引导和 #标签。
- 使用真实创作者口吻，避免 AI 味、模板感、空话和泛泛而谈。
- 引用联网搜索上下文中的真实产品、趋势、用户痛点和竞品信息时，必须忠于原文数据；不要编造搜索上下文没有支持的具体新闻、价格、销量或排名。
- 不允许编造互联网上不存在的产品；但搜索结果中已有的产品必须积极引用。
- title、angle、content 字段值中不要使用英文双引号 "；需要引用时只使用中文引号「」或单引号，避免破坏 JSON。

平台风格要求：
{platform_rules}{xiaohongshu_traffic_rules}{xiaohongshu_symbol_rules}

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
7. JSON 字符串内不得出现未转义的英文双引号。
8. 如果 platform 是“小红书”，content 必须严格满足“小红书符号与排版硬性规则”：content 第一行必须以一个标题/强调符号开头，content 正文中必须至少出现一处连续列表结构；不满足时不要输出该 item，先重写。
""".strip()


def _build_product_recommendation_rules(payload: CopywritingRequest) -> str:
    if not has_recommendation_intent(
        payload.keyword,
        payload.business_description,
        payload.product_features,
    ):
        return """
选品推荐硬性规则（当前关键词已判定为推荐/选购意图：否）：
- 当前主题不是推荐/选购类时，优先写用户业务与产品特点；只有在对比、趋势或用户决策说明时才引用联网搜索上下文里的竞品信息。
""".strip()

    return """
选品推荐硬性规则（当前关键词已判定为推荐/选购意图：是）：
- 每篇 content 必须包含一个“具体推荐”或“推荐清单”段落，不能只写体验场景、功能感受或泛行业种草。
- 每篇 content 必须从联网搜索上下文中提到至少 2 款具体产品；如果上下文中可用产品达到 3 款，优先写 3 款。
- 每款产品必须写清：品牌/型号 + 一个核心卖点或参数 + 价格、预算、适合人群中的至少一项；没有价格就写搜索上下文支持的参数，不要补造价格。
- 标题、开头和 angle 必须体现推荐、选购或对比，不要只围绕“语音操控”“运动记录”等单一功能做泛泛种草。
- 严禁用“这款表”“这款产品”“热门款”“旗舰体验”等词替代具体产品名；第一次出现必须写完整型号。
- 正文前半部分就要出现具体型号，不允许只在结尾附带一句推荐。
""".strip()


def build_publish_image_prompts_user_prompt(payload: PublishImagePromptRequest) -> str:
    tags = "、".join(payload.tags) if payload.tags else "无"
    return f"""
你是一名小红书图文配图策划和文生图提示词工程师。

请根据下面这篇已经生成好的小红书文案，为它规划 3 张配图，并为每张图生成一段可直接给 ComfyUI 使用的中文文生图描述词。

文章标题：
{payload.title}

文章标签：
{tags}

文章正文：
{payload.content}

生成范式：
- 先在心里把文章拆成 3 个连续信息段：开头核心观点 / 中段解释或场景 / 结尾结论或行动建议。
- 输出的 3 张图必须分别对应这 3 个信息段，不能三张都表达同一个画面。
- 首张图必须能单独承载整篇内容的核心卖点，确保只生成 1 张图也可以直接发布。
- 三张图整体风格必须统一。
- 每段 description 必须是一整段自然语言提示词，适合直接传给 ComfyUI，不要写项目符号，不要写解释。
- 画面适合 16:9 横版构图，可以包含图标、抽象人物、产品符号、数据卡片、信息分区、场景对比等视觉元素。

输出严格 JSON 对象，且只包含 items 字段。
items 必须是长度为 3 的数组，每个对象必须包含：
- title：这张配图对应的信息段标题，12字以内
- description：一段完整的 ComfyUI 中文文生图描述词
- keywords：3-6 个中文关键词

要求：
1. items 数量必须等于 3。
2. description 不要包含换行，不要包含 Markdown，不要包含编号。
3. 三段 description 的画面主体、构图和信息重点必须不同，但整体风格统一。
4. description 只写图像描述词，不要写“第一张图”“配图提示词”等说明性话术。
5. JSON 字符串内不得出现未转义的英文双引号。
""".strip()


def _get_platform_rule(platform: str) -> str:
    return PLATFORM_STYLE_RULES.get(
        platform,
        f"{platform}：根据平台名称推断用户场景，只生成适合“{platform}”发布的成品文案，并包含标题感正文、结尾引导和 #标签。",
    )


def _build_knowledge_context_section(knowledge_context: str) -> str:
    context = knowledge_context.strip()
    if not context:
        return ""
    return f"""

知识库上下文（来自用户选择的知识库）：
{context}
""".rstrip()
