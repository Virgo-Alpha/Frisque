#!/bin/bash

# This script automates the setup of the full local development environment
# by opening services in new terminal tabs.

echo "🚀 Starting all local agent servers..."

# Start the OrchestratorAgent in a new terminal tab on port 8502
gnome-terminal --tab --title="OrchestratorAgent" -- bash -c 'echo "--- Starting OrchestratorAgent on port 8502 ---"; cd agents/orchestratoragent/ && make playground; exec bash'

# # Start the WebSearchAgent in a new terminal tab on port 8501
# gnome-terminal --tab --title="WebSearchAgent" -- bash -c 'echo "--- Starting WebSearchAgent on port 8501 ---"; cd agents/websearchagent/ && make playground; exec bash'

# # Start the JsonFormattingAgent in a new terminal tab on port 8503
# gnome-terminal --tab --title="JsonFormattingAgent" -- bash -c 'echo "--- Starting JsonFormattingAgent on port 8503 ---"; cd agents/jsonformattingagent/ && make playground; exec bash'

echo "✅ All agent servers have been launched in new terminal tabs."
echo "You can now start your main Django application with 'docker-compose up'."