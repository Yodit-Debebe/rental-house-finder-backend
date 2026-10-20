from django.contrib import admin

from property_management.models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "city", "price", "landlord", "is_available", "created_at")
    list_filter = ("city", "is_available")
    search_fields = ("title", "address", "city")
