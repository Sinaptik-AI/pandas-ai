import unittest
from unittest.mock import ANY, AsyncMock, MagicMock
from app.models import User
from app.repositories.user import UserRepository


class TestUserRepository(unittest.IsolatedAsyncioTestCase):
    async def test_get_by_email(self):
        session_mock = AsyncMock()
        repository = UserRepository(User, session_mock)
        repository._query = MagicMock()
        repository.filter = MagicMock()

        query_mock = MagicMock()
        repository._query.return_value = query_mock
        repository.filter.return_value = query_mock

        email = "test@example.com"
        session_mock._query.return_value.filter.return_value = query_mock
        query_mock.filter.return_value = query_mock

        await repository.get_by_email(email)

        repository._query.assert_called_once()
        query_mock.filter.assert_called_once()

    async def test_create_and_init_dummy_user(self):
        session_mock = AsyncMock()
        repository = UserRepository(User, session_mock)

        user = await repository.create_and_init_dummy_user()

        session_mock.add.assert_called()
        self.assertIsNotNone(user)
        self.assertIsInstance(user, User)
        self.assertTrue(user.verified)
        self.assertEqual(user.first_name, "pandasai")

    async def test_join_memberships(self):
        session_mock = AsyncMock()
        repository = UserRepository(User, session_mock)

        query_mock = AsyncMock()

        await repository._join_memberships(query_mock)

        query_mock.options.assert_called_once_with(ANY)


if __name__ == "__main__":
    unittest.main()
