import uuid

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from redis import StrictRedis
from fakeredis import FakeStrictRedis

from app.models.goon_auth import GoonAuthChallenge, GoonAuthRequest, GoonAuthStatus

# TODO: move sa interaction and cache system into their own files
from app.config import api_settings

router = APIRouter(prefix="/goon_auth", tags=["SA Auth"])

# TODO: move sa interaction and cache system into their own files
if api_settings.cache_system == "redis":
    cache = StrictRedis(
        host=api_settings.redis_host,
        port=api_settings.redis_port,
        db=api_settings.redis_db,
        password=api_settings.redis_pass,
    )
else:
    cache = FakeStrictRedis(decode_responses=True)


@router.get(
    "/verification",
    response_model=GoonAuthChallenge,
    description="Generates a new hashed based authentication challenge",
)
async def generate_verification(
    request: GoonAuthRequest = Depends(),
) -> GoonAuthChallenge:
    user = request.user_name_sanitized()

    # Use existing hash if available
    hash = cache.get(f"hash:{user}")

    if hash is None:
        # Or create a new one
        hash = str(uuid.uuid4()).replace("-", "")[:32]
        cache.setex(f"hash:{user}", api_settings.challenge_lifespan * 60, hash)

    return GoonAuthChallenge(user_name=user, hash=hash)


@router.get(
    "/verification/update",
    response_model=GoonAuthStatus,
    description="Updated a pending verification returning "
    "the full user's data if successful",
)
async def update_verification(request: GoonAuthRequest = Depends()) -> GoonAuthStatus:
    pass


@router.delete(
    "/verification",
    description="Deletes a pending verification including any related data",
)
async def delete_verification(request: GoonAuthStatus = Depends()):
    user = request.user_name_sanitized()

    deleted = 0
    deleted += cache.delete(f"hash:{user}")
    deleted += cache.delete(f"authed:{user}")

    if deleted == 0:
        raise HTTPException(404, detail="Verification for supplied user does not exist")
