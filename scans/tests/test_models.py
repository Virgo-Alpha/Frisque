import pytest
from django.db import connection
from django.contrib.auth import get_user_model
from ..models import ScanJob, ScanResult

# Get the custom User model
User = get_user_model()


# --- Pytest Fixtures for Test Setup ---

@pytest.fixture
def test_user(db):
    """
    A pytest fixture to create and return a user instance for tests.
    The 'db' argument automatically enables database access.
    """
    return User.objects.create_user(
        email="testuser@frisque.io",
        full_name="Test User",
        password="testpassword123"
    )

@pytest.fixture
def completed_job(test_user):
    """
    A pytest fixture that depends on the test_user fixture
    to create and return a ScanJob instance.
    """
    return ScanJob.objects.create(
        user=test_user,
        company_name="Figma",
        status=ScanJob.ScanJobStatus.COMPLETED
    )


# --- Test Functions ---

def test_scanjob_creation_and_str(completed_job, test_user):
    """
    Verify that a ScanJob instance can be created successfully and its __str__ method is correct.
    This test receives the 'completed_job' and 'test_user' objects from the fixtures above.
    """
    print("Running test: test_scanjob_creation_and_str")
    job = completed_job
    assert isinstance(job, ScanJob)
    assert job.company_name == "Figma"
    assert job.user == test_user
    
    # Test the __str__ method
    expected_str = f"Scan for Figma ({ScanJob.ScanJobStatus.COMPLETED.label})"
    assert str(job) == expected_str

def test_scanresult_creation_and_str(completed_job):
    """
    Verify that a ScanResult instance can be created and linked to a ScanJob.
    """
    print("Running test: test_scanresult_creation_and_str")
    result = ScanResult.objects.create(
        job=completed_job,
        agent_name="WebSearchAgent",
        raw_output={"ceo": "Dylan Field"}
    )
    assert isinstance(result, ScanResult)
    assert result.agent_name == "WebSearchAgent"
    
    # Test the __str__ method
    expected_str = f"Result from WebSearchAgent for job {completed_job.id}"
    assert str(result) == expected_str

def test_foreign_key_relationship_and_cascade_delete(completed_job):
    """
    Confirm the foreign key relationship works and that deleting a ScanJob deletes its ScanResults.
    """
    print("Running test: test_foreign_key_relationship_and_cascade_delete")
    # Create a few results linked to the same job
    ScanResult.objects.create(job=completed_job, agent_name="Agent1", raw_output={})
    ScanResult.objects.create(job=completed_job, agent_name="Agent2", raw_output={})
    
    # Use the 'related_name' to check the count
    assert completed_job.results.count() == 2
    
    # Now, delete the parent ScanJob
    job_id = completed_job.id
    completed_job.delete()
    
    # Verify that the ScanJob is gone
    assert not ScanJob.objects.filter(id=job_id).exists()
    
    # Verify that all related ScanResults are also gone (due to on_delete=CASCADE)
    assert ScanResult.objects.filter(job__id=job_id).count() == 0

@pytest.mark.django_db
def test_database_is_postgresql():
    """
    Test that Django is connected to PostgreSQL now and not SQLite.
    This test is decorated with @pytest.mark.django_db to enable database access.
    """
    print("Running test: test_database_is_postgresql")
    assert connection.vendor == 'postgresql'