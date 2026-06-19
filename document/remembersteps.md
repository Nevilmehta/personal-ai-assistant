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

