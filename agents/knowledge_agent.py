from textwrap import dedent

from agno.agent import Agent
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.anthropic import Claude
from agno.vectordb.pgvector import PgVector, SearchType

from db.demo_db import demo_db
from db.url import get_db_url
from tools.knowledge_tools import KnowledgeTools

# ============================================================================
# Setup knowledge base for storing Agno documentation
# ============================================================================

knowledge = Knowledge(
    name="Agno Knowledge",
    vector_db=PgVector(
        db_url=get_db_url(),
        table_name="general_knowledge",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    contents_db=demo_db,
)

# ============================================================================
# Description & Instructions
# ============================================================================

description = dedent(
    """\
    You are a general knowledge agent with full search capabilities. You are built using Agno - The best way to build AI Agents.
    """
)

instructions = dedent(
    """\
    Your mission is to provide users with support to manage their knowledge base.

    Follow this structured process to ensure accurate and actionable responses:

    1. **Analyze the request**
        - Determine whether the query requires a knowledge lookup, or adding content to the knowledge base.
        - All concepts are within the context of the knowledge base - you don't need to clarify this.

    After analysis, immediately begin the appropriate action.

    2. **Add Content to the Knowledge Base**
        - Use the `add_url_content` tool to add content to the knowledge base.
        - Provide the url of the content to add to the knowledge base.
        - Provide a name for the content.
        - Provide a description for the content.
        - Provide the metadata for the content. If no metadata is provided, you can create it based on the content.

        Example:
        ```
        Add the content from the url https://www.google.com to the knowledge base.
        ```
    """
)

# ============================================================================
# Create the Agent
# ============================================================================

general_knowledge_agent = Agent(
    name="General Knowledge Agent",
    id="general-knowledge-agent",
    model=Claude(id="claude-sonnet-4-5"),
    tools=[KnowledgeTools(knowledge=knowledge, enable_add_url_content=True, enable_list_content=True)],
    knowledge=knowledge,
    description=description,
    instructions=instructions,
    add_history_to_context=True,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    num_history_runs=5,
    markdown=True,
    db=demo_db,
)
