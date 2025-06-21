# frisque/scans/views.py

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin # Ensure user is logged in
from django.urls import reverse_lazy # For redirection after success
from django.contrib import messages # For displaying messages to the user

from .forms import RunScanForm # Import the form you just created

import logging
logger = logging.getLogger(__name__)

class RunScanView(LoginRequiredMixin, View):
    """
    View for initiating a new due diligence scan.
    Requires the user to be logged in.

    Handles both GET (display form) and POST (process form submission) requests.
    """
    template_name = 'scans/run_scan.html' # We will create this template next
    login_url = reverse_lazy('login') # Redirect unauthenticated users to the custom login page
    # success_url = reverse_lazy('scans:scan_initiated_success') # Future: URL to redirect after successful scan initiation

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests: Displays an empty RunScanForm.
        """
        form = RunScanForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests: Processes submitted RunScanForm data.
        """
        form = RunScanForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data['company_name']
            company_website = form.cleaned_data['company_website']

            # --- Placeholder for actual scan initiation logic ---
            # In a real application, you would:
            # 1. Save the scan request to the database (e.g., a Scan model).
            # 2. Trigger a Celery task to perform the AI due diligence in the background.
            # 3. Store results or a scan ID to be displayed on a dashboard later.
            logger.info(f"Scan initiated: Company Name='{company_name}', Website='{company_website}' by user '{request.user.email}'")
            messages.success(request, f"Scan for '{company_name}' initiated successfully! We will begin peeling the layers.")

            # --- Future: Redirect to a scan status page or dashboard ---
            # For now, let's redirect to the home page or a simple success message
            return redirect(reverse_lazy('home')) # Redirect to home after successful submission
            # return redirect(self.success_url) # If a dedicated success URL is defined

        else:
            # If form is not valid, re-render the form with validation errors
            messages.error(request, "Please correct the errors below.")
            return render(request, self.template_name, {'form': form})
