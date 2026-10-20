from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from administration.application.commands import UpdateUserCommand
from administration.application.queries import GetUserQuery, ListUsersQuery
from administration.application.use_cases import (
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)
from administration.domain.exceptions import (
    CannotModifySelf,
    InvalidRole,
    UserNotFound,
)
from administration.domain.value_objects import UserFilters
from administration.infrastructure.persistence import DjangoUserAdminRepository
from administration.interfaces.http.permissions import IsPlatformAdmin
from administration.interfaces.http.serializers import (
    UpdateUserSerializer,
    serialize_user,
)


def _repository() -> DjangoUserAdminRepository:
    return DjangoUserAdminRepository()


def _error_response(exc: Exception) -> Response:
    if isinstance(exc, UserNotFound):
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


def _parse_is_active(raw: str | None) -> bool | None:
    if raw is None:
        return None
    if raw.lower() in ("1", "true", "yes"):
        return True
    if raw.lower() in ("0", "false", "no"):
        return False
    raise ValueError("is_active must be true or false")


class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        try:
            is_active = _parse_is_active(request.query_params.get("is_active"))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        filters = UserFilters(
            role=request.query_params.get("role") or None,
            is_active=is_active,
            search=request.query_params.get("search") or None,
        )
        users = ListUsersUseCase(_repository()).execute(
            ListUsersQuery(filters=filters)
        )
        return Response([serialize_user(user) for user in users])


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request, user_id: int):
        try:
            user = GetUserUseCase(_repository()).execute(
                GetUserQuery(user_id=user_id)
            )
        except UserNotFound as exc:
            return _error_response(exc)
        return Response(serialize_user(user))

    def patch(self, request, user_id: int):
        serializer = UpdateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = UpdateUserUseCase(_repository()).execute(
                UpdateUserCommand(
                    user_id=user_id,
                    actor_id=request.user.id,
                    **serializer.validated_data,
                )
            )
        except (UserNotFound, CannotModifySelf, InvalidRole) as exc:
            return _error_response(exc)
        return Response(serialize_user(user))
