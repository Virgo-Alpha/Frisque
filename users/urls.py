from django.urls import path
from .views import CustomLoginView, CustomLogoutView, SignUpView, UsersView
from django.contrib.auth import views as auth_views

urlpatterns = [

    path("users/", UsersView.as_view(), name="users"),
]
