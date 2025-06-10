## Environment variables
In each agents folder, copy the `.env.example` file to `.env` and fill in the required environment variables. 

```bash
cp .env.example .env
```

## Creating an agent
In the agent/ directory, you can create a new agent by following these steps:

```bash
agent-starter-pack create <agent_name>
```

## Running an agent
To run an agent, use the following command:

```bash
cd <agent_name> && make install && make playground
```

## Viewing agent
To view an agent go to `http://localhost:8501`

## Adding dependencies / requirements
To add dependencies to the agent, please modify its `pyproject.toml` file. You can add any Python package that is available on PyPI.

```bash
dependencies = [
  "google-cloud-agent-starter-pack[adk,playground]",
  # Add your new dependencies here

]
```
Then run the following command to install the new dependencies:

```bash
make install
```

## Deploying
Sign in using the service account first: 
```bash
gcloud auth activate-service-account --key-file=$HOME/.google/credentials/gcp-frisque-credentials.json
```

You might to give a few permissions to your service account such as `Cloud Build Editor`, `Artifact Registry Writer` and `Service Account Consumer`.

Locally, the agents are served on ports specified in the Makefile e.g., 8501 or 8502. The standard and most reliable way to tell Google Cloud how to start your application is by adding a simple text file to your project called a Procfile. This file explicitly defines the command that should be run to start your web server. At the base of the agent's folder add a Procfile with the following content:

```bash
web: uvicorn app.server:app --host 0.0.0.0 --port $PORT
```

To deploy, run the command:

```bash
make backend
```

_caveat_
For our case where we have env variables, we need to deploy the workers and the master agents in that order and passing the env variables in the deploy scripts. An example of the worker deployment script is show below. You should put it in the Makefile of the worker then use the command `make backend` command to deploy it.

```bash
backend:
    PROJECT_ID=$$(gcloud config get-value project) && \
    gcloud run deploy websearchagent \
        --source . \
        --project $$PROJECT_ID \
        --region "africa-south1" \
        --no-allow-unauthenticated \
        --set-env-vars "TAVILY_API_KEY=$(TAVILY_API_KEY)"
```

The url for the web search worker agent is:
```bash
WEB_SEARCH_AGENT_URL=https://websearchagent-46904927368.africa-south1.run.app
```

Then the master agent is deployed using the command:

```bash
backend:
    PROJECT_ID=$$(gcloud config get-value project) && \
    gcloud run deploy orchestratoragent \
        --source . \
        --memory "4Gi" \
        --project $$PROJECT_ID \
        --region "africa-south1" \
        --no-allow-unauthenticated \
        --labels "created-by=adk" \
        --set-env-vars \
        "COMMIT_SHA=$(shell git rev-parse HEAD),TAVILY_API_KEY=$(TAVILY_API_KEY),WEB_SEARCH_AGENT_URL=$(WEB_SEARCH_AGENT_URL)"
```

The url for the master agent is:
```bash
ORCHESTRATOR_AGENT_URL=https://orchestratoragent-46904927368.africa-south1.run.app
```

After deployment is complete, go to your Google Cloud Console, navigate to Cloud Run, and find your <agent> service. Copy its public URL. It will look something like https://<agent>-xyz-uc.a.run.app

Grant "Invoker" Permissions: By default, Cloud Run services are private. To allow your Django app to call your OrchestratorAgent, you must grant it permission (Cloud Run Invoker).
