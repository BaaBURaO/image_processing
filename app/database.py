# database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database URL
DATABASE_URL = "postgresql+asyncpg://user:password@db/image_processing_db"

# Create the asynchronous engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# Create the async session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

__all__ = ["SessionLocal", "Base", "engine"]
