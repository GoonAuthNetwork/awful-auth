from urllib import parse
import uuid

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from redis import StrictRedis
from fakeredis import FakeStrictRedis
import httpx

from app.config import api_settings, sa_settings

if api_settings.cache_system == "redis":
    cache = StrictRedis(
        host=api_settings.redis_host,
        port=api_settings.redis_port,
        db=api_settings.redis_db,
        password=api_settings.redis_pass,
    )
else:
    cache = FakeStrictRedis(decode_responses=True)

app = FastAPI()


#
# Generate Challenge
#


class AuthRequest(BaseModel):
    user_name: str = Field(
        ..., title="SA Username", min_length=3, max_length=18, regex="^[\x00-\x7F]+$"
    )


class AuthChallenge(BaseModel):
    user_name: str = Field(
        ..., title="SA Username", min_length=3, max_length=18, regex="^[\x00-\x7F]+$"
    )
    hash: str = Field(title="Hash the user is required to place in profile")


@app.post("/v1/generate_challenge", response_model=AuthChallenge)
async def generate_goon_challenge(request: AuthRequest):
    # Url encode spaces. The rest of valuation should be done in AuthRequest
    user_name = parse.quote(request.user_name)

    hash = cache.get(f"hash:{user_name}")

    if hash is None:
        hash = str(uuid.uuid4()).replace("-", "")[:32]
        cache.setex(f"hash:{user_name}", api_settings.challenge_lifespan * 60, hash)

    return AuthChallenge(user_name=user_name, hash=hash)


#
# Check Challenge
#


class AuthStatus(BaseModel):
    validated: bool


@app.get("/v1/verify_challenge", response_model=AuthStatus)
async def verify_challenge(
    user_name: str = Query(
        ..., title="SA Username", min_length=3, max_length=18, regex="^[\x00-\x7F]+$"
    )
) -> AuthStatus:
    # Url encode spaces
    user_name = parse.quote(user_name)

    # Check the cache to see if we've authed
    if cache.exists(f"authed:{user_name}"):
        return AuthStatus(validated=True)

    # Check to see if we're waiting to check the challenge hash
    hash = cache.get(f"hash:{user_name}")
    if hash is not None:
        async with httpx.AsyncClient() as client:
            profile = sa_settings.create_profile_url(user_name)
            cookies = sa_settings.create_cookie_container()
            response = await client.get(profile, cookies=cookies)

        if response.status_code == 200 and hash in response.text:
            cache.setex(f"authed:{user_name}", api_settings.auth_lifespan * 60, "true")
            return AuthStatus(validated=True)
        else:
            raise HTTPException(status_code=404, detail="Hash not found in SA profile")

    # Naw mate, nothing here
    raise HTTPException(status_code=404, detail="Hash not found for user_name")


@app.delete("/v1/clear_auth")
async def clear_auth(
    user_name: str = Query(
        ..., title="SA Username", min_length=3, max_length=18, regex="^[\x00-\x7F]+$"
    )
):
    # Url encode spaces
    user_name = parse.quote(user_name)
    cache.delete(f"authed:{user_name}")
