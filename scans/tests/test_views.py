# frisque/scans/tests/test_views.py

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

# Get the custom User model
User = get_user_model()

@pytest.mark.django_db
class TestRunScanView:
    """
    Test suite for the RunScanView in the scans app.
    Verifies page loading, form submission (valid/invalid), and user authentication.
    """

    @pytest.fixture
    def client(self):
        """Provides a Django test client."""
        from django.test import Client
        return Client()

    @pytest.fixture
    def logged_in_user(self):
        """Creates and logs in a test user, returning the user object."""
        email = 'scanuser@example.com'
        password = 'ScanUserPass123!'
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name='Scan'
        )
        EmailAddress.objects.create(
            user=user,
            email=email,
            primary=True,
            verified=True
        )
        return user

    def test_run_scan_page_loads_correctly_for_authenticated_user(self, client, logged_in_user):
        """
        Verify that the 'Run Scan' page loads successfully (HTTP 200) for an authenticated user.
        """
        # Log in the user
        client.force_login(logged_in_user) # pytest-django's convenient way to log in

        response = client.get(reverse('scans:run_scan'))

        assert response.status_code == 200
        assert 'scans/run_scan.html' in [t.name for t in response.templates]
        assert b"Initiate New Due Diligence Scan" in response.content # Check for page title

    def test_run_scan_page_redirects_unauthenticated_user_to_login(self, client):
        """
        Verify that an unauthenticated user is redirected from the 'Run Scan' page to the login page.
        """
        response = client.get(reverse('scans:run_scan'))

        assert response.status_code == 302
        # Check if it redirects to the LOGIN_URL (e.g., /login/) with a 'next' parameter
        assert response.url.startswith(reverse('login'))
        assert f"next={reverse('scans:run_scan')}" in response.url


    def test_submitting_form_with_valid_data_redirects_to_dashboard(self, client, logged_in_user, caplog):
        """
        Verify that submitting the form with valid data results in a successful scan initiation
        (logged message) and redirection to the home dashboard.
        """
        # Log in the user
        client.force_login(logged_in_user)

        valid_data = {
            'company_name': 'Test Company Inc.',
            'company_website': 'https://www.testcompany.com',
        }

        with caplog.at_level('INFO'): # Capture logs at INFO level
            response = client.post(reverse('scans:run_scan'), data=valid_data, follow=True)

            # Check for successful redirection to home page
            # RunScanView redirects to reverse_lazy('home') on success
            assert response.status_code == 200 # After following redirect
            assert response.request['PATH_INFO'] == reverse('home')

    def test_submitting_form_with_invalid_data_re_renders_page_with_errors(self, client, logged_in_user):
        """
        Verify that submitting the form with invalid data re-renders the page
        and displays validation errors.
        """
        # Log in the user
        client.force_login(logged_in_user)

        # Missing required fields (invalid data)
        invalid_data = {
            'company_name': '', # Missing
            'company_website': 'invalid-url', # Invalid format
        }

        response = client.post(reverse('scans:run_scan'), data=invalid_data)

        # Should return 200 OK because it re-renders the same page
        assert response.status_code == 200
        assert 'scans/run_scan.html' in [t.name for t in response.templates]

        # Check for error messages on the page
        assert b"Please correct the errors below." in response.content # General message from view
        assert b"This field is required." in response.content # Specific form error for company_name
        assert b"Enter a valid URL." in response.content # Specific form error for company_website
