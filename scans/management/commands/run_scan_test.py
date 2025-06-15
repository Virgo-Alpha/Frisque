from django.core.management.base import BaseCommand
from users.models import User
from scans.models import ScanJob
from scans.tasks import perform_scan_task


class Command(BaseCommand):
    help = 'Creates a test user (if needed) and dispatches a Celery task for a sample company scan.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- Starting Celery Task Test Script ---"))

        # Step 1: Get or Create a test user.
        self.stdout.write(self.style.HTTP_INFO("\n[Step 1/3] Getting or creating a test user..."))
        user, created = User.objects.get_or_create(
            email='testrunner@frisque.io',
            defaults={
                'full_name': 'Automated Test Runner',
                'password': 'testpassword'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"   -> New user 'testrunner@frisque.io' was created."))
        else:
            self.stdout.write(f"   -> Found existing user: {user.email}")
            
        # Step 2: Create a new ScanJob instance.
        company_to_scan = "NVIDIA"
        self.stdout.write(self.style.HTTP_INFO(f"\n[Step 2/3] Creating a new ScanJob for company: '{company_to_scan}'..."))
        job = ScanJob.objects.create(user=user, company_name=company_to_scan)
        self.stdout.write(f"   -> Successfully created ScanJob with ID: {job.id}")
        self.stdout.write(f"   -> Initial job status: {job.status}")

        # Step 3: Dispatch the task to Celery.
        self.stdout.write(self.style.HTTP_INFO(f"\n[Step 3/3] Dispatching task 'perform_scan_task' for job ID {job.id}..."))
        task_result = perform_scan_task.delay(job.id)
        self.stdout.write(f"   -> Task successfully sent to the message queue. Celery Task ID: {task_result.id}")
        
        self.stdout.write(self.style.SUCCESS("\n--- Test Script Finished ---"))
        self.stdout.write("\n>>> ACTION REQUIRED: Go to the terminal window where 'docker-compose up' is running to see the Celery worker's log output.")