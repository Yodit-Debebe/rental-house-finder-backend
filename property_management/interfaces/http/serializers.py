from rest_framework import serializers

from property_management.domain.entities import Property


class CreatePropertySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    address = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=100)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    bedrooms = serializers.IntegerField(min_value=0)
    bathrooms = serializers.IntegerField(min_value=0)
    is_available = serializers.BooleanField(default=True)


class UpdatePropertySerializer(serializers.Serializer):
    """All fields are optional: omitted fields keep their current value."""

    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(max_length=255, required=False)
    city = serializers.CharField(max_length=100, required=False)
    price = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=0, required=False
    )
    bedrooms = serializers.IntegerField(min_value=0, required=False)
    bathrooms = serializers.IntegerField(min_value=0, required=False)
    is_available = serializers.BooleanField(required=False)


def serialize_property(property: Property) -> dict:
    """Convert a domain Property into the API representation."""
    return {
        "id": property.id,
        "landlord_id": property.landlord_id,
        "title": property.title,
        "description": property.description,
        "address": property.address.street,
        "city": property.address.city,
        "price": str(property.price),
        "bedrooms": property.bedrooms,
        "bathrooms": property.bathrooms,
        "is_available": property.is_available,
    }
