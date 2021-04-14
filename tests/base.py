from os import path
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


# Generates a mock profile page with the specified hash
def generate_profile_page(hash: str) -> str:
    base = path.dirname(__file__)
    file = path.join(base, "content/hash-profile-template.html")

    with open(file, "r") as file:
        contents = file.read()
        return contents.replace("{INSERT_HASH_HERE}", hash)


# Generate the url we need to mock for SA profile requests
def generate_profile_url(user_name: str) -> str:
    return sa_settings.create_profile_url(user_name)


# Add a user_name & hash to the auth system
def generate_hash_in_cache(user_name: str) -> str:
    response = client.get("/goon_auth/verification", params={"user_name": user_name})
    unpacked = response.json()

    if response.status_code != 200 or "hash" not in unpacked:
        raise RuntimeError("Failed to add hash to cache")

    return unpacked["hash"]
