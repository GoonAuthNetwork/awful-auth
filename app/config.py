from enum import Enum
import os
from pathlib import Path
import sys
from urllib import parse
from typing import Dict, Optional

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseSettings, Field

DEVELOPMENT = os.environ.get("development", "False") == "True"

# Only load .env on development
# Production should handle this via docker-compose, etc
if DEVELOPMENT:
    load_dotenv()


class CacheSystem(str, Enum):
    MEMORY = "memory"
    REDIS = "redis"


class ApiSettings(BaseSettings):
    challenge_lifespan: int = Field(10, env="HASH_CHALLENGE_LIFESPAN_MINS")
    auth_lifespan: int = Field(5, env="HASH_AUTH_LIFESPAN_MINS")

    cache_system: CacheSystem = Field(CacheSystem.MEMORY, env="CACHE_SYSTEM")

    redis_host: str = Field("localhost", env="CACHE_REDIS_ADDRESS")
    redis_port: int = Field(6379, env="CACHE_REDIS_PORT")
    redis_db: int = Field(0, env="CACHE_REDIS_DB")
    redis_pass: Optional[str] = Field(None, env="CACHE_REDIS_PASSWORD")


api_settings = ApiSettings()


class SomethingAwfulSettings(BaseSettings):
    # TODO: rate limiting, etc

    session_id: str = Field(..., env="SA_COOKIES_SESSION_ID")
    session_hash: str = Field(..., env="SA_COOKIES_SESSION_HASH")
    bb_user_id: str = Field(..., env="SA_COOKIES_BB_USER_ID")
    bb_user_pass: str = Field(..., env="SA_COOKIES_BB_PASSWORD")

    profile_url: str = Field(
        "http://forums.somethingawful.com/member.php?action=getinfo&username=",
        env="SA_PROFILE_URL",
    )

    rap_sheet_url: str = Field(
        "https://forums.somethingawful.com/banlist.php?userid=",
        env="SA_RAP_SHEET_URL",
    )

    def create_cookie_container(self) -> Dict[str, str]:
        return {
            "sessionid": self.session_id,
            "sessionhash": self.session_hash,
            "bbuserid": self.bb_user_id,
            "bbpassword": self.bb_user_pass,
        }

    def create_profile_url(self, user_name: str) -> str:
        # TODO: Handle id as well as username
        sanitized_user = parse.quote(user_name)
        return f"{self.profile_url}{sanitized_user}"

    def create_rap_sheet_url(self, user_id: str) -> str:
        return f"{self.rap_sheet_url}{user_id}"


sa_settings = SomethingAwfulSettings()


class LoggingSettings(BaseSettings):
    level: str = Field("info", env="LOGGING_LEVEL")
    format: str = Field(
        "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
        + "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        env="LOGGING_FORMAT",
    )

    file: bool = Field(False, env="LOGGING_ENABLE_FILE")
    file_path: str = Field("/var/logs", env="LOGGING_FILE_PATH")
    file_name: str = Field("/access.log", env="LOGGING_FILE_NAME")
    file_rotation: str = Field("20 days", env="LOGGING_FILE_ROTATION")
    file_retention: str = Field("1 months", env="LOGGING_FILE_RETENTION")

    def setup_loguru(self):
        # Remove existing
        logger.remove()

        # Add stdout
        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=self.level.upper(),
            format=self.format,
        )

        # Add file if desires
        if self.file:
            path = Path.joinpath(self.file_path, self.file_name)
            logger.add(
                str(path),
                rotation=self.file_rotation,
                retention=self.file_retention,
                enqueue=True,
                backtrace=True,
                level=self.level.upper(),
                format=self.format,
            )


logging_settings = LoggingSettings()
