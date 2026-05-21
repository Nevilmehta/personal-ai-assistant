from app.schemas.jarvis_schema import IntentResult, QueryPlan

def create_query_plan(original_query: str, intent_result: IntentResult):
    """
    Converts user intent into an executable plan.

    In future this can decide:
    - search news
    - search vector DB
    - search calendar
    - control device
    - query personal memory
    """

    if intent_result.intent == "latest_news":
        search_query = build_news_search_query(intent_result, original_query)

        return QueryPlan(
            original_query=original_query,
            intent=intent_result.intent,
            entity=intent_result.entity,
            time_range=intent_result.time_range,
            search_query=search_query,
            retrieval_type="news_search",
        )

    return QueryPlan(
        original_query=original_query,
        intent=intent_result.intent,
        entity=intent_result.entity,
        time_range=intent_result.time_range,
        search_query=original_query,
        retrieval_type="llm_only",
    )

def build_news_search_query(intent_result: IntentResult, original_query: str):
    entity = intent_result.entity

    if entity:
        if intent_result.time_range == "today":
            return f"{entity} today"
        if intent_result.time_range == "this_week":
            return f"{entity} this week"
        return entity

    return original_query