from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

class CustomLogoutView(LogoutView):
    template_name = "registration/logout.html"

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/signup.html"
    success_url = reverse_lazy("login")

class UsersView(LoginRequiredMixin, TemplateView):
    template_name = "users/user_welcome.html"
