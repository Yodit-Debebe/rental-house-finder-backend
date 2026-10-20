from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from property_management.application.commands import (
    CreatePropertyCommand,
    DeletePropertyCommand,
    UpdatePropertyCommand,
)
from property_management.application.queries import (
    GetPropertyQuery,
    ListLandlordPropertiesQuery,
)
from property_management.application.use_cases import (
    CreatePropertyUseCase,
    DeletePropertyUseCase,
    GetPropertyUseCase,
    ListLandlordPropertiesUseCase,
    UpdatePropertyUseCase,
)
from property_management.domain.exceptions import (
    InvalidProperty,
    NotPropertyOwner,
    PropertyNotFound,
)
from property_management.infrastructure.persistence import DjangoPropertyRepository
from property_management.interfaces.http.permissions import IsLandlord
from property_management.interfaces.http.serializers import (
    CreatePropertySerializer,
    UpdatePropertySerializer,
    serialize_property,
)


def _repository() -> DjangoPropertyRepository:
    return DjangoPropertyRepository()


def _error_response(exc: Exception) -> Response:
    if isinstance(exc, PropertyNotFound):
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    if isinstance(exc, NotPropertyOwner):
        return Response(
            {"detail": "You do not own this property."},
            status=status.HTTP_403_FORBIDDEN,
        )
    return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class PropertyListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsLandlord]

    def get(self, request):
        properties = ListLandlordPropertiesUseCase(_repository()).execute(
            ListLandlordPropertiesQuery(landlord_id=request.user.id)
        )
        return Response([serialize_property(item) for item in properties])

    def post(self, request):
        serializer = CreatePropertySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            property = CreatePropertyUseCase(_repository()).execute(
                CreatePropertyCommand(
                    landlord_id=request.user.id, **serializer.validated_data
                )
            )
        except InvalidProperty as exc:
            return _error_response(exc)

        return Response(serialize_property(property), status=status.HTTP_201_CREATED)


class PropertyDetailView(APIView):
    permission_classes = [IsAuthenticated, IsLandlord]

    def get(self, request, property_id: int):
        try:
            property = GetPropertyUseCase(_repository()).execute(
                GetPropertyQuery(
                    property_id=property_id, landlord_id=request.user.id
                )
            )
        except (PropertyNotFound, NotPropertyOwner) as exc:
            return _error_response(exc)
        return Response(serialize_property(property))

    def patch(self, request, property_id: int):
        serializer = UpdatePropertySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            property = UpdatePropertyUseCase(_repository()).execute(
                UpdatePropertyCommand(
                    property_id=property_id,
                    landlord_id=request.user.id,
                    **serializer.validated_data,
                )
            )
        except (PropertyNotFound, NotPropertyOwner, InvalidProperty) as exc:
            return _error_response(exc)
        return Response(serialize_property(property))

    def delete(self, request, property_id: int):
        try:
            DeletePropertyUseCase(_repository()).execute(
                DeletePropertyCommand(
                    property_id=property_id, landlord_id=request.user.id
                )
            )
        except (PropertyNotFound, NotPropertyOwner) as exc:
            return _error_response(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)
