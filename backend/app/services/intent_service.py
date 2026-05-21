import re
from typing import Dict, Optional
from app.schemas.jarvis_schema import IntentResult

# its keyword based which has to be ai based in future
NEWS_KEYWORDS = [
    "news",
    "latest",
    "current",
    "today",
    "happening",
    "updates",
    "headlines",
]

def detect_intent(query: str):
    lower_query = query.lower().strip()

    intent = "general"
    time_range: Optional[str] = None
    entity: Optional[str] = None

    if any(keyword in lower_query for keyword in NEWS_KEYWORDS):
        intent = "latest_news" 

    if "today" in lower_query:
        time_range = "today"
    elif "this week" in lower_query:
        time_range = "this_week"
    elif "latest" in lower_query or "current" in lower_query:
        time_range = "latest"

    entity = extract_entity(lower_query)

    return IntentResult(
        intent=intent,
        entity=entity,
        time_range=time_range
    )

def extract_entity(lower_query: str):
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
            return clean_entity(match.group(1))

    cleaned = lower_query

    for word in NEWS_KEYWORDS:
        cleaned = cleaned.replace(word, "")

    remove_phrases = [
        "what is",
        "what's",
        "tell me",
        "jarvis",
        "hello",
        "hey",
    ]

    for phrase in remove_phrases:
        cleaned = cleaned.replace(phrase, "")

    cleaned = clean_entity(cleaned)

    return cleaned if cleaned else None

def clean_entity(entity: str):
    remove_words = [
        "today",
        "latest",
        "current",
        "news",
        "updates",
        "headlines",
    ]

    cleaned = entity.strip(" ?.,")

    for word in remove_words:
        cleaned = cleaned.replace(word, "")

    return cleaned.strip(" ?.,")