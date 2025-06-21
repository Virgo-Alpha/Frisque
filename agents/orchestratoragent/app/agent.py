import os
import re
import uuid
import json
import requests
from dotenv import load_dotenv

load_dotenv()

import google.auth
from google.adk.agents import Agent
from tavily import TavilyClient # <-- Import TavilyClient here as well

# --- GCP Configuration ---
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


# --- Tool Definitions ---

# This tool calls the remote WebSearchAgent
def company_researcher(query: str) -> str:
    """
    Use this tool FIRST to get a general overview and raw text about a company.
    This should be your first step.
    """
    print(f"-> Delegating general research for '{query}' to the WebSearchAgent...")

    user_id = "user"
    app_name = "app"
    session_id = str(uuid.uuid4())  # Or pass a fixed UUID if reusing sessions
    base_url = os.environ.get("WEB_SEARCH_AGENT_URL", "http://localhost:8501")

    # Step 1: Create session
    session_url = f"{base_url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
    run_url = f"{base_url}/run_sse"

    try:
        # Create session (POST empty body)
        requests.post(session_url, json={}).raise_for_status()

        # Step 2: Send message to agent
        payload = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [
                    {
                        "text": query
                    }
                ]
            },
            "streaming": False
        }

        run_response = requests.post(run_url, json=payload, stream=True)
        run_response.raise_for_status()

        final_text_response = "No valid response found."
        for line in run_response.iter_lines():
            if line and line.decode("utf-8").startswith("data: "):
                try:
                    data = json.loads(line.decode("utf-8")[6:])
                    if "content" in data and "parts" in data["content"]:
                        for part in data["content"]["parts"]:
                            if "text" in part:
                                final_text_response = part["text"]
                except json.JSONDecodeError:
                    continue

        return final_text_response

    except requests.exceptions.RequestException as e:
        return f"An error occurred while calling the WebSearchAgent: {e}"

# local web_search tool for the Orchestrator
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
def web_search(query: str) -> str:
    """
    Use this tool for targeted follow-up searches to find specific, missing pieces of information like employee size, founders, etc.
    """
    print(f"-> [Orchestrator] Performing targeted search for: '{query}'")
    try:
        response = tavily_client.search(query=query, search_depth="basic", max_results=5)
        return "\n".join([res["content"] for res in response["results"]])
    except Exception as e:
        return f"An error occurred during the web search: {e}"
    
def call_json_formatter(text_to_format: str) -> str:
    """Use this tool to convert the raw text into a structured JSON object."""
    print("-> [Orchestrator] Calling JsonFormattingAgent...")

    user_id = "user"
    app_name = "app"
    session_id = str(uuid.uuid4())
    base_url = os.environ.get("JSON_FORMATTING_AGENT_URL", "http://localhost:8503")

    session_url = f"{base_url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
    run_url = f"{base_url}/run_sse"

    try:
        # Step 1: Create a session
        requests.post(session_url, json={}).raise_for_status()

        # Step 2: Send message to agent
        payload = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [
                    {
                        "text": text_to_format
                    }
                ]
            },
            "streaming": False
        }

        response = requests.post(run_url, json=payload, stream=True, timeout=300)
        response.raise_for_status()

        final_json_response = "No valid response received."
        for line in response.iter_lines():
            if line and line.decode("utf-8").startswith("data: "):
                try:
                    data = json.loads(line.decode("utf-8")[6:])
                    if "content" in data and "parts" in data["content"]:
                        for part in data["content"]["parts"]:
                            if "text" in part:
                                final_json_response = part["text"]
                except json.JSONDecodeError:
                    continue

        return final_json_response

    except requests.exceptions.RequestException as e:
        return f"Error calling JsonFormattingAgent: {e}"

# ? The master orchestrator agent is now small thus it makes iterative calls.
# TODO: We need to limit by time / results to avoid infinite loops or excessive API calls.
# // TODO: Specify the fields, maybe
# // TODO: Add another agent to test for this.

# --- Orchestrator Agent Definition ---
OrchestratorAgent = Agent(
    name="OrchestratorAgent",
    model="gemini-2.0-flash-001",
    # The instruction is updated to explain the two-tool workflow.
    instruction="""
You are a master data analyst. Your goal is to create a detailed JSON object about a company based on the user's prompt.

Your workflow:

1. **Initial Research**: Call `company_researcher` with the company name. This gives you general background.
2. **Targeted Follow-ups**: If any fields are missing (see list below), use `web_search` to query for them. Do this even if some values seem partially available.
3. **Formatting**: Combine all raw text and pass it to `call_json_formatter`, which will return a JSON object with the following fields:

- official_name
- description
- industry
- founders
- ceo
- products
- geographical_location
- employee_size
- pricing_plans
- funding
- valuation
- release_date
- alternatives

If you cannot find a field, do not guess—just ensure the formatter receives 'Not Found' where appropriate.

Your final answer MUST be the direct, unmodified output from `call_json_formatter`.
""",
    # The Orchestrator now has two tools at its disposal.
    tools=[company_researcher, web_search, call_json_formatter],
)

root_agent = OrchestratorAgent