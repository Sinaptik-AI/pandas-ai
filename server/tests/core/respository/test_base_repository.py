import pytest
from unittest.mock import ANY, AsyncMock, MagicMock, Mock
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database import Base
from core.repository.base import BaseRepository


# Define a mock model class that inherits from Base
class MockModel(Base):
    __tablename__ = "mock_table_base"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)  # Add more attributes as needed


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def base_repository(mock_session):
    return BaseRepository(model=MockModel, db_session=mock_session)


class TestBaseRepository:
    @pytest.mark.asyncio
    async def test_create_with_attributes(self, base_repository, mock_session):
        attributes = {"id": 1, "name": "Test"}

        result = await base_repository.create(attributes)

        # Assert that the session's add method was called with the created model
        mock_session.add.assert_called_once()

        # Verify that the model is correctly created with the given attributes
        assert result.id == attributes["id"]
        assert result.name == attributes["name"]

    @pytest.mark.asyncio
    async def test_create_without_attributes(self, base_repository, mock_session):
        result = await base_repository.create()

        # Assert that the session's add method was called with the created model
        mock_session.add.assert_called_once()

        # Verify that the model is correctly created with default attributes
        assert result.id is None
        assert result.name is None

    @pytest.mark.asyncio
    async def test_get_all(self, base_repository, mock_session):
        mock_instance = MockModel(id=1, name="Test")
        mock_query_result = [mock_instance]

        # Mock the return value of session.scalars().all()
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=mock_query_result)
        mock_session.scalars.return_value = mock_scalars

        # Mock the query method to return a Select object
        base_repository._query = Mock(return_value=select(MockModel))

        # Mock _all and _all_unique methods
        base_repository._all = AsyncMock(return_value=mock_query_result)
        base_repository._all_unique = AsyncMock(return_value=mock_query_result)

        # Test with join_ being None
        result = await base_repository.get_all()

        assert result == mock_query_result
        base_repository._query.assert_called_once_with(None)
        base_repository._all.assert_called_once_with(ANY)
        base_repository._all_unique.assert_not_called()

        # Reset mocks for the next test case
        base_repository._query.reset_mock()
        base_repository._all.reset_mock()
        base_repository._all_unique.reset_mock()

        # Test with join_ not being None
        join_ = {"some_relation"}
        result = await base_repository.get_all(join_=join_)

        assert result == mock_query_result
        base_repository._query.assert_called_once_with(join_)
        base_repository._all.assert_not_called()
        base_repository._all_unique.assert_called_once_with(ANY)

    @pytest.mark.asyncio
    async def test_get_by_id(self, base_repository, mock_session):
        mock_instance = MockModel(id=1, name="Test")
        mock_query_result = MagicMock()
        mock_query_result.scalars().first.return_value = mock_instance

        mock_session.execute.return_value = mock_query_result

        result = await base_repository.get_by_id(1)

        # Compare the query executed with the expected query
        executed_query = mock_session.execute.call_args[0][0]
        expected_query = select(MockModel).filter_by(id=1)
        assert str(executed_query) == str(expected_query)

        assert result == mock_instance
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete(self, base_repository, mock_session):
        mock_instance = MockModel(id=1, name="Test")

        await base_repository.delete(mock_instance)

        mock_session.delete.assert_called_once_with(mock_instance)

    def test_query_without_join_and_order(self, base_repository):
        query = base_repository._query()

        expected_query = select(MockModel)
        assert str(query) == str(expected_query)

    def test_query_with_join(self, base_repository):
        # Mock the _maybe_join method to simulate a join
        base_repository._maybe_join = Mock(return_value="joined_query")
        query = base_repository._query(join_={"relation"})

        base_repository._maybe_join.assert_called_once_with(ANY, {"relation"})
        assert query == "joined_query"

    def test_query_with_order(self, base_repository):
        # Mock the _maybe_ordered method to simulate ordering
        base_repository._maybe_ordered = Mock(return_value="ordered_query")
        query = base_repository._query(order_={"asc": ["name"]})

        base_repository._maybe_ordered.assert_called_once_with(ANY, {"asc": ["name"]})
        assert query == "ordered_query"

    def test_query_with_join_and_order(self, base_repository):
        # Mock the _maybe_join and _maybe_ordered methods to simulate both join and ordering
        base_repository._maybe_join = Mock(return_value="joined_query")
        base_repository._maybe_ordered = Mock(return_value="ordered_joined_query")
        query = base_repository._query(join_={"relation"}, order_={"asc": ["name"]})

        base_repository._maybe_join.assert_called_once_with(ANY, {"relation"})
        base_repository._maybe_ordered.assert_called_once_with(
            "joined_query", {"asc": ["name"]}
        )
        assert query == "ordered_joined_query"


if __name__ == "__main__":
    pytest.main()
