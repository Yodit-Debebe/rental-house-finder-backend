from django.db import IntegrityError, transaction

from identity.application.exceptions import EmailAlreadyRegistered
from identity.application.ports import UserRepository
from identity.domain.entities import User
from identity.domain.value_objects import Email, Role
from identity.models import User as UserModel


class DjangoUserRepository(UserRepository):
    """Implements the UserRepository port with the Django ORM."""

    def get_by_email(self, email: Email) -> User | None:
        row = UserModel.objects.filter(email=email.value).first()
        return self._to_domain(row) if row is not None else None

    def add(self, user: User) -> User:
        try:
            with transaction.atomic():
                row = UserModel.objects.create(
                    email=user.email.value,
                    full_name=user.full_name,
                    role=user.role.value,
                    password=user.password_hash,
                )
        except IntegrityError:
            # Unique constraint on email: the database is the final authority.
            raise EmailAlreadyRegistered(str(user.email)) from None
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: UserModel) -> User:
        return User(
            id=row.pk,
            email=Email(row.email),
            full_name=row.full_name,
            role=Role(row.role),
            password_hash=row.password,
        )
