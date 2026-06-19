import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from app.config import settings
from app.db.database import Base
from app.db import models  # noqa: F401


config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata