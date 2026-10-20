from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from identity.application.commands import (
    AuthenticateUserCommand,
    RegisterUserCommand,
)
from identity.application.exceptions import (
    EmailAlreadyRegistered,
    InvalidCredentials,
)
from identity.application.use_cases.authenticate_user import AuthenticateUserUseCase
from identity.application.use_cases.register_user import RegisterUserUseCase
from identity.domain.exceptions import InvalidEmail
from identity.domain.value_objects import Email
from identity.infrastructure.persistence import DjangoUserRepository
from identity.infrastructure.security import DRFTokenIssuer, DjangoPasswordHasher
from identity.interfaces.http.serializers import (
    LoginSerializer,
    RegisterUserSerializer,
    serialize_user,
)


def _register_use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(DjangoUserRepository(), DjangoPasswordHasher())


def _authenticate_use_case() -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        DjangoUserRepository(), DjangoPasswordHasher(), DRFTokenIssuer()
    )


class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = _register_use_case().execute(
                RegisterUserCommand(**serializer.validated_data)
            )
        except EmailAlreadyRegistered as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_409_CONFLICT
            )
        except InvalidEmail as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serialize_user(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = _authenticate_use_case().execute(
                AuthenticateUserCommand(**serializer.validated_data)
            )
        except InvalidCredentials as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED
            )

        return Response({"token": result.token, "user": serialize_user(result.user)})


class MeView(APIView):
    def get(self, request):
        # request.user is populated by DRF's TokenAuthentication.
        user = DjangoUserRepository().get_by_email(Email(request.user.email))
        return Response(serialize_user(user))
