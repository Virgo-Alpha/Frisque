# Frisque

### AI-Powered Due Diligence Platform

Frisque is an agentic AI system designed to revolutionize the venture capital due diligence process. It automates and augments critical research, culminating in comprehensive investment memos and actionable insights. Frisque comes from the French words _Faux Risque_ meaning `false risk`, which is what we aim to eliminate in the due diligence process.

Read more about Frisque in our [blog post](https://dev.to/virgoalpha/frisque-using-ai-agents-for-due-diligence-4old).

## The Problem

Venture Capital (VC) firms dedicate a significant amount of time and resources to conducting due diligence on potential startup investments. This process is critical for assessing a startup's viability and growth potential, but it is incredibly time-intensive. Given that a fund's returns often come from a small percentage of its investments, streamlining this process is crucial for success.

## Our Solution

Frisque is an AI-powered platform that significantly reduces the time and effort VCs spend on initial due diligence while improving the depth and breadth of insights. The platform uses a system of specialized AI agents that can:

  * Perform targeted research on a company based on inputs like pitch decks, financial documents, and founder profiles.
  * Analyze technology stacks, market trends, legal documents, and even social media sentiment.
  * Synthesize all findings into a structured investment memo and a summary dashboard.
  * Provide real-time updates and notifications on scan progress and completion.

## Tech Stack

Frisque is built with a modern, scalable technology stack designed for asynchronous workloads and intelligent processing.

| Category             | Technology                                                                          |
| -------------------- | ----------------------------------------------------------------------------------- |
| **Backend** | Django                                                                   |
| **AI Agents** | Google Agent Development Kit (ADK)                                       |
| **Database** | PostgreSQL                                                               |
| **Task Queue** | Celery                                                                   |
| **Message Broker** | RabbitMQ                                                                 |
| **Real-time Comms** | Django Channels                                                         |
| **Containerization** | Docker, Docker Compose                                                    |
| **Cloud Storage** | Google Cloud Storage (GCS)                                              |
| **Infrastructure** | Terraform                                                                |
| **Cloud Platform** | Google Cloud Platform (GCP)                                              |

-----

## Getting Started

Follow these instructions to get the Frisque development environment up and running on your local machine.

### Prerequisites

You must have **Docker** and **Docker Compose** installed on your system.

  * [Install Docker Engine](https://docs.docker.com/engine/install/)
  * [Install Docker Compose](https://docs.docker.com/compose/install/)

### Installation & Setup

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/Virgo-Alpha/frisque.git
    cd frisque
    ```

2.  **Run the Application**
    This single command will build the Docker images, create all the necessary services (web, database, broker, worker), and start the entire application stack.

    ```bash
    docker-compose up --build
    ```

    You will see logs from all the services in your terminal. Wait for the database to initialize and the web server to start.

3.  **Access the Application**
    Once the services are running, open your web browser and navigate to:
    **`http://localhost:8000`**

    You should see the default Django "Congratulations\!" page. This confirms that the entire stack is working correctly\!

## Agents Configuration

For agents instructions, please check out the file agents/instructions.md

-----

## Development Workflow

To ensure a consistent development environment, **all commands should be run inside the `web` container** using `docker-compose exec`.

### How to Run Management Commands

Here are some examples of common `manage.py` commands.

  * **Apply Database Migrations**

    ```bash
    docker-compose exec web python manage.py migrate
    ```

  * **Create a Superuser**

    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

  * **Open a Django Shell**

    ```bash
    docker-compose exec web python manage.py shell
    ```

  * **Enter a Bash Shell Inside the Container**
    If you want an interactive shell inside the `web` container to look around:

    ```bash
    docker-compose exec web bash
    ```

## Testing the Application

  * **Runtests while inside the application Inside the Container**
    While inside the web container,you can run the command `pytest`

  * **Runtests script**
    While outside the web container, you can run the command:
    
    ```bash
    ./run_tests.sh
    ```

  You can also run the full command below:
  
```bash
docker-compose exec web pytest
```


### Stopping the Environment

To stop all running services, press `Ctrl+C` in the terminal where `docker-compose up` is running.

To stop the services and remove the containers (useful for a clean restart), run:

```bash
docker-compose down
```