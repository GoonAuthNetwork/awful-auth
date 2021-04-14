from pytest_httpx import HTTPXMock

from .base import client, generate_username, generate_profile_page, generate_profile_url


def test_full_auth(httpx_mock: HTTPXMock):
    user_name = generate_username()

    # Generate challenge
    data = {"user_name": user_name}
    response = client.get("/goon_auth/verification", params=data)
    hash = response.json()["hash"]

    assert response.status_code == 200
    assert hash is not None

    # Mock httpx
    profile = generate_profile_page(hash)

    httpx_mock.add_response(
        url=generate_profile_url(user_name),
        status_code=200,
        data=profile,
    )

    # Verify challenge
    response = client.get("/goon_auth/verification/update", params=data)
    unpacked = response.json()

    assert response.status_code == 200
    assert unpacked["validated"]
    assert unpacked["user_name"] == user_name

    # Static data pulled from the profile template
    assert unpacked["user_id"] == 164590
    assert unpacked["register_date"] == "2010-05-16T00:00:00"
