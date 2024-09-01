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
    bind=engine,  # Bind the engine to the sessionmaker
    class_=AsyncSession,  # Use the AsyncSession class
    expire_on_commit=False,  # Keep objects available after commit
    autocommit=False,  # Disable autocommit
    autoflush=False  # Disable autoflush
)

# Define the declarative base class for models
Base = declarative_base()

# Export all necessary components
__all__ = ["SessionLocal", "Base", "engine"]
