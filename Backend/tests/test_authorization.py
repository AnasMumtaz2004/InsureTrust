import pytest
from jose import jwt
from config import settings
from datetime import datetime, timedelta, timezone

def test_unauthenticated_access(client):
    protected_routes = [
        ("GET", "/api/v1/auth/me"),
        ("GET", "/api/v1/claims"),
        ("GET", "/api/v1/ops/cases/queue"),
        ("GET", "/api/v1/analytics/kpis"),
    ]

    for method, path in protected_routes:
        response = client.request(method, path)
        assert response.status_code == 401, (
            f"{method} {path} should be 401, got {response.status_code}"
        )

def test_invalid_and_expired_tokens(client):
    # Invalid token
    res = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not.a.real.token"})
    assert res.status_code == 401

    # Expired token
    now = datetime.now(timezone.utc)
    expired = now - timedelta(hours=1)
    payload = {"sub": "USR-CUSTOMER", "role": "customer", "iat": expired, "exp": expired}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401

def test_customer_cannot_access_ops_routes(client):
    # Get customer token
    login_res = client.post("/api/v1/auth/login/customer", json={"email": "customer@insuretrust.com", "password": "customer123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test ops routes
    assert client.get("/api/v1/ops/cases/queue", headers=headers).status_code == 403
    assert client.get("/api/v1/ops/cases/x/graph-state", headers=headers).status_code == 403
    assert client.get("/api/v1/analytics/kpis", headers=headers).status_code == 403

def test_staff_can_access_ops(client):
    # Get staff token
    login_res = client.post("/api/v1/auth/login/staff", json={"email": "staff@insuretrust.com", "password": "staff123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/v1/ops/cases/queue", headers=headers).status_code == 200
    assert client.get("/api/v1/analytics/kpis", headers=headers).status_code == 200

def test_cross_customer_access(client):
    # Create a second customer
    client.post("/api/v1/auth/register", json={"email": "cust2@insuretrust.com", "password": "password123", "full_name": "Cust 2"})
    login_res2 = client.post("/api/v1/auth/login/customer", json={"email": "cust2@insuretrust.com", "password": "password123"})
    token2 = login_res2.json()["access_token"]
    
    # Try to access first customer's demo claim
    res = client.get("/api/v1/claims/CLM-DEMO-001", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 404

def test_spoofed_claimant_id(client):
    login_res = client.post("/api/v1/auth/login/customer", json={"email": "customer@insuretrust.com", "password": "customer123"})
    token = login_res.json()["access_token"]
    user_id = login_res.json()["user_id"]

    res = client.post("/api/v1/claims/submit", json={
        "policy_number": "POL-1",
        "claimant_id": "SPOOFED-ID",
        "incident_date": "2026-01-01",
        "claimed_amount": 100,
        "diagnosis_codes": ["M54.5"],
        "description": "test"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    assert res.json()["claimant_id"] == user_id
