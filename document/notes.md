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

----------------------------------------
RSS adapters
   ├── Google News adapter
   ├── direct publisher RSS adapter
   └── future API adapter
          ↓
normalized article records
          ↓
content extraction
          ↓
article storage

-----------------------------------------
Embedding + Qdrant Vector Search:

Full article content when available
        ↓
Otherwise cleaned RSS snippet
        ↓
Otherwise title
        ↓
Article chunks
        ↓
Embedding model
        ↓
Qdrant vector database
        ↓
Semantic search API

We will use Qdrant because its local setup is straightforward with Docker, and its Python client supports collections, vectors with payloads, upserts, and similarity queries. Qdrant’s official quickstart exposes REST on port 6333, gRPC on 6334, and a local dashboard.

Uploaded Architecture:
PostgreSQL
├── articles
├── article_chunks
└── query history

Qdrant
└── jarvis_article_chunks
    ├── vector
    └── payload
        ├── chunk_id
        ├── article_id
        ├── title
        ├── source
        ├── published
        ├── content_quality
        └── text

PostgreSQL remains your source of truth.
Qdrant stores searchable vector representations.

This follows Qdrant’s standard flow:
create collection
↓
upsert PointStruct vectors with payload
↓
query_points for similarity search
---------------------------------------------

QDrant works:
For each article chunk:
article chunk
↓
embedding model converts text into vector
↓
Qdrant stores vector + metadata

When the user asks:
"What AI startups recently raised funding?"

we do:
user query
↓
convert query into vector
↓
Qdrant compares query vector with stored chunk vectors
↓
returns most semantically similar chunks

Qdrant supports similarity search and hybrid retrieval using dense and sparse vectors, and it exposes HTTP and gRPC APIs with official client libraries for multiple languages.

Unlike traditional REST APIs that pass data as text (like JSON or XML), a gRPC API allows a client application to directly call a function or method on a remote server application as if it were a local function on its own machine.

Think of it like SQL databases:
PostgreSQL
MySQL
MongoDB
DynamoDB

There is not only one database.
Similarly, for vector search:
Qdrant
Pinecone
Weaviate
Milvus
pgvector
Chroma
FAISS

Why not store everything only in PostgreSQL?
Because Qdrant is optimized for:
Find the text chunks whose meaning is closest to this query

PostgreSQL = organized storage room
Qdrant = intelligent search engine

We remove repetitive articles because one article can contain multiple chunks. Qdrant also provides a grouping API specifically for situations where a large document is split into multiple chunks and you want results grouped by document ID. For this first version, application-side deduplication is easier to understand and debug.

Your existing database endpoints can continue using FastAPI’s Depends(get_db) pattern. FastAPI’s dependency-injection system calls the dependency and injects its result into the route function, which is why your SQLAlchemy session setup works cleanly in the existing endpoints.

--------------------------------------------------

stored knowledge
   ↓
chunking
   ↓
embeddings
   ↓
Qdrant vector search
   ↓
context retrieval
   ↓
Gemini grounded answer
   ↓
source list

Jarvis can choose between:
live news search
stored knowledge retrieval
hybrid intelligence
general conversation

Right now jarvis stores articles only when u ask a question,

Redis = task broker
Celery worker = ingestion processor
Celery Beat = scheduler

Later, Kafka can replace or supplement parts of this system when we introduce streaming ingestion from RSS, videos, podcasts, and other event sources.

Architecture after this phase:
Celery Beat
   ↓ every 30 minutes
Redis Queue
   ↓
Celery Ingestion Worker
   ↓
Tracked topics
   ├── artificial intelligence
   ├── AI startups
   ├── OpenAI
   ├── Anthropic
   └── NVIDIA AI
         ↓
News retrieval
         ↓
PostgreSQL article storage
         ↓
Chunk creation
         ↓
Embedding generation
         ↓
Qdrant upsert

Redis database 0 will carry queued tasks.
Redis database 1 will temporarily store task results.

First ingestion
→ snippet fallback saved

Later ingestion
→ full article extraction succeeds
→ article content upgraded
→ snippet chunks replaced by full-content chunks

Jarvis can learn without waiting for you to ask:
scheduled ingestion
Redis task queue
Celery worker
topic-based retrieval
automatic PostgreSQL storage
chunk generation
Qdrant indexing
RAG-ready knowledge

--------------------------------------->
Beat = alarm clock
Redis = waiting area
Worker = employee
Task function = actual job instructions
PostgreSQL = permanent article storage
Qdrant = searchable vector storage

--------------------------------------------------
After phase 2.7,
Jarvis now has dashboard-ready APIs:

ingestion overview
topic overview
knowledge base overview
system overview

This is important because later you can build:

Jarvis Control Center

with cards like:

Tracked Topics: 7
Enabled Topics: 6
Articles Stored: 120
Chunks Indexed: 120
Latest Ingestion: Success
Failed Runs: 0
Full Content Articles: 12

------------------------------------------
What is gRPC?
gRPC is a way for two programs/services to talk to each other.

In your project:
FastAPI backend
   ↓ talks to
Qdrant vector database

Earlier they were talking through normal HTTP/REST.
Now they are talking through gRPC.

gRPC
gRPC is more like a fast direct service-to-service call.
Instead of sending JSON text, it sends compact binary data using something called Protocol Buffers.

So instead of:
Send big JSON request
Parse JSON response

it does:
Send compact binary request
Receive compact binary response

That makes it faster and more efficient for backend services.

Qdrant:
REST = easier for manual debugging
gRPC = better for app-to-database performance

By switching to gRPC:
FastAPI → Qdrant

became more efficient and stable for vector search.
This is common when a service supports both REST and gRPC.

-------------------------------------------------------------------------
Where gRPC is used in real systems-->

gRPC is commonly used in:
microservices
vector databases
internal backend services
high-performance APIs
real-time systems
AI infrastructure
Kubernetes-based systems

Example:
speech-service → intent-service
intent-service → rag-service
rag-service → vector-db

In your future Jarvis architecture, gRPC could be used between internal services.

I used REST for the public FastAPI endpoints because it is easy for clients and dashboards to consume. For the vector database communication with Qdrant, I switched to gRPC because vector search involves sending dense numeric embeddings, and gRPC is more efficient and stable for internal service-to-service communication.

-----------------------------------------------------

Dockerize the full Backend stack,
Target Docker Architecture:

jarvis-api
   ↓
PostgreSQL
Redis
Qdrant

jarvis-worker
   ↓
Redis queue
PostgreSQL
Qdrant

jarvis-beat
   ↓
Redis queue