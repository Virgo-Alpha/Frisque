# users/views.py

from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm # Assuming this form exists and is correctly defined

class CustomLoginView(LoginView):
    """
    Custom Login View to handle user authentication.
    Uses 'registration/login.html' as the template.
    redirect_authenticated_user ensures logged-in users are redirected
    to LOGIN_REDIRECT_URL (defined in settings.py) instead of seeing the login page.
    """
    template_name = "registration/login.html"
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    """
    Custom Logout View to handle user logout.
    Uses 'registration/logout.html' as the template.
    next_page specifies the URL to redirect to after successful logout.
    """
    template_name = "registration/logout.html"
    next_page = reverse_lazy('home') # Redirects to the 'home' URL name after logout

class SignUpView(CreateView):
    """
    View for user registration (Sign Up).
    Uses CustomUserCreationForm for handling form validation and user creation.
    Renders 'users/signup.html' template.
    On successful signup, redirects to the 'login' URL.
    """
    form_class = CustomUserCreationForm
    template_name = "users/signup.html"
    success_url = reverse_lazy("login")

class UsersView(LoginRequiredMixin, TemplateView):
    """
    A protected view for authenticated users (e.g., a user dashboard).
    Requires a user to be logged in to access.
    If not logged in, redirects to the 'login' URL.
    Renders 'users/user_welcome.html' template.
    """
    template_name = "users/user_welcome.html"
    login_url = 'login' # Name of the URL for the login page
