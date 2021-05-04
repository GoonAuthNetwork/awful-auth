from fastapi import APIRouter
from fastapi.param_functions import Depends

from app.models.error import ApiError
from app.models.goon_auth import GoonAuthChallenge, GoonAuthRequest, GoonAuthStatus
from app.sa_utils import check_auth_status
from app.verification_cache import cache

router = APIRouter(prefix="/goon_auth", tags=["SA Auth"])


@router.get(
    "/verification",
    description="Generates a new verification hash for the specified user",
    response_model=GoonAuthChallenge,
    responses={500: {"model": ApiError, "description": "Hash Creation Error"}},
)
async def generate_verification(
    request: GoonAuthRequest = Depends(),
) -> GoonAuthChallenge:
    user = request.user_name

    hash = cache.get_hash(user, create_if_not_exists=True)
    if hash is None:
        return ApiError.create_response(500, "Failed to create hash")

    return GoonAuthChallenge(user_name=user, hash=hash)


@router.get(
    "/verification/update",
    description="Updated a pending verification returning "
    "the full user's data if successful",
    response_model=GoonAuthStatus,
    responses={
        404: {"model": ApiError, "description": "Hash Not Found Error"},
        500: {"model": ApiError, "description": "Auth Save Error"},
    },
)
async def update_verification(request: GoonAuthRequest = Depends()) -> GoonAuthStatus:
    # Previously authed and in the cache period
    pre_check = cache.get_auth(request.user_name)
    if pre_check is not None:
        return pre_check

    # Ensure we have a hash to check against
    hash = cache.get_hash(request.user_name)
    if hash is None:
        return ApiError.create_response(404, "Hash not found for specified user")

    # Check and set/return
    status = await check_auth_status(request.user_name, hash)
    if status is None:
        return GoonAuthStatus(validated=False)

    if not cache.set_auth(request.user_name, status):
        return ApiError.create_response(500, "Failed to save auth")

    # Clean up check
    if status.validated:
        cache.delete_hash(request.user_name)

    return status


@router.delete(
    "/verification",
    description="Deletes a pending verification including any related data",
    responses={
        404: {"model": ApiError, "description": "User Not Found Error"},
    },
)
async def delete_verification(request: GoonAuthRequest = Depends()):
    user = request.user_name

    if not (cache.delete_hash(user) or cache.delete_auth(user)):
        return ApiError.create_response(404, "Verification for user does not exist")
