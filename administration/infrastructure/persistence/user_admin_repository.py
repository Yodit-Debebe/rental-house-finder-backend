from django.db.models import Q

from administration.domain.entities import ManagedUser
from administration.domain.repositories import UserAdminRepository
from administration.domain.value_objects import AdminUserRole, UserFilters
from identity.models import User as UserModel


class DjangoUserAdminRepository(UserAdminRepository):
    """Implements the UserAdminRepository port over the identity user table."""

    def list(self, filters: UserFilters) -> list[ManagedUser]:
        rows = UserModel.objects.all().order_by("id")

        if filters.role is not None:
            rows = rows.filter(role=filters.role)
        if filters.is_active is not None:
            rows = rows.filter(is_active=filters.is_active)
        if filters.search:
            term = filters.search.strip()
            if term:
                rows = rows.filter(
                    Q(email__icontains=term) | Q(full_name__icontains=term)
                )

        return [self._to_domain(row) for row in rows]

    def get(self, user_id: int) -> ManagedUser | None:
        row = UserModel.objects.filter(pk=user_id).first()
        return self._to_domain(row) if row is not None else None

    def save(self, user: ManagedUser) -> ManagedUser:
        if user.id is None:
            raise ValueError("Cannot save a user without an id")

        UserModel.objects.filter(pk=user.id).update(
            role=user.role.value,
            is_active=user.is_active,
        )
        return self.get(user.id)

    @staticmethod
    def _to_domain(row: UserModel) -> ManagedUser:
        return ManagedUser(
            id=row.pk,
            email=row.email,
            full_name=row.full_name,
            role=AdminUserRole(row.role),
            is_active=row.is_active,
            is_staff=row.is_staff,
        )
