from django.contrib.auth.forms import UserCreationForm
from .models import User  # Your custom user
from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "full_name", "company")

class CustomAllauthSignupForm(AllauthSignupForm):
    # Override the __init__ to remove the username field
    def __init__(self, *args, **kwargs):
        super(CustomAllauthSignupForm, self).__init__(*args, **kwargs)

    # If you want to add first_name and last_name during signup
    full_name = forms.CharField(max_length=30, required=False, label='Full Name')

    def save(self, request):
        user = super(CustomAllauthSignupForm, self).save(request)
        user.full_name = self.cleaned_data.get('full_name')
        user.save()
        return user