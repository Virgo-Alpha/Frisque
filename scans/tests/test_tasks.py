import pytest
import json
from unittest.mock import patch
from requests.exceptions import RequestException

from django.contrib.auth import get_user_model
from ..models import ScanJob, ScanResult
from ..tasks import perform_scan_task

# Get the custom User model
User = get_user_model()


# --- Pytest Fixtures for Test Setup ---

@pytest.fixture
def test_user(db):
    """A fixture to provide a user for the tests."""
    return User.objects.create_user(
        email="testuser@frisque.io",
        full_name="Test User",
        )

@pytest.fixture
def pending_job(test_user):
    """A fixture to provide a new ScanJob in the PENDING state."""
    return ScanJob.objects.create(user=test_user, company_name="TestCorp")


# --- Test Functions ---

@patch('scans.tasks.call_orchestrator_agent')
def test_perform_scan_task_success(mock_call_agent, pending_job):
    """
    Tests the successful execution path of the Celery task.
    We mock the `call_orchestrator_agent` to simulate a successful API call.
    """
    print("Running test: test_perform_scan_task_success")
    
    # 1. Configure the Mock
    # We tell our fake function what it should return: a valid JSON string.
    mock_success_json = json.dumps({"official_name": "TestCorp Inc.", "ceo": "Test CEO"})
    mock_call_agent.return_value = mock_success_json
    
    # 2. Execute the Task
    # We call the task directly. It will use the MOCKED version of the function.
    perform_scan_task(pending_job.id)
    
    # 3. Assert the Results
    # Reload the job from the database to get its updated state.
    pending_job.refresh_from_db()
    
    # Check that our mock function was called correctly
    mock_call_agent.assert_called_once_with("TestCorp")
    
    # Check that the job status and final report were updated
    assert pending_job.status == ScanJob.ScanJobStatus.COMPLETED
    assert pending_job.final_report["ceo"] == "Test CEO"
    
    # Check that a successful ScanResult was created
    assert ScanResult.objects.count() == 1
    result = ScanResult.objects.first()
    assert result.job == pending_job
    assert result.status == ScanResult.ScanResultStatus.SUCCESS
    assert result.raw_output["official_name"] == "TestCorp Inc."


@patch('scans.tasks.call_orchestrator_agent')
def test_perform_scan_task_failure(mock_call_agent, pending_job):
    """
    Tests the failure path of the Celery task.
    We mock the `call_orchestrator_agent` to simulate a network error.
    """
    print("Running test: test_perform_scan_task_failure")
    
    # 1. Configure the Mock
    # We tell our fake function to raise an exception when called.
    mock_call_agent.side_effect = RequestException("Simulated network failure")
    
    # 2. Execute the Task
    perform_scan_task(pending_job.id)
    
    # 3. Assert the Results
    # Reload the job from the database to get its updated state.
    pending_job.refresh_from_db()
    
    # Check that our mock function was called
    mock_call_agent.assert_called_once_with("TestCorp")
    
    # Check that the job status was correctly marked as FAILED
    assert pending_job.status == ScanJob.ScanJobStatus.FAILED
    assert pending_job.final_report is None # The final report should not be set
    
    # Check that an ERROR ScanResult was created
    assert ScanResult.objects.count() == 1
    result = ScanResult.objects.first()
    assert result.job == pending_job
    assert result.status == ScanResult.ScanResultStatus.ERROR
    assert "Simulated network failure" in result.error_message