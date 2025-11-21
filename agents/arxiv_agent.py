from textwrap import dedent

from agno.agent import Agent
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.anthropic import Claude
from agno.vectordb.pgvector import PgVector, SearchType
from agno.db.postgres import PostgresDb
from db.demo_db import demo_db
from db.url import get_db_url
from agno.tools.arxiv import ArxivTools
from tools.knowledge_tools import KnowledgeTools
from agno.os import AgentOS

# ============================================================================
# Setup knowledge base for storing Agno documentation
# ============================================================================

content_db = PostgresDb(id="arxiv-content", db_url=get_db_url())

knowledge = Knowledge(
    name="Agno Documentation",
    vector_db=PgVector(
        db_url=get_db_url(),
        table_name="arxiv_knowledge",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    contents_db=content_db,
)

# ============================================================================
# Description & Instructions
# ============================================================================
description = dedent(
    """\
    You are an ArXiv research assistant with full search capabilities.You are built using Agno - The best way to build AI Agents.
    """
)


instructions = dedent(
    """\
    You are an ArXiv Research Assistant with full search capabilities.
    You can search for academic papers on ArXiv and in your internal Knowledge Base.
    You can also use the `list_knowledge_content` tool to list the content in the Knowledge Base.
    You can use the `search_knowledge` tool to query the Knowledge Base for relevant papers.

    When a user asks a question, you must always first use the list content function to see what knowledge is available.
    Then based on the results, you can search the knowledge base for in depth information about the topic.
    If you dont find it in the knowledge base, you can use the Arxiv tools to search for the paper.

    If a relevant paper is found in the Knowledge Base, use its summary to answer the question.
    If the answer is found in the Knowledge Base, do NOT ask the user whether they want to add the paper—it is already stored.
    If the Knowledge Base does not contain a relevant paper, use the ArXiv search tools to look for one.
    After retrieving ArXiv results, ask the user if they want any of the papers added to the Knowledge Base.

    Before adding any paper to the Knowledge Base, you MUST:
        - Include the name parameter
        - Include the description parameter
        - Include the metadata parameter with ALL of the following: author, published_date, arxiv_id, url, categories
        - You are allowed, but not required, to add additional metadata to the paper if you think it is relevant.

    If a paper does not have a summary, you must generate one.
    When storing a paper, always use the PDF URL returned by ArXiv, not the abstract URL.
    Use the `add_arxiv_content` tool to add papers to the Knowledge Base.

    You can provide detailed paper summaries, insights, and support comprehensive literature reviews.
    You must always perform a search (either in the Knowledge Base, ArXiv or by Listing the content in the Knowledge Base) before answering any research question.
    Never answer a research question directly without first performing the appropriate search.
    When replying, keep your responses very professional and concise.
    Be structured, without emojis and dont be overly verbose.
    """
)

# instructions = dedent(
#     """\
#     Your mission is to provide comprehensive, developer-focused support for the Agno ecosystem.

#     Follow this structured process to ensure accurate and actionable responses:

#     1. **Analyze the request**
#         - Determine whether the query requires a knowledge lookup, code generation, or both.
#         - All concepts are within the context of Agno - you don't need to clarify this.

#     After analysis, immediately begin the search process (no need to ask for confirmation).

#     2. **Search Process**
#         - Use the `search_knowledge` tool to retrieve relevant concepts, code examples, and implementation details.
#         - Perform iterative searches until you've gathered enough information or exhausted relevant terms.

#     Once your research is complete, decide whether code creation is required.
#     If it is, ask the user if they'd like you to generate an Agent for them.

#     3. **Code Creation**
#         - Provide fully working code examples that can be run as-is.
#         - Always use `agent.run()` (not `agent.print_response()`).
#         - Include all imports, setup, and dependencies.
#         - Add clear comments, type hints, and docstrings.
#         - Demonstrate usage with example queries.

#         Example:
#         ```python
#         from agno.agent import Agent
#         from agno.tools.duckduckgo import DuckDuckGoTools

#         agent = Agent(tools=[DuckDuckGoTools()])

#         response = agent.run("What's happening in France?")
#         print(response)
#         ```
#     """
# )

# ============================================================================
# Create the Agent
# ============================================================================
arxiv_agent = Agent(
    name="ArXiv Research Assistant",
    model=Claude(id="claude-sonnet-4-5"),
    db=demo_db,
    tools=[ArxivTools(), KnowledgeTools(knowledge=knowledge, enable_list_content=True, enable_add_arxiv_content=True)],
    knowledge=knowledge,
    description=description,
    instructions=instructions,
    add_history_to_context=True,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    num_history_runs=5,
    markdown=True,
    enable_agentic_knowledge_filters=True,
)

# ************* Create AgentOS *************
agent_os = AgentOS(agents=[arxiv_agent])
app = agent_os.get_app()

# ************* Run AgentOS *************
if __name__ == "__main__":
    agent_os.serve(app="arxiv_agent:app", reload=True)
