import pytest

@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "test123",
        "name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login_user(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "pass123",
        "name": "Login User"
    })

    response = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "pass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login@example.com"

@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "email": "wrong@example.com",
        "password": "correct",
        "name": "Wrong Test"
    })

    response = await client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrong"
    })
    assert response.status_code == 401
