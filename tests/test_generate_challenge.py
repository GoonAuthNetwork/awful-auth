from .base import client, generate_username


# Test requiring a username
def test_generate_challenge_require_username():
    data = {}
    response = client.post("/v1/generate_challenge", json=data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "user_name"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


# Test mangled username, aka unicode
def test_generate_challenge_mangled_username():
    data = {"user_name": "🤔🤔🤔🤔🤔"}
    response = client.post("/v1/generate_challenge", json=data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"pattern": "^[\x00-\x7f]+$"},
                "loc": ["body", "user_name"],
                "msg": 'string does not match regex "^[\x00-\x7f]+$"',
                "type": "value_error.str.regex",
            }
        ]
    }


# Ensure we get a hash back when everything is "valid"
def test_generate_challenge_hash():
    data = {"user_name": generate_username()}
    response = client.post("/v1/generate_challenge", json=data)
    assert response.status_code == 200
    assert response.json()["hash"] is not None


# Ensure we get the same hash back between requests with the same username
def test_generate_challenge_duplicate_request():
    data = {"user_name": generate_username()}

    response = client.post("/v1/generate_challenge", json=data)
    assert response.status_code == 200

    response2 = client.post("/v1/generate_challenge", json=data)
    assert response2.status_code == 200

    assert response.json() == response2.json()
