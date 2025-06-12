from django.urls import path
from .views import CustomLoginView, CustomLogoutView, SignUpView, UsersView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("users/", UsersView.as_view(), name="users"),
]
