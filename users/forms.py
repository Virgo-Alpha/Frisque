from django.contrib.auth.forms import UserCreationForm
from .models import User  # Your custom user

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "full_name", "company")
