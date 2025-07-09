from fastapi.testclient import TestClient
from app.main import app
from app.models.user import UserType

client = TestClient(app)

def test_register_and_login():
    # Register a new user
    response = client.post("/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpass",
        "type": UserType.ESTUDIANTE.value
    })
    assert response.status_code == 200
    # Login with the new user
    response = client.post("/token", data={
        "username": "test@example.com",
        "password": "testpass"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    # Get current user
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
