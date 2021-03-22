from pytest_httpx import HTTPXMock

from .base import client, generate_username, generate_profile_url


def test_full_auth(httpx_mock: HTTPXMock):
    user_name = generate_username()

    # Generate challenge
    data = {"user_name": user_name}
    response = client.post("/v1/generate_challenge", json=data)
    hash = response.json()["hash"]

    assert response.status_code == 200
    assert hash is not None

    # Mock httpx
    httpx_mock.add_response(
        url=generate_profile_url(user_name),
        status_code=200,
        data=f"there's a {hash} in here some where",
    )

    # Verify challenge
    url = f"/v1/verify_challenge?user_name={user_name}"
    response2 = client.get(url)
    assert response2.status_code == 200
    assert response2.json() == {"validated": True}
