import pytest
from unittest.mock import AsyncMock, patch
from core.database.transactional import Transactional, Propagation


async def dummy_function():
    return "dummy"


async def exception_function():
    raise ValueError("Error")


class TestTransactionalDecorator:
    @pytest.mark.asyncio
    @patch("core.database.transactional.session", new_callable=AsyncMock)
    async def test_transactional_required_success(self, mock_session):
        mock_session_instance = AsyncMock()
        mock_session_instance.begin = AsyncMock()
        mock_session_instance.commit = AsyncMock()
        mock_session_instance.rollback = AsyncMock()
        mock_session.return_value = mock_session_instance

        decorator = Transactional(propagation=Propagation.REQUIRED)
        decorated_function = decorator(dummy_function)
        result = await decorated_function()

        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_not_called()
        assert result == "dummy"

    @pytest.mark.asyncio
    @patch("core.database.transactional.session", new_callable=AsyncMock)
    async def test_transactional_required_failure(self, mock_session):
        mock_session_instance = AsyncMock()
        mock_session_instance.begin = AsyncMock()
        mock_session_instance.commit = AsyncMock()
        mock_session_instance.rollback = AsyncMock()
        mock_session.return_value = mock_session_instance

        decorator = Transactional(propagation=Propagation.REQUIRED)
        decorated_function = decorator(exception_function)

        with pytest.raises(ValueError):
            await decorated_function()

        mock_session.begin.assert_not_called()
        mock_session.commit.assert_not_called()
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    @patch("core.database.transactional.session", new_callable=AsyncMock)
    async def test_transactional_required_new_success(self, mock_session):
        mock_session_instance = AsyncMock()
        mock_session_instance.begin = AsyncMock()
        mock_session_instance.commit = AsyncMock()
        mock_session_instance.rollback = AsyncMock()
        mock_session.return_value = mock_session_instance

        decorator = Transactional(propagation=Propagation.REQUIRED_NEW)
        decorated_function = decorator(dummy_function)
        result = await decorated_function()

        mock_session.begin.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_not_called()
        assert result == "dummy"

    @pytest.mark.asyncio
    @patch("core.database.transactional.session", new_callable=AsyncMock)
    async def test_transactional_required_new_failure(self, mock_session):
        mock_session_instance = AsyncMock()
        mock_session_instance.begin = AsyncMock()
        mock_session_instance.commit = AsyncMock()
        mock_session_instance.rollback = AsyncMock()
        mock_session.return_value = mock_session_instance

        decorator = Transactional(propagation=Propagation.REQUIRED_NEW)
        decorated_function = decorator(exception_function)

        with pytest.raises(ValueError):
            await decorated_function()

        mock_session.begin.assert_called_once()
        mock_session.commit.assert_not_called()
        mock_session.rollback.assert_called_once()
