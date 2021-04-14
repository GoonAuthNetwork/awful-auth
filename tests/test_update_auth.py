from pytest_httpx import HTTPXMock

from .base import (
    client,
    generate_username,
    generate_profile_page,
    generate_profile_url,
    generate_hash_in_cache,
)


# Test requiring a username
def test_update_verification_require_username():
    data = {}
    response = client.get("/goon_auth/verification/update", params=data)
    unpacked = response.json()
    detail = unpacked["detail"][0]

    assert response.status_code == 422
    assert "user_name" in detail["loc"]
    assert detail["msg"] == "field required"
    assert detail["type"] == "value_error.missing"


def test_update_verification_managled_username():
    data = {"user_name": "🤔🤔🤔🤔🤔"}
    response = client.get("/goon_auth/verification/update", params=data)
    unpacked = response.json()
    detail = unpacked["detail"][0]

    assert response.status_code == 422
    assert "user_name" in detail["loc"]
    assert "string does not match regex " in detail["msg"]


def test_update_verification_hash_not_found():
    data = {"user_name": generate_username()}
    response = client.get("/goon_auth/verification/update", params=data)
    unpacked = response.json()

    assert response.status_code == 404
    assert unpacked["message"] == "Hash not found for specified user"


def test_update_verification_missing_profile_hash(httpx_mock: HTTPXMock):
    # Generate the hash for the user
    user_name = generate_username()
    generate_hash_in_cache(user_name)

    # Mock httpx
    httpx_mock.add_response(
        url=generate_profile_url(user_name),
        status_code=200,
        data="random data that doesn't match the hash",
    )

    # Run the actual test
    data = {"user_name": user_name}
    response = client.get("/goon_auth/verification/update", params=data)
    unpacked = response.json()

    assert response.status_code == 200
    assert not unpacked["validated"]


def test_update_verification_profile_hash(httpx_mock: HTTPXMock):
    # Generate the hash for the user
    user_name = generate_username()
    hash = generate_hash_in_cache(user_name)
    profile = generate_profile_page(hash)

    # Mock httpx
    httpx_mock.add_response(
        url=generate_profile_url(user_name),
        status_code=200,
        data=profile,
    )

    data = {"user_name": user_name}
    response = client.get("/goon_auth/verification/update", params=data)
    unpacked = response.json()

    assert response.status_code == 200
    assert unpacked["validated"]
    assert unpacked["user_name"] == user_name

    # Static data pulled from the profile template
    assert unpacked["user_id"] == 164590
    assert unpacked["register_date"] == "2010-05-16T00:00:00"
