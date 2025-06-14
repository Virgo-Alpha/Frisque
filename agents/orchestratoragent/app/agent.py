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
    # ... (The code for this function remains exactly the same as the last version)
    print(f"-> Delegating general research for '{query}' to the WebSearchAgent...")
    user_id = "orchestrator-user"
    session_id = str(uuid.uuid4())
    base_url = os.environ.get("WEB_SEARCH_AGENT_URL", "http://localhost:8501")
    session_url = f"{base_url}/apps/app/users/{user_id}/sessions/{session_id}"
    run_url = f"{base_url}/run_sse"
    try:
        requests.post(session_url, json={}).raise_for_status()
        payload = {
            "app_name": "app", "user_id": user_id, "session_id": session_id,
            "new_message": {"parts": [{"text": query}]}
        }
        run_response = requests.post(run_url, json=payload, stream=True)
        run_response.raise_for_status()
        final_text_response = "No valid response found."
        for line in run_response.iter_lines():
            if line and line.decode('utf-8').startswith("data: "):
                # ... (parsing logic remains the same)
                data = json.loads(line.decode('utf-8')[6:])
                if "content" in data and "parts" in data["content"] and data["content"]["parts"]:
                    final_text_response = data["content"]["parts"][0].get("text", final_text_response)
        return final_text_response
    except requests.exceptions.RequestException as e:
        return f"An error occurred while calling the WebSearchAgent: {e}"

# This is a NEW, local web_search tool for the Orchestrator
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
def web_search(query: str) -> str:
    """
    Use this tool for targeted follow-up searches to find specific, missing pieces of information like employee size, founders, etc.
    """
    print(f"-> [Orchestrator] Performing targeted search for: '{query}'")
    try:
        response = tavily_client.search(query=query, search_depth="basic", max_results=3)
        return "\n".join([res["content"] for res in response["results"]])
    except Exception as e:
        return f"An error occurred during the web search: {e}"

# ? The master orchestrator agent is now small thus it makes iterative calls.
# TODO: We need to limit by time / results to avoid infinite loops or excessive API calls.
# TODO: Specify the fields, maybe
# TODO: Add another agent to test for this.

# --- Orchestrator Agent Definition ---
OrchestratorAgent = Agent(
    name="OrchestratorAgent",
    model="gemini-2.0-flash-001",
    # The instruction is updated to explain the two-tool workflow.
    instruction="""
    You are a master data analyst. Your goal is to create a detailed JSON object about a company.
    You have a two-step process and two tools available:

    1.  **Initial Research:** First, you MUST call the `company_researcher` tool with the company's name. This will give you a general block of text.
    2.  **Analysis and Follow-up:** Analyze the text from the first step. Then, create the final JSON object. If any information (like 'employee_size' or 'founders') is missing from the text, you MUST use the `web_search` tool to perform targeted follow-up searches to find it. Example: `web_search(query='Figma employee count')`.

    Your final answer must be a single JSON object with all fields correctly filled.
    """,
    # The Orchestrator now has two tools at its disposal.
    tools=[company_researcher, web_search],
)

root_agent = OrchestratorAgent