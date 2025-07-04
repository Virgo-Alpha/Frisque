"""
URL configuration for frisque_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views as User_views
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', User_views.CustomLoginView.as_view(), name='login'),
    path('logout/', User_views.CustomLogoutView.as_view(), name='logout'),
    path('users/', User_views.UsersView.as_view(), name='user'),
    path('signup/', User_views.SignUpView.as_view(), name='signup'),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('scans/', include('scans.urls')),
]
