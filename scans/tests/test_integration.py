# In scans/tests/test_integration.py

import pytest
import json
from unittest.mock import patch

from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import ScanJob, ScanResult
from ..tasks import perform_scan_task

User = get_user_model()


# --- Fixtures for setting up test data ---

@pytest.fixture
def test_user(db):
    """Creates a user for tests with all required fields."""
    # This now includes full_name and password to match your custom user model
    return User.objects.create_user(
        email="integration_user@frisque.io",
        full_name="Integration Test User",
        company="Frisque Testing Co",
        password="testpassword123"
    )

@pytest.fixture
def pending_job(test_user):
    """Creates a ScanJob with a PENDING status."""
    return ScanJob.objects.create(user=test_user, company_name="TestCorp")

@pytest.fixture
def completed_job(test_user):
    """Creates a ScanJob with a COMPLETED status and a mock report."""
    report_data = {
        "official_name": "Test Corporation Inc.",
        "description": "A company for testing purposes.",
        "ceo": "Dr. Testo",
        "founders": ["John Doe", "Jane Doe"]
    }
    return ScanJob.objects.create(
        user=test_user,
        company_name="TestCorp",
        status=ScanJob.ScanJobStatus.COMPLETED,
        final_report=report_data
    )


# --- Tests for the Celery Task ---

@patch('scans.tasks.call_orchestrator_agent')
def test_scan_task_updates_job_on_success(mock_call_agent, pending_job):
    """
    Verify that the Celery task correctly updates the ScanJob status and final_report
    when the agent call is successful.
    """
    # 1. Configure the Mock
    mock_success_json_str = json.dumps({
        "official_name": "TestCorp Inc.",
        "description": "A successful test."
    })
    mock_call_agent.return_value = mock_success_json_str
    
    # 2. Execute the Task
    perform_scan_task(pending_job.id)
    
    # 3. Assert the Results
    pending_job.refresh_from_db()
    
    mock_call_agent.assert_called_once_with("TestCorp")
    
    assert pending_job.status == ScanJob.ScanJobStatus.COMPLETED
    assert pending_job.final_report['official_name'] == "TestCorp Inc."
    
    assert pending_job.results.count() == 1
    result_record = pending_job.results.first()
    assert result_record.status == ScanResult.ScanResultStatus.SUCCESS


# --- Tests for the Result View ---

def test_result_view_displays_completed_job_info(client, completed_job):
    """
    Verify that the results page displays the correct information for a COMPLETED job.
    """
    client.force_login(completed_job.user)
    url = reverse('scans:scan_result', kwargs={'pk': completed_job.pk})
    response = client.get(url)
    
    assert response.status_code == 200
    
    content = response.content.decode()
    assert "Scan Report: TestCorp" in content
    assert "Test Corporation Inc." in content
    assert "Dr. Testo" in content
    assert "John Doe" in content

def test_result_view_shows_in_progress_message(client, pending_job):
    """
    Verify that the results page shows the "In Progress" message for a PENDING job.
    """
    client.force_login(pending_job.user)
    url = reverse('scans:scan_result', kwargs={'pk': pending_job.pk})
    response = client.get(url)
    
    assert response.status_code == 200
    
    content = response.content.decode()
    assert '<meta http-equiv="refresh" content="30">' in content
    assert "Your report is being generated" in content
    assert "Test Corporation Inc." not in content
