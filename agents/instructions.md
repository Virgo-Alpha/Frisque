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
To deploy, run the command:

```bash
make deploy
```

After deployment is complete, go to your Google Cloud Console, navigate to Cloud Run, and find your <agent> service. Copy its public URL. It will look something like https://<agent>-xyz-uc.a.run.app
