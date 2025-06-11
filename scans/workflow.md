### **The Complete Workflow: From User Click to Final Report**

Here is the precise sequence of events and the role each component plays:

**Step 1: The User's Request (Django View)**

1.  A user logs into your Django web application and fills out the "Run Scan" form with the company name "Figma". They click "Submit".
2.  The request hits a Django View.
3.  The **first thing** the Django View does is create a new `ScanJob` record in your database. It sets the `company_name='Figma'`, `user=request.user`, and the initial `status='PENDING'`. It saves this and gets the new job's ID (e.g., `job_id = 123`).
4.  The **last thing** the Django View does is launch a background task, passing it the ID of the job it just created. The code looks like this: `perform_scan_task.delay(job_id=123)`.
5.  The view then immediately returns a response to the user, like "Your scan has started and you will be notified upon completion." The user experiences no waiting.

**Step 2: The Asynchronous Backbone (Celery and RabbitMQ)**

* The `perform_scan_task.delay()` command doesn't actually run the task. It sends a message containing the task name and the `job_id` to **RabbitMQ**. RabbitMQ is like a post office or a to-do list for your system.
* A separate process, the **Celery Worker**, is constantly watching this RabbitMQ "mailbox" for new messages. It sees the new task, picks it up, and starts executing the `perform_scan_task` function.

**Step 3: The Bridge in Action (The Celery Task)**

This is where the link happens. The `perform_scan_task` function is running in the background, but because it's part of your Django project, it knows about your models and your agents.

1.  The task receives `job_id=123`. It uses this to fetch the `ScanJob` object from the database: `job = ScanJob.objects.get(id=123)`.
2.  It updates the status: `job.status = 'IN_PROGRESS'` and saves it.
3.  Now, the task makes the API call to your deployed **`OrchestratorAgent`**, passing it the company name: `final_report = orchestrator.call(job.company_name)`.
4.  The `OrchestratorAgent` does all of its complex work: it calls the `WebSearchAgent`, maybe calls the `FinancialBot`, gets all the individual results back, and synthesizes them into a final report. This might take several minutes. The Celery task waits patiently for this to complete.
5.  Eventually, the `OrchestratorAgent` returns the final, synthesized report. Crucially, it could also return the *intermediate results* from the worker agents.

**Step 4: Storing the Results (The Celery Task's Final Job)**

Now we get to your specific question. Who creates the `ScanResult`?

The **Celery Task** does. It has received the data back from the Orchestrator and is now responsible for persisting it to the database.

1.  Let's say the orchestrator returned a final report and a list of individual results.
2.  The Celery task will now loop through those individual results. For each one, it creates a `ScanResult` record.
    * `ScanResult.objects.create(job=job, agent_name='WebSearchAgent', raw_output=...)`
    * `ScanResult.objects.create(job=job, agent_name='FinancialBot', raw_output=...)`
3.  Finally, it updates the master `ScanJob` record with the final synthesized report and sets the status to `COMPLETED`.
    * `job.final_report = final_report`
    * `job.status = 'COMPLETED'`
    * `job.save()`

### **Answering Your Questions Directly**

* **How is the Orchestrator agent linked to the ScanJob?**
    It isn't, directly. The **Celery Task** is linked to the `ScanJob`. The Celery Task *calls* the Orchestrator. The task acts as the middleman, holding the `ScanJob`'s context while the agent does its thinking.

* **Should the Orchestrator store the results, or should the worker agent directly publish to ScanResult?**
    Neither. This is the most important architectural principle:
    * **The Worker Agents should be "dumb" about your database.** They should know nothing about your Django models. Their only job is to receive a request and return a JSON response. This keeps them decoupled and reusable.
    * **The Orchestrator's job is AI reasoning and data synthesis.** It combines the results from the workers. It should not be responsible for database writes.
    * The **Celery Task**, which lives in your Django world, is responsible for all database interactions. It takes the data returned by the orchestrator and uses the Django ORM to save it correctly into the `ScanResult` and `ScanJob` models.

This creates a clean separation of concerns: Django and Celery handle the web application and data persistence, while the Agents handle the AI-powered data processing and reasoning.