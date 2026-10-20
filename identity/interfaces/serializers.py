from rest_framework import serializers

from identity.domain.entities import User
from identity.domain.value_objects import Role


class RegisterUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=[role.value for role in Role],
        default=Role.TENANT.value,
    )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


def serialize_user(user: User) -> dict:
    """Convert a domain User into the API representation (never the password)."""
    return {
        "id": user.id,
        "email": user.email.value,
        "full_name": user.full_name,
        "role": user.role.value,
    }
