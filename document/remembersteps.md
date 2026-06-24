Alembic===>
From now on, whenever you change models:

Example:
new_column = Column(String(255), nullable=True)

Run:
alembic revision --autogenerate -m "add new column"
Review the generated file.

Then apply:
alembic upgrade head
If needed, rollback one migration:
alembic downgrade -1

To mark database as current--->
alembic stamp head

=>docker dataabse error
docker compose exec api python -c "from app.db.database import Base, engine; from app.db import models; Base.metadata.create_all(bind=engine)"
docker compose exec api alembic stamp head
docker compose exec postgres psql -U postgres -d jarvis_db -c "\dt"

=> docker commands:

To run docker containers:
Docker compose up -d (for detached mode)

Stop containers:
docker compose down

Stop and delete volumes/data:
docker compose down -v

Rebuild API after dependency changes:
docker compose up --build

View API logs:
docker compose logs -f api

View worker logs:
docker compose logs -f worker

Open shell inside API container:
docker compose exec api bash

Run Alembic inside API container:
docker compose exec api alembic upgrade head

=>
postgreSQL uses localhost
Docker uses postgreSQL

================================================
1. Code changes vs database changes

Normal code changes like these:
routes
services
schemas
LLM logic
RAG logic
Celery task logic
API endpoint changes

do not need Alembic.

For these, you only restart/rebuild the app:
docker compose up --build

or if containers are already running:
docker compose restart api worker beat

2. Requirements changes

If you change:
requirements.txt
Dockerfile
docker-compose.yml
.env.docker

then you need Docker rebuild:
docker compose up --build

or stronger:
docker compose build --no-cache
docker compose up

Alembic is not for requirements.

3. Database model changes

Alembic is only for database schema changes.
For example, if you change app/db/models.py like:

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    author = Column(String(255), nullable=True)  # new column

Then you do:
docker compose exec api alembic revision --autogenerate -m "add author to articles"

Then apply it:
docker compose exec api alembic upgrade head

4. What are we automating?
We are not automating migration generation.

This command should stay manual:
alembic revision --autogenerate -m "..."

Because generated migrations must be reviewed. You don’t want Docker randomly creating migration files in production.
What we do want to automate is this command:
docker compose exec api alembic upgrade head

That means:
when container starts
↓
wait for PostgreSQL
↓
run alembic upgrade head automatically
↓
start FastAPI

So after we add entrypoint.sh, you won’t manually run this every startup:
docker compose exec api alembic upgrade head

Docker will run it for you.

=============================================
Simple rule

Use this mental model:

Changed normal Python code?
→ restart/rebuild Docker

Changed requirements.txt?
→ docker compose up --build

Changed database models.py?
→ create Alembic migration manually
→ Docker startup applies it automatically
==============================================
