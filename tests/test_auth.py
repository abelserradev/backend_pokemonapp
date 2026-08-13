def test_should_register_and_login_json_with_valid_credentials(client, unique_email):
    password = "secret123"
    register_response = client.post(
        "/api/register",
        json={"email": unique_email, "password": password},
    )
    assert register_response.status_code == 200
    assert "user" in register_response.json()

    login_response = client.post(
        "/api/login/json",
        json={"email": unique_email, "password": password},
    )
    assert login_response.status_code == 200
    payload = login_response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["user"]["email"] == unique_email


def test_should_return_401_when_login_json_credentials_are_wrong(client, unique_email):
    client.post(
        "/api/register",
        json={"email": unique_email, "password": "secret123"},
    )
    response = client.post(
        "/api/login/json",
        json={"email": unique_email, "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales incorrectas"
