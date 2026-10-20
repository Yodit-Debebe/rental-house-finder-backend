from django.urls import path

from administration.interfaces.http.views import UserDetailView, UserListView

app_name = "administration"

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:user_id>/", UserDetailView.as_view(), name="user-detail"),
]
