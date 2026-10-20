from django.contrib.auth.hashers import check_password, make_password

from identity.application.ports import PasswordHasher


class DjangoPasswordHasher(PasswordHasher):
    """Implements the PasswordHasher port with Django's password hashers."""

    def hash(self, raw_password: str) -> str:
        return make_password(raw_password)

    def verify(self, raw_password: str, password_hash: str) -> bool:
        return check_password(raw_password, password_hash)
