from django.urls import path

from identity.interfaces.views import LoginView, MeView, RegisterUserView

app_name = "identity"

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
]
