"""Async SQLAlchemy engine, session factory, and Redis connection pool."""

from __future__ import annotations

from typing import AsyncGenerator

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# ── SQLAlchemy ────────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Redis ─────────────────────────────────────────────────────────────────────
redis_pool: aioredis.Redis | None = None


async def init_redis() -> aioredis.Redis:
    """Initialise the Redis connection pool (call once at startup)."""
    global redis_pool
    redis_pool = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
    )
    return redis_pool


async def close_redis() -> None:
    """Shut down the Redis connection pool (call at shutdown)."""
    global redis_pool
    if redis_pool is not None:
        await redis_pool.close()
        redis_pool = None


async def get_redis() -> aioredis.Redis:
    """FastAPI dependency — returns the shared Redis client."""
    if redis_pool is None:
        raise RuntimeError("Redis pool not initialised. Call init_redis() first.")
    return redis_pool
