import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test environment before any app imports
os.environ["SECRET_KEY"] = "super_secret_test_key_that_is_long_enough_for_hs256_alg"
os.environ["DATABASE_URL"] = "sqlite:///./test_insuretrust.db"

# Now import the app and DB stuff
from api.main import app
from database.database import Base, engine, SessionLocal, seed_demo_data

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_insuretrust.db"):
        os.remove("./test_insuretrust.db")

@pytest.fixture(scope="module")
def client():
    # Use TestClient as a context manager to trigger lifespan events
    with TestClient(app) as c:
        yield c
