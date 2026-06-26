# Jarvis Dev Commands

## Docker Development

Start full stack:

```bash
docker compose up --build

Stop:
docker compose down

Stop and delete volumes:
docker compose down -v

View API logs:
docker compose logs -f api

View worker logs:
docker compose logs -f worker

Run migrations manually if needed:
docker compose exec api alembic upgrade head

Open API docs:
http://127.0.0.1:8000/docs
Local Development

Start Redis and Qdrant only:
docker compose up redis qdrant

Run local FastAPI:
uvicorn app.main:app --reload

Run local Celery worker on Windows:
celery -A app.celery_app.celery_app worker --loglevel=info --pool=solo -Q ingestion

Run local Celery beat:
celery -A app.celery_app.celery_app beat --loglevel=info

Run migrations locally:
alembic upgrade head
Voice CLI Local Only

Install voice dependencies:
pip install -r requirements-voice.txt

Run voice CLI:
python jarvis_voice_cli.py

Run text CLI:
python jarvis_cli.py
