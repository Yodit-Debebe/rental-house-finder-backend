from administration.application.queries import GetUserQuery
from administration.domain.entities import ManagedUser
from administration.domain.exceptions import UserNotFound
from administration.domain.repositories import UserAdminRepository


class GetUserUseCase:
    def __init__(self, repository: UserAdminRepository):
        self._repository = repository

    def execute(self, query: GetUserQuery) -> ManagedUser:
        user = self._repository.get(query.user_id)
        if user is None:
            raise UserNotFound(f"User {query.user_id} was not found")
        return user
