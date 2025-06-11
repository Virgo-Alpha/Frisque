import uuid
from django.db import models
from django.conf import settings


class ScanJob(models.Model):
    """
    The master record for a single due diligence request. This is the "Project".
    """
    class ScanJobStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user who initiated the scan."
    )
    company_name = models.CharField(max_length=255, help_text="The name of the company being scanned.")
    company_url = models.URLField(max_length=255, blank=True, null=True, help_text="The primary URL of the company.")
    
    status = models.CharField(
        max_length=20,
        choices=ScanJobStatus.choices,
        default=ScanJobStatus.PENDING,
        help_text="The current status of the overall scan job."
    )
    final_report = models.JSONField(blank=True, null=True, help_text="The final, synthesized report from the Orchestrator.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """
        A human-readable representation of the model instance.
        """
        return f"Scan for {self.company_name} ({self.get_status_display()})"


class ScanResult(models.Model):
    """
    Stores the individual output from a single worker agent for a specific ScanJob. This is a "Deliverable".
    """
    class ScanResultStatus(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Success'
        ERROR = 'ERROR', 'Error'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(
        ScanJob,
        on_delete=models.CASCADE,
        related_name='results', # Allows us to do job.results.all() to get all results for a job
        help_text="The parent ScanJob this result belongs to."
    )
    agent_name = models.CharField(max_length=100, help_text="The name of the worker agent that produced this result.")
    
    status = models.CharField(
        max_length=20,
        choices=ScanResultStatus.choices,
        default=ScanResultStatus.SUCCESS
    )
    raw_output = models.JSONField(help_text="The raw JSON output from the worker agent.")
    error_message = models.TextField(blank=True, null=True, help_text="Any error messages if this specific agent task failed.")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        """
        A human-readable representation of the model instance.
        """
        return f"Result from {self.agent_name} for job {self.job.id}"