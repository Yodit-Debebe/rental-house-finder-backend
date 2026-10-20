from django.urls import path

from property_management.interfaces.http.views import (
    PropertyDetailView,
    PropertyListCreateView,
)

app_name = "property_management"

urlpatterns = [
    path("", PropertyListCreateView.as_view(), name="list-create"),
    path("<int:property_id>/", PropertyDetailView.as_view(), name="detail"),
]
