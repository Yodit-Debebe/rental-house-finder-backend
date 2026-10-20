from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from property_management.application.commands import (
    CreatePropertyCommand,
    DeletePropertyCommand,
    DeletePropertyImageCommand,
    UpdatePropertyCommand,
    UploadPropertyImageCommand,
)
from property_management.application.queries import (
    GetPropertyQuery,
    ListLandlordPropertiesQuery,
)
from property_management.application.use_cases import (
    CreatePropertyUseCase,
    DeletePropertyImageUseCase,
    DeletePropertyUseCase,
    GetPropertyUseCase,
    ListAmenitiesUseCase,
    ListLandlordPropertiesUseCase,
    UpdatePropertyUseCase,
    UploadPropertyImageUseCase,
)
from property_management.domain.exceptions import (
    InvalidAmenity,
    InvalidProperty,
    NotPropertyOwner,
    PropertyImageNotFound,
    PropertyNotFound,
)
from property_management.infrastructure.persistence import (
    DjangoAmenityRepository,
    DjangoPropertyImageRepository,
    DjangoPropertyRepository,
)
from property_management.interfaces.http.permissions import IsLandlord
from property_management.interfaces.http.serializers import (
    CreatePropertySerializer,
    PropertyImageUploadSerializer,
    UpdatePropertySerializer,
    serialize_amenity,
    serialize_image,
    serialize_property,
)


def _properties() -> DjangoPropertyRepository:
    return DjangoPropertyRepository()


def _images() -> DjangoPropertyImageRepository:
    return DjangoPropertyImageRepository()


def _amenity_list():
    return ListAmenitiesUseCase(DjangoAmenityRepository()).execute()


def _error_response(exc: Exception) -> Response:
    if isinstance(exc, (PropertyNotFound, PropertyImageNotFound)):
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    if isinstance(exc, NotPropertyOwner):
        return Response(
            {"detail": "You do not own this property."},
            status=status.HTTP_403_FORBIDDEN,
        )
    return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class AmenityListView(APIView):
    permission_classes = [IsAuthenticated, IsLandlord]

    def get(self, request):
        return Response([serialize_amenity(item) for item in _amenity_list()])


class PropertyListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsLandlord]

    def get(self, request):
        properties = ListLandlordPropertiesUseCase(_properties()).execute(
            ListLandlordPropertiesQuery(landlord_id=request.user.id)
        )
        amenities = _amenity_list()
        images = _images()
        return Response(
            [
                serialize_property(
                    item,
                    amenities=amenities,
                    images=images.list_by_property(item.id),
                )
                for item in properties
            ]
        )

    def post(self, request):
        serializer = CreatePropertySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            property = CreatePropertyUseCase(_properties()).execute(
                CreatePropertyCommand(
                    landlord_id=request.user.id, **serializer.validated_data
                )
            )
        except (InvalidProperty, InvalidAmenity) as exc:
            return _error_response(exc)

        return Response(
            serialize_property(property, amenities=_amenity_list()),
            status=status.HTTP_201_CREATED,
        )


class PropertyDetailView(APIView):
    permission_classes = [IsAuthenticated, IsLandlord]

    def get(self, request, property_id: int):
        try:
            property = GetPropertyUseCase(_properties()).execute(
                GetPropertyQuery(
                    property_id=property_id, landlord_id=request.user.id
                )
            )
        except (PropertyNotFound, NotPropertyOwner) as exc:
            return _error_response(exc)
        return Response(
            serialize_property(
                property,
                amenities=_amenity_list(),
                images=_images().list_by_property(property.id),
            )
        )

    def patch(self, request, property_id: int):
        serializer = UpdatePropertySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            property = UpdatePropertyUseCase(_properties()).execute(
                UpdatePropertyCommand(
                    property_id=property_id,
                    landlord_id=request.user.id,
                    **serializer.validated_data,
                )
            )
        except (
            PropertyNotFound,
            NotPropertyOwner,
            InvalidProperty,
            InvalidAmenity,
        ) as exc:
            return _error_response(exc)
        return Response(
            serialize_property(
                property,
                amenities=_amenity_list(),
                images=_images().list_by_property(property.id),
            )
        )

    def delete(self, request, property_id: int):
        try:
            DeletePropertyUseCase(_properties()).execute(
                DeletePropertyCommand(
                    property_id=property_id, landlord_id=request.user.id
                )
            )
        except (PropertyNotFound, NotPropertyOwner) as exc:
            return _error_response(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PropertyImageUploadView(APIView):
    permission_classes = [IsAuthenticated, IsLandlord]

    def post(self, request, property_id: int):
        serializer = PropertyImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upload = serializer.validated_data["image"]

        try:
            image = UploadPropertyImageUseCase(
                _properties(), _images()
            ).execute(
                UploadPropertyImageCommand(
                    property_id=property_id,
                    landlord_id=request.user.id,
                    file_name=upload.name,
                    content=upload.read(),
                    caption=serializer.validated_data.get("caption", ""),
                    is_cover=serializer.validated_data.get("is_cover", False),
                )
            )
        except (PropertyNotFound, NotPropertyOwner) as exc:
            return _error_response(exc)

        return Response(serialize_image(image), status=status.HTTP_201_CREATED)


class PropertyImageDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsLandlord]

    def delete(self, request, property_id: int, image_id: int):
        try:
            DeletePropertyImageUseCase(_properties(), _images()).execute(
                DeletePropertyImageCommand(
                    property_id=property_id,
                    image_id=image_id,
                    landlord_id=request.user.id,
                )
            )
        except (PropertyNotFound, PropertyImageNotFound, NotPropertyOwner) as exc:
            return _error_response(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)
