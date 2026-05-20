import re
from typing import Dict, Optional

def detect_intent(query: str):
    lower_query = query.lower()

    intent = "general"
    time_range = None
    entity = None

    # its keyword based which has to be ai based in future
    news_keywords = [
        "news",
        "latest",
        "current",
        "today",
        "happening",
        "updates",
        "headlines",
    ]

    if any(keyword in lower_query for keyword in news_keywords):
        intent = "latest_news" 

    if "today" in lower_query:
        time_range = "today"
    elif "this week" in lower_query:
        time_range = "this_week"
    elif "latest" in lower_query or "current" in lower_query:
        time_range = "latest"

    patterns = [
        r"about (.+)",
        r"on (.+)",
        r"of (.+)",
        r"for (.+)",
        r"happening with (.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, lower_query)
        if match:
            entity = match.group(1).strip()
            break

    if not entity:
        cleaned = lower_query
        for word in news_keywords:
            cleaned = cleaned.replace(word, "")
        cleaned = cleaned.replace("what is", "")
        cleaned = cleaned.replace("what's", "")
        cleaned = cleaned.replace("tell me", "")
        cleaned = cleaned.replace("jarvis", "")
        cleaned = cleaned.strip(" ?.")
        entity = cleaned if cleaned else None

    return {
        "intent": intent,
        "entity": entity,
        "time_range": time_range
    }