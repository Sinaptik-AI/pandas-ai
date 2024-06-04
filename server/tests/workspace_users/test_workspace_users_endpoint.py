import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User, Workspace
from app.api.dependencies.database import get_db
from app.main import app

@pytest.mark.asyncio
async def test_get_workspace_users_success(async_client: AsyncClient, test_db: AsyncSession):
    # Setup test data
    async with test_db() as db:
        workspace = Workspace(name="Test Workspace")
        db.add(workspace)
        await db.commit()
        await db.refresh(workspace)

        user1 = User(email="user1@example.com", workspace_id=workspace.id)
        user2 = User(email="user2@example.com", workspace_id=workspace.id)
        db.add_all([user1, user2])
        await db.commit()

    response = await async_client.get(f"/api/v1/users/workspace_users/{workspace.id}")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['email'] == "user1@example.com"
    assert response.json()[1]['email'] == "user2@example.com"

@pytest.mark.asyncio
async def test_get_workspace_users_unauthorized(async_client: AsyncClient):
    response = await async_client.get("/api/v1/users/workspace_users/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_workspace_users_invalid_workspace_id(async_client: AsyncClient):
    response = await async_client.get("/api/v1/users/workspace_users/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_workspace_users_empty_list(async_client: AsyncClient, test_db: AsyncSession):
    # Setup test data
    async with test_db() as db:
        workspace = Workspace(name="Empty Workspace")
        db.add(workspace)
        await db.commit()
        await db.refresh(workspace)

    response = await async_client.get(f"/api/v1/users/workspace_users/{workspace.id}")
    assert response.status_code == 200
    assert response.json() == []
