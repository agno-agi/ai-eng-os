# AgentOS

Welcome to your AgentOS: a robust, production-ready application for serving agents, multi-agent teams, and agentic workflows.

It includes:

- An **AgentOS server** for serving agents, multi-agent teams and agentic workflows.
- A **PostgreSQL database** for storing agent sessions, knowledge, and memories.
- A set of **pre-built Agents, Teams and Workflows** to use as a starting point.

For more information, checkout [Agno](https://agno.link/gh) and give it a ⭐️

---

## TL;DR – Get Running Quickly

If you just want to try this out locally:

1. **Install Docker Desktop** and make sure it is running.
2. **Clone this repo** and `cd` into it.
3. **Set your API keys** (at least `ANTHROPIC_API_KEY`, and `OPENAI_API_KEY` if you want the knowledge agent).
4. **Start everything** with `docker compose up -d`.
5. **Open the docs** at `http://localhost:8000/docs`.
6. **Connect Agno UI** to `http://localhost:8000` at [Agno UI](https://os.agno.com).

Details for each step are below.

---

## 1. Environments You Can Use

This repository lets you run AgentOS in two environments:

- **Local** using [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Cloud** using [Railway](https://railway.app)

Make sure Docker Desktop is installed and running. Install Railway CLI only if you plan to deploy to the cloud.

---

## 2. Clone the repo

git clone https://github.com/agno-agi/ai-eng-os.git
cd ai-eng-os---

## 3. Configure API keys

We'll use Sonnet 4.5 as the default model, so you must export the `ANTHROPIC_API_KEY` environment variable:

export ANTHROPIC_API_KEY="YOUR_API_KEY_HERE"Optionally, export the `OPENAI_API_KEY` and `EXA_API_KEY` environment variables to use OpenAI and Exa services:

export OPENAI_API_KEY="YOUR_API_KEY_HERE"
export EXA_API_KEY="YOUR_API_KEY_HERE"**Note:** OpenAI is used to create embeddings for the knowledge base. To use the Agno Knowledge Agent, you **must** set `OPENAI_API_KEY`.

> [!TIP]
> You can use the `example.env` file as a template to create your own `.env` file.

---

## 4. Run the application locally

### Start with Docker Compose

Run the application using Docker Compose:

docker compose up -dThis command starts:

- The **AgentOS server**, running on [http://localhost:8000](http://localhost:8000).
- The **PostgreSQL database** for storing agent sessions, knowledge, and memories, accessible on `localhost:5432`.

Once started, you can:

- View the AgentOS server documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### Connect the AgnoUI to the AgentOS server

- Open the [Agno UI](https://os.agno.com)
- Login and add `http://localhost:8000` as a new AgentOS. You can call it `Local AgentOS` (or any name you prefer).

### Stop the application

When you're done, stop the application using:

docker compose down---

## 5. Cloud deployment (Railway)

To deploy the application to Railway, run the following commands:

1. **Login to Railway**:

railway login2. **Deploy the application**:

./scripts/railway_up.shThis command will:

- Create a new Railway project.
- Deploy a PgVector database service to your Railway project.
- Build and deploy the Docker image to your Railway project.
- Set environment variables in your AgentOS service.
- Create a new domain for your AgentOS service.

### Updating the application on Railway

To update the application, run:

railway up --service agent_os -dThis rebuilds and redeploys the Docker image to your Railway service.

### Deleting the application from Railway

To delete the application, run:

railway down --service agent_os
railway down --service pgvector**Careful:** This deletes the AgentOS and PgVector database services from your Railway project.

### Connecting AgnoUI to a Railway AgentOS

To connect the AgnoUI to the AgentOS server running on Railway:

- Open the [Agno UI](https://os.agno.com)
- Create a new AgentOS by clicking on the `+` button in the top right corner.
- Enter the Railway AgentOS URL and click on the `Connect` button.
- You can also add a local endpoint from your dev setup. To add the Railway endpoint, you may be provided with a coupon code during the workshop.

---

## 6. Prebuilt Agents, Teams and Workflows

This repo includes several ready-to-use building blocks so you can try things quickly.

### Agents (`/agents`)

- **Web Search Agent**: A simple agent that can search the web.
- **Agno Assist**: An agent that can help answer questions about Agno.
  - **Important:** Load the `agno_assist` knowledge base before using this agent by running:

   
    docker exec -it mb-agent-os-agent-os-1 python -m agents.agno_knowledge_agent
        This script adds the Agno documentation to the knowledge base.

- **Finance Agent**: Uses the YFinance API to get stock prices and financial data.
- **Research Agent**: Searches the web for information.
- **Memory Manager**: Manages the memory of the agents.
- **YouTube Agent**: Searches YouTube for videos and answers questions about them.

### Teams (`/teams`)

- **Finance Team**: A team of agents that work together to analyze financial data.

### Workflows (`/workflows`)

- **Research Workflow**: Researches information from multiple sources simultaneously.

---

## 7. Development Setup (for contributors)

If you want to work on the codebase locally (beyond just running with Docker), set up a virtual environment.

### Install `uv`

We use `uv` for Python environment and package management. Install it by following the [`uv` documentation](https://docs.astral.sh/uv/#getting-started) or use the command below for Unix-like systems:

curl -LsSf https://astral.sh/uv/install.sh | sh### Create Virtual Environment & Install Dependencies

Run the `dev_setup.sh` script. This will create a virtual environment and install project dependencies:

./scripts/dev_setup.sh### Activate Virtual Environment

Activate the created virtual environment:

source .venv/bin/activate(On Windows, the command might differ, e.g., `.venv\Scripts\activate`)

---

## 8. Managing Python Dependencies

If you need to add or update Python dependencies:

### Modify `pyproject.toml`

Add or update your desired Python package dependencies in the `[dependencies]` section of the `pyproject.toml` file.

### Generate `requirements.txt`

The `requirements.txt` file is used to build the application image. After modifying `pyproject.toml`, regenerate `requirements.txt` using:

./scripts/generate_requirements.shTo upgrade all existing dependencies to their latest compatible versions, run:

./scripts/generate_requirements.sh upgrade### Rebuild Docker Images

Rebuild your Docker images to include the updated dependencies:

docker compose up -d --build---

## 9. Community & Support

Need help, have a question, or want to connect with the community?

- 📚 **[Read the Agno Docs](https://docs.agno.com)** for more in-depth information.
- 💬 **Chat with us on [Discord](https://agno.link/discord)** for live discussions.
- ❓ **Ask a question on [Discourse](https://agno.link/community)** for community support.
- 🐛 **[Report an Issue](https://github.com/agno-agi/agent-api/issues)** on GitHub if you find a bug or have a feature request.