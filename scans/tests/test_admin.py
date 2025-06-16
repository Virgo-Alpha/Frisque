import pytest
from django.db import connection
from django.contrib.auth import get_user_model
from ..models import ScanJob, ScanResult

User = get_user_model()

# --- Fixtures ---
@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email="testuser@frisque.io",
        full_name="Test User",
        password="testpassword123"
    )

@pytest.fixture
def completed_job(test_user):
    return ScanJob.objects.create(
        user=test_user,
        company_name="Figma",
        status=ScanJob.ScanJobStatus.COMPLETED
    )

# --- Test Functions ---
def test_scanjob_creation_and_str(completed_job, test_user):
    print("Running test: test_scanjob_creation_and_str")
    job = completed_job
    assert isinstance(job, ScanJob)
    assert job.company_name == "Figma"
    assert job.user == test_user
    expected_str = f"Scan for Figma ({ScanJob.ScanJobStatus.COMPLETED.label})"
    assert str(job) == expected_str

def test_scanresult_creation_and_str(completed_job):
    print("Running test: test_scanresult_creation_and_str")
    result = ScanResult.objects.create(
        job=completed_job,
        agent_name="WebSearchAgent",
        raw_output={"ceo": "Dylan Field"}
    )
    assert isinstance(result, ScanResult)
    assert result.agent_name == "WebSearchAgent"
    expected_str = f"Result from WebSearchAgent for job {completed_job.id}"
    assert str(result) == expected_str

def test_foreign_key_relationship_and_cascade_delete(completed_job):
    print("Running test: test_foreign_key_relationship_and_cascade_delete")
    ScanResult.objects.create(job=completed_job, agent_name="Agent1", raw_output={})
    ScanResult.objects.create(job=completed_job, agent_name="Agent2", raw_output={})
    assert completed_job.results.count() == 2
    job_id = completed_job.id
    completed_job.delete()
    assert not ScanJob.objects.filter(id=job_id).exists()
    assert ScanResult.objects.filter(job__id=job_id).count() == 0

@pytest.mark.django_db
def test_database_is_postgresql():
    print("Running test: test_database_is_postgresql")
    assert connection.vendor == 'postgresql'