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

--------------------------------------------------------
For this first version, the audio works in a very simple way:

Press Enter
   ↓
Record fixed 5 seconds
   ↓
Save temporary WAV file
   ↓
Whisper transcribes it
   ↓
Send text to Jarvis

So yes, it will sometimes miss words, cut you off, or misunderstand if:

you start speaking late
you speak longer than 5 seconds
background noise is high
mic quality is weak
you speak too softly
Whisper model is too small
