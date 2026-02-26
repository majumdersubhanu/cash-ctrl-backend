import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.core.config import settings
from app.models import *  # noqa
from app.db.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
