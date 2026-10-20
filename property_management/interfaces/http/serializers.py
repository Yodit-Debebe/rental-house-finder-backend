from rest_framework import serializers

from property_management.domain.entities import Amenity, Property, PropertyImage


class CreatePropertySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    address = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=100)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    bedrooms = serializers.IntegerField(min_value=0)
    bathrooms = serializers.IntegerField(min_value=0)
    is_available = serializers.BooleanField(default=True)
    amenity_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=list,
    )


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
    amenity_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False
    )


class PropertyImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
    caption = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    is_cover = serializers.BooleanField(default=False)


def serialize_amenity(amenity: Amenity) -> dict:
    return {"id": amenity.id, "name": amenity.name}


def serialize_image(image: PropertyImage) -> dict:
    return {
        "id": image.id,
        "url": image.url,
        "caption": image.caption,
        "is_cover": image.is_cover,
    }


def serialize_property(
    property: Property,
    amenities: list[Amenity] | None = None,
    images: list[PropertyImage] | None = None,
) -> dict:
    """Convert a domain Property into the API representation."""
    amenities_by_id = {amenity.id: amenity for amenity in amenities or []}
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
        "amenities": [
            serialize_amenity(amenities_by_id[amenity_id])
            for amenity_id in property.amenity_ids
            if amenity_id in amenities_by_id
        ],
        "images": [serialize_image(image) for image in images or []],
    }
