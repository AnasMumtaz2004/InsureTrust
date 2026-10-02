def test_seeded_customer_login(client):
    response = client.post("/api/v1/auth/login/customer", json={
        "email": "customer@insuretrust.com",
        "password": "customer123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["role"] == "customer"

def test_seeded_staff_login(client):
    response = client.post("/api/v1/auth/login/staff", json={
        "email": "staff@insuretrust.com",
        "password": "staff123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["role"] == "staff"

def test_login_wrong_password(client):
    response = client.post("/api/v1/auth/login/customer", json={
        "email": "customer@insuretrust.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_register_forces_customer_role(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "hacker@insuretrust.com",
        "password": "password123",
        "full_name": "Hacker",
        "role": "admin"  # trying to inject admin
    })
    assert response.status_code == 200
    assert response.json()["role"] == "customer"

def test_create_staff_auth(client):
    # Get tokens
    customer_res = client.post("/api/v1/auth/login/customer", json={"email": "customer@insuretrust.com", "password": "customer123"})
    customer_token = customer_res.json()["access_token"]
    
    staff_res = client.post("/api/v1/auth/login/staff", json={"email": "staff@insuretrust.com", "password": "staff123"})
    staff_token = staff_res.json()["access_token"]

    # customer cannot create staff
    res = client.post("/api/v1/auth/create-staff", json={
        "email": "newstaff1@insuretrust.com", "password": "password123", "full_name": "S1", "role": "staff"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    assert res.status_code == 403

    # staff cannot create staff
    res = client.post("/api/v1/auth/create-staff", json={
        "email": "newstaff2@insuretrust.com", "password": "password123", "full_name": "S2", "role": "staff"
    }, headers={"Authorization": f"Bearer {staff_token}"})
    assert res.status_code == 403
