from unittest import TestCase

from administration.application.commands import UpdateUserCommand
from administration.application.queries import GetUserQuery, ListUsersQuery
from administration.application.use_cases import (
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)
from administration.domain.entities import ManagedUser
from administration.domain.exceptions import (
    CannotModifySelf,
    InvalidRole,
    UserNotFound,
)
from administration.domain.repositories import UserAdminRepository
from administration.domain.value_objects import AdminUserRole, UserFilters


class InMemoryUserAdminRepository(UserAdminRepository):
    def __init__(self, users: list[ManagedUser] | None = None):
        self._users = {user.id: user for user in users or []}

    def list(self, filters: UserFilters) -> list[ManagedUser]:
        users = list(self._users.values())
        if filters.role is not None:
            users = [user for user in users if user.role.value == filters.role]
        if filters.is_active is not None:
            users = [
                user for user in users if user.is_active == filters.is_active
            ]
        if filters.search:
            term = filters.search.strip().lower()
            users = [
                user
                for user in users
                if term in user.email.lower() or term in user.full_name.lower()
            ]
        return users

    def get(self, user_id: int) -> ManagedUser | None:
        return self._users.get(user_id)

    def save(self, user: ManagedUser) -> ManagedUser:
        self._users[user.id] = user
        return user


def make_user(
    user_id: int = 1,
    email: str = "user@example.com",
    full_name: str = "Test User",
    role: AdminUserRole = AdminUserRole.TENANT,
    is_active: bool = True,
    is_staff: bool = False,
) -> ManagedUser:
    return ManagedUser(
        id=user_id,
        email=email,
        full_name=full_name,
        role=role,
        is_active=is_active,
        is_staff=is_staff,
    )


class ListUsersUseCaseTests(TestCase):
    def setUp(self):
        self.repository = InMemoryUserAdminRepository(
            [
                make_user(1, "a@example.com", "Alice", AdminUserRole.LANDLORD),
                make_user(2, "b@example.com", "Bob", AdminUserRole.TENANT),
                make_user(
                    3,
                    "c@example.com",
                    "Carol",
                    AdminUserRole.TENANT,
                    is_active=False,
                ),
            ]
        )
        self.use_case = ListUsersUseCase(self.repository)

    def execute(self, **filters):
        return self.use_case.execute(ListUsersQuery(filters=UserFilters(**filters)))

    def test_lists_everyone_without_filters(self):
        self.assertEqual(len(self.execute()), 3)

    def test_filters_by_role(self):
        users = self.execute(role="tenant")

        self.assertEqual([user.full_name for user in users], ["Bob", "Carol"])

    def test_filters_by_active_status(self):
        users = self.execute(is_active=False)

        self.assertEqual([user.full_name for user in users], ["Carol"])

    def test_searches_email_and_name(self):
        self.assertEqual([user.full_name for user in self.execute(search="alice")], ["Alice"])
        self.assertEqual(
            [user.full_name for user in self.execute(search="example.com")],
            ["Alice", "Bob", "Carol"],
        )


class GetUserUseCaseTests(TestCase):
    def setUp(self):
        self.repository = InMemoryUserAdminRepository([make_user(1)])
        self.use_case = GetUserUseCase(self.repository)

    def test_returns_user(self):
        self.assertEqual(
            self.use_case.execute(GetUserQuery(user_id=1)).email, "user@example.com"
        )

    def test_missing_user_raises(self):
        with self.assertRaises(UserNotFound):
            self.use_case.execute(GetUserQuery(user_id=999))


class UpdateUserUseCaseTests(TestCase):
    def setUp(self):
        self.repository = InMemoryUserAdminRepository([make_user(1)])
        self.use_case = UpdateUserUseCase(self.repository)

    def execute(self, **overrides):
        values = {"user_id": 1, "actor_id": 99}
        values.update(overrides)
        return self.use_case.execute(UpdateUserCommand(**values))

    def test_changes_role(self):
        user = self.execute(role="landlord")

        self.assertEqual(user.role, AdminUserRole.LANDLORD)
        self.assertEqual(self.repository.get(1).role, AdminUserRole.LANDLORD)

    def test_deactivates_user(self):
        user = self.execute(is_active=False)

        self.assertFalse(user.is_active)
        self.assertFalse(self.repository.get(1).is_active)

    def test_rejects_invalid_role(self):
        with self.assertRaises(InvalidRole):
            self.execute(role="superhero")

    def test_cannot_modify_self(self):
        with self.assertRaises(CannotModifySelf):
            self.execute(user_id=5, actor_id=5, is_active=False)

    def test_missing_user_raises(self):
        with self.assertRaises(UserNotFound):
            self.execute(user_id=999)
