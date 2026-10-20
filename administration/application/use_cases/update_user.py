from administration.application.commands import UpdateUserCommand
from administration.domain.entities import ManagedUser
from administration.domain.exceptions import (
    CannotModifySelf,
    InvalidRole,
    UserNotFound,
)
from administration.domain.repositories import UserAdminRepository
from administration.domain.value_objects import AdminUserRole


class UpdateUserUseCase:
    def __init__(self, repository: UserAdminRepository):
        self._repository = repository

    def execute(self, command: UpdateUserCommand) -> ManagedUser:
        if command.user_id == command.actor_id:
            raise CannotModifySelf("Administrators cannot modify their own account")

        user = self._repository.get(command.user_id)
        if user is None:
            raise UserNotFound(f"User {command.user_id} was not found")

        if command.role is not None:
            try:
                user.role = AdminUserRole(command.role)
            except ValueError:
                raise InvalidRole(f"'{command.role}' is not a valid role") from None

        if command.is_active is not None:
            user.is_active = command.is_active

        return self._repository.save(user)
