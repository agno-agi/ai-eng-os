# AgentOS

Welcome to your AgentOS: a robust, production-ready application for serving agents, multi-agent teams and agentic workflows. It includes:

- An **AgentOS server** for serving agents, multi-agent teams and agentic workflows.
- A **PostgreSQL database** for storing agent sessions, knowledge, and memories.
- A set of **pre-built agents, teams and workflows** to use as a starting point.

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

We'll use sonnet 4.5 as the default model, please export the `ANTHROPIC_API_KEY` environment variable to get started.

```sh
export ANTHROPIC_API_KEY="YOUR_API_KEY_HERE"
```

Optional: Export the `OPENAI_API_KEY` and `EXA_API_KEY` environment variables to use OpenAI and Exa services:

```sh
export OPENAI_API_KEY="YOUR_API_KEY_HERE"
export EXA_API_KEY="YOUR_API_KEY_HERE"
```

Note: We are using OpenAI to create embeddings for the knowledge base. So, please export the `OPENAI_API_KEY` environment variable to use the Agno Knowledge Agent.

> [!TIP]
> You can use the `example.env` file as a template to create your own `.env` file.

## Starting the application

### Local Setup

Run the application using docker compose:

```sh
docker compose up -d
```

This command starts:

- The **AgentOS server**, running on [http://localhost:8000](http://localhost:8000).
- The **PostgreSQL database** for storing agent sessions, knowledge, and memories, accessible on `localhost:5432`.

Once started, you can:

- View the AgentOS server documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### Connect the AgnoUI to the AgentOS server

- Open the [Agno UI](https://os.agno.com)
- Login and add `http://localhost:8000` as a new AgentOS. You can call it `Local AgentOS` (or any name you prefer).

### Stop the application

When you're done, stop the application using:

```sh
docker compose down
```

### Cloud Setup

To deploy the application to Railway, run the following commands:

1. Login to Railway:

```sh
railway login
```

2. Deploy the application:

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
./scripts/railway_up.sh
```

This command will rebuild and redeploy the docker image to your Railway project.

### Deleting the application

To delete the application, run the following command:

```sh
railway down --service agent_os
railway down --service pgvector
```

Careful: This command will delete the AgentOS and PgVector database services from your Railway project.

### Connecting the AgnoUI to the AgentOS server

To connect the AgnoUI to the AgentOS server:

- Open the [Agno UI](https://os.agno.com)
- Create a new AgentOS by clicking on the `+` button in the top right corner.
- Enter the AgentOS URL and click on the `Connect` button.
- You can add a local endpoint from your dev setup. To add the railway endpoint, you will be provided with a coupon code during the workshop.

## Prebuilt Agents, Teams and Workflows

The `/agents` folder contains pre-built agents that you can use as a starting point.

- Web Search Agent: A simple agent that can search the web.
- Agno Assist: An Agent that can help answer questions about Agno.
  - Important: Make sure to load the `agno_assist` knowledge base before using this agent by running `docker exec -it mb-agent-os-agent-os-1 python -m agents.agno_knowledge_agent
`. Running this script will add the Agno documentation to the knowledge base.
- Finance Agent: An agent that uses the YFinance API to get stock prices and financial data.
- Research Agent: An agent that can search the web for information.
- Memory Manager: An agent that can manage the memory of the agents.
- YouTube Agent: An agent that can search YouTube for videos and answer questions about them.

The `/teams` folder contains pre-built teams that you can use as a starting point.

- Finance Team: A team of agents that can work together to analyze financial data.

The `/workflows` folder contains pre-built workflows that you can use as a starting point.

- Research Workflow: A workflow that can research information from multiple sources simultaneously.

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
- 🐛 **[Report an Issue](https://github.com/agno-agi/agent-api/issues)** on GitHub if you find a bug or have a feature request.
