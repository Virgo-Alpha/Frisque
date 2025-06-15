import os
import json
import uuid
import re
import requests
import logging

logger = logging.getLogger(__name__)


def call_orchestrator_agent(company_name: str) -> str:
    """
    Calls the OrchestratorAgent microservice and robustly parses the
    streaming response to extract the final JSON output.
    """
    base_url = os.environ.get(
        "ORCHESTRATOR_AGENT_URL",
        "http://host.docker.internal:8502",
        # "https://orchestratoragent-46904927368.africa-south1.run.app"
        )
    print(f"-> Targeting Orchestrator at: {base_url}")
    print(f"-> Delegating research for '{company_name}' to the OrchestratorAgent...")

    user_id = "frisque-backend-user"
    session_id = str(uuid.uuid4())
    session_url = f"{base_url}/apps/app/users/{user_id}/sessions/{session_id}"
    run_url = f"{base_url}/run_sse"

    try:
        # Step 1: Create the session.
        create_session_response = requests.post(session_url, json={
            "new_message": {"parts": [{"text": company_name}]}
        })
        create_session_response.raise_for_status()
        print(f"   -> Successfully created remote session: {session_id}")

        # Step 2: Run the prompt in the new session.
        new_message_payload = {"parts": [{"text": company_name}]}
        run_payload = {
            "app_name": "app",
            "user_id": user_id,
            "session_id": session_id,
            "new_message": new_message_payload,
        }
        logger.info(f"run_payload: {run_payload}")  # Debug log
        
        print(f"   -> Sending prompt '{company_name}' to session...")
        run_response = requests.post(run_url, json=run_payload, stream=True)
        run_response.raise_for_status()
        
        # --- ROBUST STREAM PARSING LOGIC ---
        full_text_response = ""
        for line in run_response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    try:
                        data = json.loads(decoded_line[6:])
                        # The final agent answer is in a part with a 'text' key.
                        # We concatenate all text parts to build the full response.
                        if "content" in data and "parts" in data["content"]:
                            text_part = data["content"]["parts"][0].get("text")
                            if text_part:
                                full_text_response += text_part
                    except json.JSONDecodeError:
                        continue
        
        if not full_text_response:
            return '{"error": "Agent returned an empty response."}'

        # Clean up the final response by removing markdown backticks if they exist
        match = re.search(r"```json\s*(\{.*\})\s*```", full_text_response, re.DOTALL)
        if match:
            return match.group(1)
        
        return full_text_response

    except requests.exceptions.RequestException as e:
        return f'{{"error": "An exception occurred while calling the agent: {e}"}}'