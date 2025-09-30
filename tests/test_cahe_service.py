import json
from unittest.mock import patch

from src.spacextracker.services import cache_service


def sample_func(x, y):
    return {"sum": x + y}


def test_cache_hit():
    cached_value = json.dumps({"sum": 3})

    with patch("src.spacextracker.services.cache_service.redis_client") as mock_redis:
        mock_redis.get.return_value = cached_value

        decorated = cache_service.redis_cache()(sample_func)
        result = decorated(1, 2)

        assert result == {"sum": 3}

        mock_redis.get.assert_called_once()
        mock_redis.setex.assert_not_called()


def test_cache_miss():
    with patch("src.spacextracker.services.cache_service.redis_client") as mock_redis:
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        decorated = cache_service.redis_cache()(sample_func)
        result = decorated(1, 2)

        assert result == {"sum": 3}

        assert mock_redis.get.called
        mock_redis.setex.assert_called_once()


def test_cache_miss_with_kwargs():
    with patch("src.spacextracker.services.cache_service.redis_client") as mock_redis:
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        decorated = cache_service.redis_cache()(sample_func)
        result = decorated(x=5, y=7)

        assert result == {"sum": 12}
        mock_redis.setex.assert_called_once()


def test_cache_ttl_override():
    with patch("src.spacextracker.services.cache_service.redis_client") as mock_redis:
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        decorated = cache_service.redis_cache(ttl=60)(sample_func)
        result = decorated(2, 3)

        assert result == {"sum": 5}
        args, kwargs = mock_redis.setex.call_args
        assert args[1] == 60
