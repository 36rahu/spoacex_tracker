import json
import functools
from hashlib import sha256
from typing import Callable, TypeVar, ParamSpec

from spacextracker.db import redis_client, CACHE_TTL
from spacextracker.logger import logger  # import your logger

P = ParamSpec("P")
R = TypeVar("R")


def redis_cache(ttl: int = CACHE_TTL) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Cache function results in Redis for a given TTL.

    Args:
        ttl (int): Cache time-to-live in seconds.

    Returns:
        Callable: Decorated function with Redis caching.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Create a unique cache key
            key_raw = {"func": func.__name__, "args": args, "kwargs": kwargs}
            key_str = json.dumps(key_raw, sort_keys=True, default=str)
            cache_key = f"cache:{sha256(key_str.encode()).hexdigest()}"

            try:
                # Try Redis cache
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    logger.info(f"Cache hit for {func.__name__} with key {cache_key}")
                    return json.loads(cached_data)

                logger.info(
                    f"Cache miss for {func.__name__} → calling original function"
                )
                # Call the original function
                result = func(*args, **kwargs)

                # Store in Redis
                redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
                logger.info(f"Stored result in cache with key {cache_key}")
                return result

            except Exception as e:
                logger.error(
                    f"Redis caching error for {func.__name__}: {e}", exc_info=True
                )
                # Fallback to calling the original function if Redis fails
                return func(*args, **kwargs)

        return wrapper

    return decorator
