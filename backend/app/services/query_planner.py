from app.schemas.jarvis_schema import IntentResult, QueryPlan

LIVE_NEWS_KEYWORDS = [
    "today",
    "latest",
    "current",
    "breaking",
    "right now",
    "recent news",
    "headlines",
    "news today",
]

KNOWLEDGE_BASE_KEYWORDS = [
    "previous",
    "earlier",
    "stored",
    "tracked",
    "history",
    "historical",
    "before",
    "last week",
    "this month",
    "trend",
    "trends",
    "recurring",
    "compare",
    "comparison",
]

HYBRID_KEYWORDS = [
    "compare",
    "compared",
    "versus",
    " vs ",
    "difference between",
    "changed since",
    "today and before",
    "today versus",
    "today compared",
    "current compared",
    "latest compared",
]

def create_query_plan(
    original_query: str,
    intent_result: IntentResult,
) -> QueryPlan:
    lower_query = original_query.lower()

    use_live_news = should_use_live_news(
        lower_query=lower_query,
        intent=intent_result.intent,
    )

    use_knowledge_base = should_use_knowledge_base(
        lower_query=lower_query,
    )

    retrieval_type = determine_retrieval_type(
        use_live_news=use_live_news,
        use_knowledge_base=use_knowledge_base,
        lower_query=lower_query,
    )

    search_query = build_search_query(
        intent_result=intent_result,
        original_query=original_query,
    )

    return QueryPlan(
        original_query=original_query,
        intent=intent_result.intent,
        entity=intent_result.entity,
        time_range=intent_result.time_range,
        search_query=search_query,
        retrieval_type=retrieval_type,
        use_live_news=use_live_news,
        use_knowledge_base=use_knowledge_base,
    )


def should_use_live_news(
    lower_query: str,
    intent: str,
) -> bool:
    if intent == "latest_news":
        return True

    return any(
        keyword in lower_query
        for keyword in LIVE_NEWS_KEYWORDS
    )


def should_use_knowledge_base(lower_query: str) -> bool:
    return any(
        keyword in lower_query
        for keyword in KNOWLEDGE_BASE_KEYWORDS
    )


def determine_retrieval_type(
    use_live_news: bool,
    use_knowledge_base: bool,
    lower_query: str,
) -> str:
    if any(keyword in lower_query for keyword in HYBRID_KEYWORDS):
        return "hybrid"

    if use_live_news and use_knowledge_base:
        return "hybrid"

    if use_live_news:
        return "live_news"

    if use_knowledge_base:
        return "knowledge_base"

    return "general"


def build_search_query(
    intent_result: IntentResult,
    original_query: str,
) -> str:
    entity = intent_result.entity

    if not entity:
        return original_query

    if intent_result.time_range == "today":
        return f"{entity} today"

    if intent_result.time_range == "this_week":
        return f"{entity} this week"

    return entity