import os
from dotenv import load_dotenv

DEVELOPMENT = os.environ.get("development", "False") == "True"

# Only load .env on development
# Production should handle this via docker-compose, etc
if DEVELOPMENT:
    load_dotenv()

# API Config
HASH_CHALLENGE_LIFESPAN_MINS = int(os.environ.get("HASH_CHALLENGE_LIFESPAN_MINS", "10"))
HASH_AUTH_LIFESPAN_MINS = int(os.environ.get("HASH_AUTH_LIFESPAN_MINS", "5"))

# SA Cookies
SA_COOKIES_SESSION_ID = os.environ.get("SA_COOKIES_SESSION_ID")
SA_COOKIES_SESSION_HASH = os.environ.get("SA_COOKIES_SESSION_HASH")
SA_COOKIES_BB_USER_ID = os.environ.get("SA_COOKIES_BB_USER_ID")
SA_COOKIES_BB_PASSWORD = os.environ.get("SA_COOKIES_BB_PASSWORD")

# Cache system, redis/memory
CACHE_SYSTEM = os.environ.get("CACHE_SYSTEM", "memory")

# Redis settings
CACHE_REDIS_HOST = os.environ.get("CACHE_REDIS_ADDRESS", "localhost")
CACHE_REDIS_PORT = int(os.environ.get("CACHE_REDIS_PORT", "6379"))
CACHE_REDIS_DB = int(os.environ.get("CACHE_REDIS_DB", "0"))
CACHE_REDIS_PASSWORD = os.environ.get("CACHE_REDIS_PASSWORD")
