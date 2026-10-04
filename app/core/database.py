import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

# Normalize URL for psycopg v3 dialect if needed
database_url = settings.DATABASE_URL
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif database_url.startswith("postgresql://") and "+psycopg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Connection pool settings optimized for serverless Neon PostgreSQL
engine_args = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# Only add pool sizing for non-serverless/standard pools
if "sqlite" not in database_url:
    engine_args.update({
        "pool_size": 10,
        "max_overflow": 20,
    })

engine = create_engine(database_url, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for providing database session to route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize all tables defined in models."""
    try:
        # Import models so Base metadata is populated
        import app.models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as exc:
        logger.warning(
            "Could not connect to Neon DB during startup or tables creation: %s. "
            "Verify your DATABASE_URL in .env.",
            exc,
        )
