import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_unauthenticated_redirect(client):
    """Unauthenticated users should be redirected to login when accessing a protected page."""
    response = client.get(reverse('user'))  # Assuming 'user' is the name of the user page view
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_successful_login(client, django_user_model):
    """Users can log in with correct credentials."""
    username = 'testuser'
    password = 'testpass123'
    django_user_model.objects.create_user(username=username, password=password)

    login_url = reverse('login')
    response = client.post(login_url, {'username': username, 'password': password})

    assert response.status_code == 302  # Redirect after login
    assert reverse('user') in response.url  # Assuming it redirects to 'user' page


@pytest.mark.django_db
def test_logout(client, django_user_model):
    """Logged-in users can log out and see the home page."""
    username = 'logoutuser'
    password = 'logoutpass'
    user = django_user_model.objects.create_user(username=username, password=password)

    client.login(username=username, password=password)

    response = client.get(reverse('logout'))

    assert response.status_code == 200
    assert b"You have been logged out" in response.content


@pytest.mark.django_db
def test_signup_then_login(client):
    """User can sign up, log in, and access the user page."""
    signup_url = reverse('signup')
    login_url = reverse('login')

    credentials = {
        'username': 'newuser',
        'password1': 'strongpassword123',
        'password2': 'strongpassword123'
    }

    response = client.post(signup_url, credentials)
    assert response.status_code == 302
    assert reverse('login') in response.url

    # Now log in
    login_response = client.post(login_url, {
        'username': 'newuser',
        'password': 'strongpassword123'
    })
    assert login_response.status_code == 302
    assert reverse('user') in login_response.url
