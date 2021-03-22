import asyncio
import random
import string

from fakeredis import FakeStrictRedis
from fastapi.testclient import TestClient

import src.server

# Mock Redis cache
src.server.cache = FakeStrictRedis(decode_responses=True)  # noqa: F811

# Make a TestClient from our FastAPI server
client = TestClient(src.server.app)


# Generate a random, valid, username to test with
def generate_username() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=15))


# Generate the url we need to mock for SA profile requests
def generate_profile_url(user_name: str) -> str:
    return src.server.SA_PROFILE_URL + user_name


# Add a user_name & hash to the redis cache
def generate_hash_in_cache(user_name: str) -> str:
    req = src.server.AuthRequest(user_name=user_name)
    func = src.server.generate_goon_challenge(req)

    loop = asyncio.get_event_loop()
    res: src.server.AuthChallenge = loop.run_until_complete(func)

    return res.hash
