from dataclasses import dataclass

from administration.domain.value_objects import UserFilters


@dataclass(frozen=True)
class ListUsersQuery:
    filters: UserFilters
