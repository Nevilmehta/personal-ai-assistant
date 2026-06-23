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

