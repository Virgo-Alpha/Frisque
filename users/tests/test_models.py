import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

@pytest.mark.django_db
def test_create_user_success():
    user = User.objects.create_user(
        email='testuser@example.com',
        password='securepassword123',
        full_name='Test User',
        company='Test VC'
    )
    assert user.email == 'testuser@example.com'
    assert user.full_name == 'Test User'
    assert user.company == 'Test VC'
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False

@pytest.mark.django_db
def test_create_superuser_success():
    admin = User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        full_name='Admin User',
        company='Frisque Capital'
    )
    assert admin.email == 'admin@example.com'
    assert admin.is_superuser is True
    assert admin.is_staff is True
    assert admin.is_active is True

@pytest.mark.django_db
def test_create_user_no_email_raises_value_error():
    with pytest.raises(ValueError) as excinfo:
        User.objects.create_user(
            email='',
            password='somepass123',
            full_name='No Email',
            company='Ghost Firm'
        )
    assert 'Users must have an email address' in str(excinfo.value)
