# from django.views.generic import TemplateView

# class HomeView(TemplateView):
#     template_name = "home.html"

from django.views.generic import TemplateView, CreateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm

class HomeView(TemplateView):
    template_name = 'home.html'

class SignUpView(CreateView):
    template_name = 'signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

class UserPageView(LoginRequiredMixin, TemplateView):
    template_name = 'user.html'
    login_url = 'login'
