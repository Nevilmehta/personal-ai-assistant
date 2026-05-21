The intent service understands the user.

The query planner decides what to do.

Later this becomes the “brain router.” - query_planner
---------
Pipeline Architecture:
main.py
   ↓
jarvis_orchestrator.py
   ↓
intent_service.py
   ↓
query_planner.py
   ↓
news_service.py
   ↓
llm_service.py
This is the start of a real system.

------------------------
Later query_planner will decide,
latest_news → news service
personal question → memory service
calendar → calendar service
open app → device control service
old knowledge → vector DB

