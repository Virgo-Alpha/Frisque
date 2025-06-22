from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin # Ensure user is logged in
from django.urls import reverse_lazy # For redirection after success
from django.http import JsonResponse
from django.contrib import messages

from scans.models import ScanJob
from scans.tasks import perform_scan_task # For displaying messages to the user

from .forms import RunScanForm # Import the form you just created

import logging
logger = logging.getLogger(__name__)

class RunScanView(LoginRequiredMixin, View):
    """
    View for initiating a new due diligence scan.
    Requires the user to be logged in.

    Handles both GET (display form) and POST (process form submission) requests.
    """
    template_name = 'scans/run_scan.html'
    login_url = reverse_lazy('login')
    # success_url = reverse_lazy('scans:scan_initiated_success') # Future: URL to redirect after successful scan initiation

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests: Displays an empty RunScanForm.
        """
        form = RunScanForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests: Creates a ScanJob and dispatches a Celery task.
        """
        # Assuming form validation is handled or you get data directly
        company_name = request.POST.get('company_name', '')
        company_url = request.POST.get('company_website', '')

        if not company_name:
            messages.error(request, "Company name is a required field.")
            return render(request, self.template_name, {})

        # 1. Create a new ScanJob record in the database.
        new_job = ScanJob.objects.create(
            user=request.user,
            company_name=company_name,
            company_url=company_url
        )

        # 2. Dispatch the Celery task with the ID of the new job.
        perform_scan_task.delay(new_job.id)

        # 3. Add a success message for the user.
        messages.success(request, f"Scan for '{company_name}' initiated successfully! You will be notified upon completion.")
        
        # 4. Redirect the user to the results page for the new job.
        return redirect('scans:scan_result', pk=new_job.id)


class ScanResultView(LoginRequiredMixin, DetailView):
    """
    Displays the final report for a specific ScanJob using Django's generic DetailView.
    """
    model = ScanJob
    template_name = 'scans/scan_result.html'
    context_object_name = 'job'
