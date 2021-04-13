from typing import Optional
import uuid
from redis import StrictRedis
from fakeredis import FakeStrictRedis

from app.config import api_settings
from app.models.goon_auth import GoonAuthStatus


class VerificationCache:
    def __init__(self, internal_cache: StrictRedis) -> None:
        self.cache = internal_cache

    def get_hash(
        self, user_name: str, create_if_not_exists: bool = True
    ) -> Optional[str]:
        key = f"hash:{user_name}"
        hash = self.cache.get(key)

        if hash is None and create_if_not_exists:
            hash = str(uuid.uuid4()).replace("-", "")[:32]
            self.cache.setex(key, api_settings.challenge_lifespan * 60, hash)

        return hash

    def delete_hash(self, user_name: str) -> bool:
        return self.cache.delete(f"hash:{user_name}") >= 1

    def get_auth(self, user_name: str) -> Optional[GoonAuthStatus]:
        key = f"authed:{user_name}"

        if self.cache.exists(key):
            data = self.cache.get(key)
            return GoonAuthStatus.parse_raw(data)

        return None

    def delete_auth(self, user_name: str) -> bool:
        return self.cache.delete(f"authed:{user_name}") >= 1


if api_settings.cache_system == "redis":
    internal_cache = StrictRedis(
        host=api_settings.redis_host,
        port=api_settings.redis_port,
        db=api_settings.redis_db,
        password=api_settings.redis_pass,
    )
else:
    internal_cache = FakeStrictRedis(decode_responses=True)

cache = VerificationCache(internal_cache)
