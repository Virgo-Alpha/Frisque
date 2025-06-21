import os
import json
import uuid
import re
import requests
import logging

logger = logging.getLogger(__name__)


def call_orchestrator_agent(company_name: str) -> str:
    """
    Calls the OrchestratorAgent microservice and parses the streaming response
    to extract the final JSON output.
    """
    base_url = os.environ.get(
        "ORCHESTRATOR_AGENT_URL",
        "https://orchestratoragent-46904927368.africa-south1.run.app", 
    )

    print(f"-> Targeting Orchestrator at: {base_url}")
    print(f"-> Delegating research for '{company_name}' to the OrchestratorAgent...")

    user_id = "frisque-backend-user"
    app_name = "app"
    session_id = str(uuid.uuid4())

    session_url = f"{base_url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
    run_url = f"{base_url}/run_sse"

    try:
        # Step 1: Create the session (with empty body)
        requests.post(session_url, json={
            "new_message": {
                "role": "user",
                "parts": [{"text": company_name}]
            }
        }).raise_for_status()

        print(f"   -> Successfully created remote session: {session_id}")

        # Step 2: Run the orchestrator agent
        payload = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [{"text": company_name}]
            },
            "streaming": False
        }

        logger.info(f"run_payload: {payload}")
        print(f"   -> Sending prompt '{company_name}' to session...")

        run_response = requests.post(run_url, json=payload, stream=True)
        run_response.raise_for_status()

        # Streamed text accumulation
        full_text_response = ""
        for line in run_response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    try:
                        data = json.loads(decoded_line[6:])
                        if "content" in data and "parts" in data["content"]:
                            for part in data["content"]["parts"]:
                                if "text" in part:
                                    full_text_response += part["text"]
                    except json.JSONDecodeError:
                        continue

        if not full_text_response:
            return '{"error": "Agent returned an empty response."}'

        # Strip JSON from markdown ```json blocks if present
        match = re.search(r"```json\s*(\{.*?\})\s*```", full_text_response, re.DOTALL)
        if match:
            return match.group(1)

        return full_text_response

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"An exception occurred while calling the agent: {str(e)}"})
