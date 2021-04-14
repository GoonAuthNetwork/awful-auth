from .base import client, generate_username


# Test mangled username, aka unicode
def test_generate_verification_mangled_username():
    data = {"user_name": "🤔🤔🤔🤔🤔"}
    response = client.get("/goon_auth/verification", params=data)
    unpacked = response.json()
    detail = unpacked["detail"][0]

    assert response.status_code == 422
    assert "user_name" in detail["loc"]
    assert "string does not match regex " in detail["msg"]


# Ensure we get a hash back when everything is "valid"
def test_generate_verification_hash():
    data = {"user_name": generate_username()}
    response = client.get("/goon_auth/verification", params=data)
    unpacked = response.json()

    assert response.status_code == 200
    assert unpacked["user_name"] == data["user_name"]
    assert unpacked["hash"] is not None


# Ensure we get the same hash back between requests with the same username
def test_generate_verification_duplicate_request():
    data = {"user_name": generate_username()}

    response = client.get("/goon_auth/verification", params=data)
    assert response.status_code == 200

    response2 = client.get("/goon_auth/verification", params=data)
    assert response2.status_code == 200

    assert response.json() == response2.json()
