# from django.views.generic import TemplateView

# class HomeView(TemplateView):
#     template_name = "home.html"

from django.views.generic import TemplateView, CreateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.sites.models import Site
import logging 

logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Directly try to get the Site with ID 1, as per settings.SITE_ID
        # This will raise DoesNotExist if it's not found, confirming the issue.
        site_obj = Site.objects.get(id=2)
        context["site"] = site_obj # Add it to context if found
        # No logging here for now, to keep it simple and avoid potential side-issues
        return context

class SignUpView(CreateView):
    template_name = 'signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

class UserPageView(LoginRequiredMixin, TemplateView):
    template_name = 'user.html'
    login_url = 'login'
