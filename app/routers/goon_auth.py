from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends

from app.models.goon_auth import GoonAuthChallenge, GoonAuthRequest, GoonAuthStatus
from app.sa_utils import check_auth_status
from app.verification_cache import cache

router = APIRouter(prefix="/goon_auth", tags=["SA Auth"])


@router.get(
    "/verification",
    response_model=GoonAuthChallenge,
    description="Generates a new hashed based authentication challenge",
)
async def generate_verification(
    request: GoonAuthRequest = Depends(),
) -> GoonAuthChallenge:
    user = request.user_name

    hash = cache.get_hash(user)
    if hash is None:
        raise HTTPException(500, "Failed to create hash")

    return GoonAuthChallenge(user_name=user, hash=hash)


@router.get(
    "/verification/update",
    response_model=GoonAuthStatus,
    description="Updated a pending verification returning "
    "the full user's data if successful",
)
async def update_verification(request: GoonAuthRequest = Depends()) -> GoonAuthStatus:
    # Previously authed and in the cache period
    pre_check = cache.get_auth(request.user_name)
    if pre_check is not None:
        return pre_check

    # Ensure we have a hash to check against
    hash = cache.get_hash(request.user_name, create_if_not_exists=False)
    if hash is None:
        raise HTTPException(404, detail="Hash not found for specified user")

    # Check and set/return
    status = await check_auth_status(request.user_name, hash)
    if status is None:
        return GoonAuthStatus(validated=False)

    if not cache.set_auth(request.user_name, status):
        raise HTTPException(500, detail="Failed to save auth")

    return status


@router.delete(
    "/verification",
    description="Deletes a pending verification including any related data",
)
async def delete_verification(request: GoonAuthStatus = Depends()):
    user = request.user_name

    if not (cache.delete_hash(user) or cache.delete_auth(user)):
        raise HTTPException(404, detail="Verification for supplied user does not exist")
