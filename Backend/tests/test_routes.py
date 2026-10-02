import os
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from api.main import app
from database.models import Claim
from database.database import get_db

client = TestClient(app)

def test_cors_disallowed_origin():
    response = client.get("/", headers={"Origin": "http://evil.com"})
    assert "access-control-allow-origin" not in response.headers

def test_document_upload_success(monkeypatch, tmp_path):
    # Mock settings
    import config
    monkeypatch.setattr(config.settings.uploads, "dir", str(tmp_path))
    
    # Needs a mock DB and Claim for the auth and claim access dependencies
    # We can bypass auth for tests, but let's override dependencies
    from api.deps import get_current_user, assert_claim_access
    from database.models import User
    
    def override_get_user():
        return User(id="USR-TEST", role="staff", full_name="Test Staff", email="teststaff@example.com", hashed_password="x")
        
    def override_assert_access(user, claim):
        pass
        
    app.dependency_overrides[get_current_user] = override_get_user
    app.dependency_overrides[assert_claim_access] = override_assert_access
    
    class MockClaim:
        def __init__(self, id):
            self.id = id
            self.claim_number = "TEST-123"
            self.claimant_id = "USR-TEST"
            
    # Mock DB query
    class MockQuery:
        def filter(self, *args):
            return self
        def first(self):
            return MockClaim("CLM-TEST")
            
    class MockDB:
        def query(self, *args):
            return MockQuery()
        def add(self, *args):
            pass
        def commit(self, *args):
            pass
        def refresh(self, *args):
            args[0].uploaded_at = datetime.utcnow()
            
    def override_get_db():
        yield MockDB()
        
    app.dependency_overrides[get_db] = override_get_db

    # Valid PDF
    response = client.post(
        "/api/v1/documents/upload",
        data={"claim_id": "CLM-TEST", "document_type": "MEDICAL_BILL"},
        files={"file": ("test.pdf", b"pdf content", "application/pdf")}
    )
    assert response.status_code == 200
    assert response.json()["processed_status"] == "UPLOADED"
    
    # Path Traversal filename
    response = client.post(
        "/api/v1/documents/upload",
        data={"claim_id": "CLM-TEST", "document_type": "MEDICAL_BILL"},
        files={"file": ("../../evil.pdf", b"pdf content", "application/pdf")}
    )
    assert response.status_code == 200
    doc_name = response.json()["document_name"]
    assert doc_name == "evil.pdf"
    assert ".." not in doc_name
    
    # Invalid extension / type
    response = client.post(
        "/api/v1/documents/upload",
        data={"claim_id": "CLM-TEST", "document_type": "MEDICAL_BILL"},
        files={"file": ("test.exe", b"exe content", "application/x-msdownload")}
    )
    assert response.status_code == 415

    # Oversize file
    import io
    # Create a 11MB file in memory
    # To avoid huge memory usage, we just use a generator or large bytes
    # Alternatively we can mock settings max_mb to 0 for this test
    monkeypatch.setattr(config.settings.uploads, "max_mb", 0)
    response = client.post(
        "/api/v1/documents/upload",
        data={"claim_id": "CLM-TEST", "document_type": "MEDICAL_BILL"},
        files={"file": ("large.pdf", b"x" * (1024), "application/pdf")}
    )
    assert response.status_code == 413
