import json
from celery import shared_task
from .models import ScanJob, ScanResult
from .utils import call_orchestrator_agent
import logging

logger = logging.getLogger(__name__)


# TODO: Debug the celery import
# TODO: Run the test in web shell and check the logs

@shared_task
def perform_scan_task(scan_job_id: str):
    """
    A Celery task to perform a full due diligence scan asynchronously.
    """
    logger.info(f"Starting scan for ScanJob ID: {scan_job_id}")
    try:
        job = ScanJob.objects.get(id=scan_job_id)
        logger.info(f"Found job with company_name: {job.company_name}")  # Log the company name
    except ScanJob.DoesNotExist:
        logger.error(f"Error: ScanJob with ID {scan_job_id} not found.")
        return

    # 1. Update the job status to show it's running
    job.status = ScanJob.ScanJobStatus.IN_PROGRESS
    job.save()

    try:
        # 2. Call the Orchestrator Agent via the utility function
        result_str = call_orchestrator_agent(job.company_name)
        result_json = json.loads(result_str)

        # 3. Create a ScanResult record to log the successful agent interaction
        ScanResult.objects.create(
            job=job,
            agent_name="OrchestratorAgent",
            status=ScanResult.ScanResultStatus.SUCCESS,
            raw_output=result_json
        )

        # 4. Update the main ScanJob with the final report and mark as complete
        job.final_report = result_json
        job.status = ScanJob.ScanJobStatus.COMPLETED
        job.save()
        logger.info(f"Successfully completed scan for ScanJob ID: {scan_job_id}")

    except Exception as e:
        # If anything goes wrong during the API call or processing,
        # log it and mark the job as failed.
        logger.exception(f"Error during scan for ScanJob ID {scan_job_id}: {e}")
        error_message = f"An unexpected error occurred: {str(e)}"
        ScanResult.objects.create(
            job=job,
            agent_name="OrchestratorAgent",
            status=ScanResult.ScanResultStatus.ERROR,
            raw_output={"error": error_message},
            error_message=error_message
        )
        job.status = ScanJob.ScanJobStatus.FAILED
        job.save()

    # Here we would add the logic for email notifications (Ticket F1.7)
    # For example: send_completion_email(job.id)