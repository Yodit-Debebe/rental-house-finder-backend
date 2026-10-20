from pathlib import Path

from django.core.files.base import ContentFile
from django.db import transaction

from property_management.domain.entities import PropertyImage
from property_management.domain.repositories import PropertyImageRepository
from property_management.models import PropertyImage as PropertyImageModel


class DjangoPropertyImageRepository(PropertyImageRepository):
    """Implements the PropertyImageRepository port with Django file storage."""

    def list_by_property(self, property_id: int) -> list[PropertyImage]:
        rows = PropertyImageModel.objects.filter(property_id=property_id).order_by(
            "-is_cover", "created_at"
        )
        return [self._to_domain(row) for row in rows]

    def get(self, image_id: int) -> PropertyImage | None:
        row = PropertyImageModel.objects.filter(pk=image_id).first()
        return self._to_domain(row) if row is not None else None

    def add(
        self,
        property_id: int,
        file_name: str,
        content: bytes,
        caption: str,
        is_cover: bool,
    ) -> PropertyImage:
        with transaction.atomic():
            has_images = PropertyImageModel.objects.filter(
                property_id=property_id
            ).exists()

            if is_cover:
                PropertyImageModel.objects.filter(
                    property_id=property_id, is_cover=True
                ).update(is_cover=False)
            else:
                # The first image of a property becomes its cover automatically.
                is_cover = not has_images

            row = PropertyImageModel(
                property_id=property_id,
                caption=caption.strip(),
                is_cover=is_cover,
            )
            # Path.name prevents a crafted filename from escaping the upload dir.
            row.image.save(Path(file_name).name, ContentFile(content), save=False)
            row.save()

        return self._to_domain(row)

    def delete(self, image_id: int) -> None:
        row = PropertyImageModel.objects.filter(pk=image_id).first()
        if row is not None:
            row.image.delete(save=False)
            row.delete()

    @staticmethod
    def _to_domain(row: PropertyImageModel) -> PropertyImage:
        return PropertyImage(
            id=row.pk,
            property_id=row.property_id,
            url=row.image.url,
            caption=row.caption,
            is_cover=row.is_cover,
        )
