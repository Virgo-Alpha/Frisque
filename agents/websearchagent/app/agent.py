# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# In agents/websearchagent/agent.py

import os
import json
from dotenv import load_dotenv

load_dotenv()

import google.auth
from google.adk.agents import Agent
from tavily import TavilyClient

# --- GCP Configuration ---
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# --- Tool Definition ---
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def web_search(query: str) -> str:
    """Performs a web search to find information on a company."""
    print(f"-> [WebSearchAgent] Performing single web search for: '{query}'")
    try:
        # We now only return the 'content' of the top search result for simplicity.
        response = tavily_client.search(query=query, search_depth="basic", max_results=3)
        # Combine the content of the results into a single text block
        return "\n".join([res["content"] for res in response["results"]])
    except Exception as e:
        return f"An error occurred during the web search: {e}"

# --- Agent Definition ---
WebSearchAgent = Agent(
    name="WebSearchAgent",
    model="gemini-2.0-flash-001",
    # This instruction is now extremely simple.
    instruction="""
    You are a simple search service. The user's prompt is a search query.
    Immediately call the `web_search` tool with the user's prompt as the `query`.
    Return the raw output from the tool directly. Do not add any extra text.
    """,
    tools=[web_search],
)

root_agent = WebSearchAgent