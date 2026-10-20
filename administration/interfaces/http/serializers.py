from rest_framework import serializers

from administration.domain.entities import ManagedUser
from administration.domain.value_objects import AdminUserRole


class UpdateUserSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=[role.value for role in AdminUserRole], required=False
    )
    is_active = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Provide role and/or is_active.")
        return attrs


def serialize_user(user: ManagedUser) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
    }
