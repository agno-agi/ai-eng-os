# AgentOS

Welcome to your AgentOS: a robust, production-ready application for serving agents, multi-agent teams and agentic workflows. It includes:

- An **AgentOS server** for serving agents, multi-agent teams and agentic workflows.
- A **PostgreSQL database** for storing agent sessions, knowledge, and memories.
- A set of **pre-built Agents, Teams and Workflows** to use as a starting point.

For more information, checkout [Agno](https://agno.link/gh) and give it a ⭐️

## Quickstart

Follow these steps to get your AgentOS up and running. This repository allows you to deploy your AgentOS in two environments:

- Local using [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Cloud using [Railway](https://railway.app)

Make sure Docker Desktop is installed and running. And Railway CLI is installed for cloud deployment.

Follow these steps to get your AgentOS up and running:

### Clone the repo

```sh
git clone https://github.com/agno-agi/ai-eng-os.git
cd ai-eng-os
```

### Configure API keys

For this workshop, we'll be using OpenAI and Anthropic models, please export the `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` environment variables to get started. We'll also be using Parallel Search to search and extract content from the web. To use Parallel Search, you need to export the `PARALLEL_API_KEY` environment variable. The API keys will be provided to you during the workshop.

```sh
export OPENAI_API_KEY="YOUR_API_KEY_HERE"
export ANTHROPIC_API_KEY="YOUR_API_KEY_HERE"
export PARALLEL_API_KEY="YOUR_API_KEY_HERE"
```

> [!TIP]
> You can use the `example.env` file as a template to create your own `.env` file. But you will still need to export the API keys.

## Starting the application

### Local Setup

Run the application using docker compose:

```sh
docker compose up --build -d
```

This command builds the Docker image and starts the application:

- The **AgentOS server**, running on [http://localhost:8000](http://localhost:8000).
- The **PostgreSQL database** for storing agent sessions, knowledge, and memories, accessible on `localhost:5432`.

Once started, you can:

- View the AgentOS server documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### Connect the AgentOS UI to the AgentOS server

- Open the [AgentOS UI](https://os.agno.com)
- Login and add `http://localhost:8000` as a new AgentOS. You can call it `Local AgentOS` (or any name you prefer).

### Stop the application

When you're done, stop the application using:

```sh
docker compose down
```

### Adding knowledge to Agno Knowledge Agent locally

To add knowledge to the Agno Knowledge Agent, run the following command:

```sh
docker exec -it ai-eng-os-agent-os-1 python -m agents.agno_knowledge_agent
```

This command will add the Agno documentation to the knowledge base.

### Adding F1 data and loading knowledge to SQL Analysis Team locally

To add F1 data and load knowledge to the SQL Analysis Team, run the following commands:

```sh
docker exec -it ai-eng-os-agent-os-1 python -m scripts.load_f1_data
docker exec -it ai-eng-os-agent-os-1 python -m teams.data_analysis_team
```

The `load_f1_data` script will add the F1 data to the database and the `data_analysis_team` script will load the knowledge to the SQL Analysis Team.

### Cloud Setup

To deploy the application to Railway, run the following commands:

1. Install Railway CLI:

```sh
brew install railway
```

More information on how to install Railway CLI can be found [here](https://docs.railway.com/guides/cli).

2. Login to Railway:

```sh
railway login
```

3. Deploy the application:

```sh
./scripts/railway_up.sh
```

This command will:

- Create a new Railway project.
- Deploy a PgVector database service to your Railway project.
- Build and deploy the docker image to your Railway project.
- Set environment variables in your AgentOS service.
- Create a new domain for your AgentOS service.

### Updating the application

To update the application, run the following command:

```sh
railway up --service agent_os -d
```

This rebuilds and redeploys the Docker image to your Railway service.

### Deleting the application

To delete the application, run the following command:

```sh
railway down --service agent_os
railway down --service pgvector
```

Careful: This command will delete the AgentOS and PgVector database services from your Railway project.

### Adding Knowledge on Railway

To add knowledge to the Agno Knowledge Agent, run the following command:

```sh
railway ssh --service agent_os
```

This command will open a ssh session to the AgentOS service.

Once you are in the ssh session, you can run the following command to add knowledge to the Agno Knowledge Agent:

```sh
python -m agents.agno_knowledge_agent
```

To add knowledge to the SQL Analysis Team, run the following commands:

```sh
python -m scripts.load_f1_data.py
python -m teams.data_analysis_team
```

### Connecting the AgnoUI to the AgentOS server

To connect the AgentOS UI to the AgentOS server:

- Open the [AgentOS UI](https://os.agno.com)
- Create a new AgentOS by clicking on the `+` button in the top left corner.
- Enter the AgentOS URL and click on the `Connect` button.
- You can add a local endpoint from your dev setup. To add the railway endpoint, you will be provided with a coupon code during the workshop.

## Prebuilt Agents, Teams and Workflows

The `/agents` folder contains pre-built agents that you can use as a starting point.

- **Web Search Agent**: A simple agent that can search the web.
- **Agno Assist**: An agent that can help answer questions about Agno.

  - **Important:** Load the `agno_assist` knowledge base before using this agent by running:

    ```sh
    docker exec -it ai-eng-os-agent-os-1 python -m agents.agno_knowledge_agent
    ```

    This script adds the Agno documentation to the knowledge base.

- **Finance Agent**: Uses the YFinance API to get stock prices and financial data.
- **Research Agent**: Searches the web for information.
- **Memory Manager**: Manages the memory of the agents.
- **YouTube Agent**: Searches YouTube for videos and answers questions about them.
- **ArXiv Agent**: Searches ArXiv for papers and answers questions about them.

The `/teams` folder contains pre-built teams that you can use as a starting point.

- **Finance Team**: A team of agents that work together to analyze financial data.
- **Data Analysis Team**: A specialized team that combines SQL querying, data analysis, and report generation for comprehensive insights.

The `/workflows` folder contains pre-built workflows that you can use as a starting point.

- **Research Workflow**: Researches information from multiple sources simultaneously regarding a given topic and synthesizes the information into a report.
- **Business Profile Workflow**: Creates a business profile from a given business name, website and description.
- **Invoice Processing Workflow**: Processes invoices from a given PDF URL and extracts the data in a structured format.

## Development Setup

To setup your local virtual environment:

### Install `uv`

We use `uv` for python environment and package management. Install it by following the the [`uv` documentation](https://docs.astral.sh/uv/#getting-started) or use the command below for unix-like systems:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Create Virtual Environment & Install Dependencies

Run the `dev_setup.sh` script. This will create a virtual environment and install project dependencies:

```sh
./scripts/dev_setup.sh
```

### Activate Virtual Environment

Activate the created virtual environment:

```sh
source .venv/bin/activate
```

(On Windows, the command might differ, e.g., `.venv\Scripts\activate`)

## Managing Python Dependencies

If you need to add or update python dependencies:

### Modify pyproject.toml

Add or update your desired Python package dependencies in the `[dependencies]` section of the `pyproject.toml` file.

### Generate requirements.txt

The `requirements.txt` file is used to build the application image. After modifying `pyproject.toml`, regenerate `requirements.txt` using:

```sh
./scripts/generate_requirements.sh
```

To upgrade all existing dependencies to their latest compatible versions, run:

```sh
./scripts/generate_requirements.sh upgrade
```

### Rebuild Docker Images

Rebuild your Docker images to include the updated dependencies:

```sh
docker compose up -d --build
```

## Community & Support

Need help, have a question, or want to connect with the community?

- 📚 **[Read the Agno Docs](https://docs.agno.com)** for more in-depth information.
- 💬 **Chat with us on [Discord](https://agno.link/discord)** for live discussions.
- ❓ **Ask a question on [Discourse](https://agno.link/community)** for community support.
- 🐛 **[Report an Issue](https://github.com/agno-agi/agno/issues)** on GitHub if you find a bug or have a feature request.
