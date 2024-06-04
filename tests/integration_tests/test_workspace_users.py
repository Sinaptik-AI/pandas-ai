import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from core.config import settings
from core.database.base import Base
from app.models import User, Workspace

# Setup test database and override get_db dependency
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[settings.get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def setup_database():
    # Setup test data
    db = TestingSessionLocal()
    user1 = User(email="user1@example.com")
    user2 = User(email="user2@example.com")
    workspace = Workspace(name="Test Workspace", users=[user1, user2])
    db.add(user1)
    db.add(user2)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    yield workspace.id
    # Teardown test data
    db.query(User).delete()
    db.query(Workspace).delete()
    db.commit()

def test_get_workspace_users(setup_database):
    workspace_id = setup_database
    response = client.get(f"/workspaces/{workspace_id}/users")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['email'] == "user1@example.com"
    assert response.json()[1]['email'] == "user2@example.com"

def test_get_workspace_users_non_existent_workspace():
    response = client.get("/workspaces/999/users")
    assert response.status_code == 404
