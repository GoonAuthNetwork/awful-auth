from typing import Optional
import uuid
from loguru import logger
from redis import StrictRedis
from fakeredis import FakeStrictRedis

from app.config import api_settings
from app.models.goon_auth import GoonAuthStatus


class VerificationCache:
    def __init__(self, internal_cache: StrictRedis) -> None:
        self.cache = internal_cache

    def get_hash(
        self, user_name: str, create_if_not_exists: bool = False
    ) -> Optional[str]:
        key = f"hash:{user_name}"
        hash = self.cache.get(key)

        created = False
        if hash is None and create_if_not_exists:
            hash = str(uuid.uuid4()).replace("-", "")[:32]
            created = self.cache.setex(key, api_settings.challenge_lifespan * 60, hash)

        logger.debug(f"Got hash for `{user_name}`, created: {created}")

        return hash

    def delete_hash(self, user_name: str) -> bool:
        return self.cache.delete(f"hash:{user_name}") >= 1

    def get_auth(self, user_name: str) -> Optional[GoonAuthStatus]:
        key = f"authed:{user_name}"

        if self.cache.exists(key):
            data = self.cache.get(key)
            logger.debug(f"Found auth info for `{user_name}` - {data}")

            return GoonAuthStatus.parse_raw(data)

        logger.debug(f"Failed to find auth for `{user_name}`")

        return None

    def set_auth(self, user_name: str, status: GoonAuthStatus) -> bool:
        key = f"authed:{user_name}"
        value = status.json()

        logger.debug(f"Storing auth for `{user_name}` - {value}")

        return self.cache.setex(
            key, api_settings.auth_lifespan, value
        ) and self.delete_hash(user_name)

    def delete_auth(self, user_name: str) -> bool:
        return self.cache.delete(f"authed:{user_name}") >= 1


if api_settings.cache_system == "redis":
    logger.info(
        f"Connecting to redis at `{api_settings.redis_host}:{api_settings.redis_db}`..."
    )
    __internal_cache = StrictRedis(
        host=api_settings.redis_host,
        port=api_settings.redis_port,
        db=api_settings.redis_db,
        password=api_settings.redis_pass,
    )
    logger.info("Redis connected!")
else:
    logger.info("Using in memory FakeStrictRedis, please don't do this in production")
    __internal_cache = FakeStrictRedis(decode_responses=True)

cache = VerificationCache(__internal_cache)
