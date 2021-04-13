import asyncio
import random
import string

from fakeredis import FakeStrictRedis
from fastapi.testclient import TestClient

import app.main
from app.config import sa_settings

# Mock Redis cache
app.main.cache = FakeStrictRedis(decode_responses=True)  # noqa: F811

# Make a TestClient from our FastAPI server
client = TestClient(app.main.app)


# Generate a random, valid, username to test with
def generate_username() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=15))


# Generate the url we need to mock for SA profile requests
def generate_profile_url(user_name: str) -> str:
    return sa_settings.create_profile_url(user_name)


# Add a user_name & hash to the redis cache
def generate_hash_in_cache(user_name: str) -> str:
    req = app.main.AuthRequest(user_name=user_name)
    func = app.main.generate_goon_challenge(req)

    loop = asyncio.get_event_loop()
    res: app.main.AuthChallenge = loop.run_until_complete(func)

    return res.hash
