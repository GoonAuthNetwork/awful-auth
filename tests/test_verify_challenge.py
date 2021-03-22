from pytest_httpx import HTTPXMock

from .base import (
    client,
    generate_username,
    generate_profile_url,
    generate_hash_in_cache,
)


# Test requiring a username
def test_verify_challenge_require_username():
    url = "/v1/verify_challenge?user_name="
    response = client.get(url)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"limit_value": 3},
                "loc": ["query", "user_name"],
                "msg": "ensure this value has at least 3 characters",
                "type": "value_error.any_str.min_length",
            }
        ]
    }


def test_verify_challenge_managled_username():
    url = "/v1/verify_challenge?user_name=🤔🤔🤔🤔🤔"
    response = client.get(url)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"pattern": "^[\x00-\x7f]+$"},
                "loc": ["query", "user_name"],
                "msg": 'string does not match regex "^[\x00-\x7f]+$"',
                "type": "value_error.str.regex",
            }
        ]
    }


def test_verify_challenge_hash_not_found():
    user_name = generate_username()
    url = f"/v1/verify_challenge?user_name={user_name}"
    response = client.get(url)
    assert response.status_code == 404
    assert response.json() == {"detail": "Hash not found for user_name"}


def test_verify_challenge_missing_profile_hash(httpx_mock: HTTPXMock):
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
    url = f"/v1/verify_challenge?user_name={user_name}"
    response = client.get(url)
    assert response.status_code == 404
    assert response.json() == {"detail": "Hash not found in SA profile"}


def test_verify_challenge_profile_hash(httpx_mock: HTTPXMock):
    # Generate the hash for the user
    user_name = generate_username()
    hash = generate_hash_in_cache(user_name)

    # Mock httpx
    httpx_mock.add_response(
        url=generate_profile_url(user_name),
        status_code=200,
        data=f"there's a {hash} in here some where",
    )

    url = f"/v1/verify_challenge?user_name={user_name}"
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {"validated": True}
