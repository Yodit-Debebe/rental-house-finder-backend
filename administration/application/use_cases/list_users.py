from administration.application.queries import ListUsersQuery
from administration.domain.entities import ManagedUser
from administration.domain.repositories import UserAdminRepository


class ListUsersUseCase:
    def __init__(self, repository: UserAdminRepository):
        self._repository = repository

    def execute(self, query: ListUsersQuery) -> list[ManagedUser]:
        return self._repository.list(query.filters)
