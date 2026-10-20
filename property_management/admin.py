from django.contrib import admin

from property_management.models import Amenity, Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 0


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "city", "price", "landlord", "is_available", "created_at")
    list_filter = ("city", "is_available", "amenities")
    search_fields = ("title", "address", "city")
    filter_horizontal = ("amenities",)
    inlines = [PropertyImageInline]


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
