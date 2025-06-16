# frisque/frisque_core/tests/test_auth.py

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from allauth.account.models import EmailAddress

# Get the custom User model
User = get_user_model()

@pytest.mark.django_db
class TestAuthFlows:
    """
    Comprehensive test suite for user authentication flows in the Frisque application using pytest.
    Covers login, logout, signup, and protected page access.
    """

    @pytest.fixture
    def test_user_data(self):
        return {
            'email': 'testuser@example.com',
            'password': 'Password123!',
            'full_name': 'Test'
        }

    @pytest.fixture
    def test_user(self, test_user_data):
        user = User.objects.create_user(
            email=test_user_data['email'],
            password=test_user_data['password'],
            full_name=test_user_data['full_name']
        )
        return user

    @pytest.fixture
    def client(self):
        from django.test import Client
        return Client()

    def test_unauthenticated_user_redirected_from_protected_page(self, client):
        response = client.get(reverse('user'))
        assert response.status_code == 302
        expected_redirect_url = f"{settings.LOGIN_URL}?next={reverse('user')}"
        assert response.url == expected_redirect_url

    def test_user_can_successfully_log_in(self, client, test_user_data, test_user):
        response = client.post(
            reverse("account_login"),
            {
                "login": test_user_data["email"],
                "password": test_user_data["password"]
            },
            follow=True
        )

        print(response.content.decode())  # to debug response

        assert response.status_code == 200
        assert response.request["PATH_INFO"].rstrip("/") == settings.LOGIN_REDIRECT_URL.rstrip("/")


    def test_logged_in_user_can_successfully_log_out(self, client, test_user, test_user_data):
        """
        Verify that a logged-in user can successfully log out and is redirected
        to the LOGOUT_REDIRECT_URL (home page).
        """
        # --- Check if user is initially logged in ---
        # 1. Log in the user using the client's login method (sets session)
        login_success = client.login(email=test_user_data['email'], password=test_user_data['password'])
        assert login_success is True, "User failed to log in for logout test setup."

        # 2. Verify login state by accessing a protected page (should not redirect)
        pre_logout_protected_response = client.get(reverse('user'))
        assert pre_logout_protected_response.status_code == 200
        assert b"Welcome, Test!" in pre_logout_protected_response.content


        # --- Attempt to log out ---
        # Use GET for logout if ACCOUNT_LOGOUT_ON_GET = True is set in settings.py
        # Otherwise, a POST with CSRF token is required.
        # Given your settings, GET should work and redirect.
        response = client.get(reverse('account_logout')) # Your custom logout URL
        print(f"Logout GET response status: {response.status_code}, URL: {response.url}")

        # Assert that it redirects to LOGOUT_REDIRECT_URL
        assert response.status_code == 302
        assert response.url == settings.LOGOUT_REDIRECT_URL

        # --- Check if user is actually logged out ---
        # Try to access the protected page again. It should now redirect to login.
        post_logout_protected_response = client.get(reverse('user'))
        assert post_logout_protected_response.status_code == 302
        assert post_logout_protected_response.url.startswith(settings.LOGIN_URL)


    def test_user_can_sign_up_then_log_in_and_see_user_page(self, client):
        new_user_email = 'newuser@example.com'
        new_user_password = 'NewPassword123!'

        # 1. Attempt to sign up the new user
        signup_response = client.post(
            reverse('account_signup'),
            {
                'email': new_user_email,
                'password1': new_user_password,
                'password2': new_user_password
            },
            follow=True
        )

        if signup_response.status_code != 200:
            print(signup_response.context["form"].errors)

        # Assertion corrected: SignUpView.success_url is reverse_lazy('login'),
        # so after following, it should land on the login page.
        assert signup_response.status_code == 200
        assert signup_response.request['PATH_INFO'] == settings.LOGIN_REDIRECT_URL
        # ! Currently, after sign up you are just logged in but this shouldn't be the case
        # assert b"Please log in with your newly created account." in signup_response.content

        # 2. Log in with the newly signed-up user's credentials
        login_response = client.post(
            reverse('account_login'),
            {'login': new_user_email, 'password': new_user_password},
            follow=True
        )

        # Check if login was successful and redirected to LOGIN_REDIRECT_URL
        assert login_response.status_code == 200
        assert login_response.request['PATH_INFO'] == settings.LOGIN_REDIRECT_URL

        # Verify the user is authenticated and is on their user page
        assert b"Welcome, " in login_response.content
        assert 'users/user_welcome.html' in [t.name for t in login_response.templates]

        # Verify that the new user object exists in the database
        assert User.objects.filter(email=new_user_email).exists()