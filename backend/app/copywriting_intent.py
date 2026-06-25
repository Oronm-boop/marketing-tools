RECOMMENDATION_INTENT_TERMS = (
    "推荐",
    "选购",
    "对比",
    "横向",
    "性价比",
    "哪款",
    "哪一款",
    "榜单",
    "排行榜",
    "排行",
    "清单",
    "测评",
    "评测",
    "入手",
    "购买",
    "买什么",
    "怎么选",
    "避坑",
)


def has_recommendation_intent(*parts: str) -> bool:
    haystack = " ".join(part for part in parts if part)
    return any(term in haystack for term in RECOMMENDATION_INTENT_TERMS)
