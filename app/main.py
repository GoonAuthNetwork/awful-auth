from urllib import parse
import uuid

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from redis import StrictRedis
from fakeredis import FakeStrictRedis
import httpx

from . import config

SA_COOKIES = {
    "sessionid": config.SA_COOKIES_SESSION_ID,
    "sessionhash": config.SA_COOKIES_SESSION_HASH,
    "bbuserid": config.SA_COOKIES_BB_USER_ID,
    "bbpassword": config.SA_COOKIES_BB_PASSWORD,
}

SA_PROFILE_URL = "http://forums.somethingawful.com/member.php?action=getinfo&username="

if config.CACHE_SYSTEM == "redis":
    cache = StrictRedis(
        host=config.CACHE_REDIS_HOST,
        port=config.CACHE_REDIS_PORT,
        db=config.CACHE_REDIS_DB,
        password=config.CACHE_REDIS_PASSWORD,
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
        cache.setex(f"hash:{user_name}", config.HASH_CHALLENGE_LIFESPAN_MINS * 60, hash)

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
            response = await client.get(SA_PROFILE_URL + user_name, cookies=SA_COOKIES)

        if response.status_code == 200 and hash in response.text:
            cache.setex(
                f"authed:{user_name}", config.HASH_AUTH_LIFESPAN_MINS * 60, "true"
            )
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
