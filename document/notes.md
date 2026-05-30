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

Your Jarvis becomes more serious because it has:
Voice loop
Real-time news
LLM summarization
Source tracking
Persistent memory/history

trafilatura:
trafilatura is useful because it extracts clean article text from messy web pages.

After Jarvis fetches articles:
Article content saved
   ↓
If content exists
   ↓
Split content into chunks
   ↓
Save chunks

For now, because your current articles have content_available: false, chunking may not create chunks for those rows yet. That is okay. The system will be ready for when full content extraction works or when we ingest direct article text later.

Training/Backpropagation: If you are training that network, backpropagation updates the model's weights based on how accurately it processes these individual chunks.

Trafilatura is meant to extract main text from actual web pages, and feedparser gives us RSS entry fields like summary and link, but Google News RSS links are often redirect/wrapper links rather than clean publisher article URLs. Feedparser’s docs also confirm entry.summary comes from RSS description/summary fields, which explains why we only reliably get snippets from RSS right now.

trafilatura = good general extractor
newspaper3k = good for news articles
BeautifulSoup = fallback text cleanup

For a serious Jarvis news intelligence pipeline, Google News RSS should be used mainly for discovery, not as the only source.

Later we should add direct feeds from sources like:
TechCrunch RSS
The Verge RSS
VentureBeat RSS
MIT Tech Review RSS
Google AI Blog
OpenAI Blog
Anthropic News
NVIDIA Blog
Microsoft AI Blog

