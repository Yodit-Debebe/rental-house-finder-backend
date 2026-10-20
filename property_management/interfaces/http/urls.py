from django.urls import path

from property_management.interfaces.http.views import (
    AmenityListView,
    PropertyDetailView,
    PropertyImageDeleteView,
    PropertyImageUploadView,
    PropertyListCreateView,
)

app_name = "property_management"

urlpatterns = [
    path("", PropertyListCreateView.as_view(), name="list-create"),
    path("amenities/", AmenityListView.as_view(), name="amenities"),
    path(
        "<int:property_id>/images/",
        PropertyImageUploadView.as_view(),
        name="image-upload",
    ),
    path(
        "<int:property_id>/images/<int:image_id>/",
        PropertyImageDeleteView.as_view(),
        name="image-delete",
    ),
    path("<int:property_id>/", PropertyDetailView.as_view(), name="detail"),
]
