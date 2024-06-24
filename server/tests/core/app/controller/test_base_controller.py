import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from core.database import Base
from core.exceptions import NotFoundException
from core.repository import BaseRepository
from core.controller import BaseController


class MockModel(Base):
    __tablename__ = "mock_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)  # Add more attributes as needed


class MockSchema(BaseModel):
    name: str
    age: int


class TestBaseController:
    @pytest.fixture
    def mock_repository(self):
        return Mock(spec=BaseRepository)

    @pytest.fixture
    def base_controller(self, mock_repository):
        return BaseController(MockModel, mock_repository)

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, base_controller, mock_repository):
        mock_instance = MockModel()
        mock_repository.get_by = AsyncMock(return_value=mock_instance)

        result = await base_controller.get_by_id(1)
        assert result == mock_instance
        mock_repository.get_by.assert_called_once_with(
            field="id", value=1, join_=None, unique=True
        )

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, base_controller, mock_repository):
        mock_repository.get_by = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException) as exc:
            await base_controller.get_by_id(1)

        assert str(exc.value) == "Mock_Table with id: 1 does not exist"

    @pytest.mark.asyncio
    async def test_get_by_uuid_found(self, base_controller, mock_repository):
        mock_instance = MockModel()
        mock_repository.get_by = AsyncMock(return_value=mock_instance)

        uuid = UUID("12345678123456781234567812345678")
        result = await base_controller.get_by_uuid(uuid)
        assert result == mock_instance
        mock_repository.get_by.assert_called_once_with(
            field="uuid", value=uuid, join_=None, unique=True
        )

    @pytest.mark.asyncio
    async def test_get_by_uuid_not_found(self, base_controller, mock_repository):
        mock_repository.get_by = AsyncMock(return_value=None)

        uuid = UUID("12345678123456781234567812345678")
        with pytest.raises(NotFoundException) as exc:
            await base_controller.get_by_uuid(uuid)

        assert (
            str(exc.value)
            == "Mock_Table with id: 12345678-1234-5678-1234-567812345678 does not exist"
        )

    @pytest.mark.asyncio
    async def test_get_all(self, base_controller, mock_repository):
        mock_instance = MockModel()
        mock_repository.get_all = AsyncMock(return_value=[mock_instance])

        result = await base_controller.get_all(skip=0, limit=10)
        assert result == [mock_instance]
        mock_repository.get_all.assert_called_once_with(0, 10, None)

    @pytest.mark.asyncio
    @patch(
        "core.controller.base.Transactional",
        lambda *args, **kwargs: lambda func: func,
    )
    @patch("core.database.session.session_context", MagicMock())
    async def test_create(self, base_controller, mock_repository):
        attributes = {"name": "test"}
        mock_instance = MockModel()
        mock_repository.create = AsyncMock(return_value=mock_instance)

        result = await base_controller.create(attributes)
        assert result == mock_instance
        mock_repository.create.assert_called_once_with(attributes)

    @pytest.mark.asyncio
    @patch(
        "core.controller.base.Transactional",
        lambda *args, **kwargs: lambda func: func,
    )
    @patch("core.database.session.session_context", MagicMock())
    async def test_delete_success(self, base_controller, mock_repository):
        mock_model = MockModel()
        mock_repository.delete.return_value = True

        result = await base_controller.delete(mock_model)

        mock_repository.delete.assert_called_once_with(mock_model)
        assert result is True

    @pytest.mark.asyncio
    @patch(
        "core.controller.base.Transactional",
        lambda *args, **kwargs: lambda func: func,
    )
    @patch("core.database.session.session_context", MagicMock())
    async def test_delete_failure(self, base_controller, mock_repository):
        mock_model = MockModel()
        mock_repository.delete.return_value = False

        result = await base_controller.delete(mock_model)

        mock_repository.delete.assert_called_once_with(mock_model)
        assert result is False

    def test_extract_attributes_from_schema(self):
        schema = MockSchema(name="test", age=30)
        result = BaseController.extract_attributes_from_schema(schema)
        assert result == {"name": "test", "age": 30}

    def test_extract_attributes_from_schema_with_excludes(self):
        schema = MockSchema(name="test", age=30)
        result = BaseController.extract_attributes_from_schema(
            schema, excludes={"name"}
        )
        assert result == {"age": 30}

    def test_extract_attributes_from_schema_with_empty_excludes(self):
        schema = MockSchema(name="test", age=30)
        result = BaseController.extract_attributes_from_schema(schema, excludes=set())
        assert result == {"name": "test", "age": 30}

    def test_extract_attributes_from_schema_with_unset_values(self):
        class MockSchemaWithOptional(BaseModel):
            name: str
            age: int = None
            address: str = None

        schema = MockSchemaWithOptional(name="test")
        result = BaseController.extract_attributes_from_schema(
            schema, excludes={"address"}
        )
        assert result == {"name": "test"}
