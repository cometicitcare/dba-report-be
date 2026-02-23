"""
Buddhist Affairs MIS Dashboard - Database Connection
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from typing import AsyncGenerator

from app.config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=10,
    connect_args={
        "command_timeout": 15,
        "server_settings": {
            "statement_timeout": "15000",  # 15 seconds max per query
            "lock_timeout": "5000",         # 5 seconds max waiting for locks
        }
    },
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    Usage in FastAPI endpoint:
        async def endpoint(db: AsyncSession = Depends(get_db)):
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


async def execute_raw_sql(query: str, params: dict = None) -> list:
    """Execute raw SQL query and return results"""
    async with async_session_factory() as session:
        result = await session.execute(text(query), params or {})
        return result.fetchall()
