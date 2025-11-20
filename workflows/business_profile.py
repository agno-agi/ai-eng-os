from textwrap import dedent
from typing import Dict, List, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.parallel import ParallelTools
from agno.workflow import Step, Workflow
from agno.workflow.parallel import Parallel
from agno.workflow.step import StepInput, StepOutput
from pydantic import BaseModel

from db.demo_db import demo_db

# ============================================================================
# Create Schemas
# ============================================================================


class BusinessProfileInput(BaseModel):
    name: str
    website: str
    description: Optional[str] = None


class BusinessProfileOutput(BaseModel):
    name: str
    website: Optional[str] = None
    description: Optional[str] = None

    industry: Optional[str] = None
    founded_year: Optional[int] = None
    employee_count: Optional[int] = None
    revenue: Optional[str] = None

    headquarters: Optional[str] = None
    locations: Optional[List[str]] = None

    linkedin: Optional[str] = None
    twitter: Optional[str] = None

    key_people: Optional[List[str]] = None
    contact_email: Optional[str] = None

    competitors: Optional[List[str]] = None


# ============================================================================
# Create Search Agents
# ============================================================================

web_researcher = Agent(
    name="Web Researcher",
    role="Search the web for current information and sources",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[DuckDuckGoTools()],
    description=dedent("""\
        You are the Web Researcher — an agent that searches the web for up-to-date information,
        news articles, and credible sources on any topic.
        """),
    instructions=dedent("""\
        1. Search the web for recent and relevant information on the given topic.
        2. Prioritize credible sources like news sites, official documentation, and reputable publications.
        3. Gather diverse perspectives and factual information for the given business.
        4. Summarize findings with clear citations and links.
        """),
    add_history_to_context=True,
    markdown=True,
    db=demo_db,
)

parallel_search_agent = Agent(
    name="Parallel Search Agent",
    role="Perform deep semantic search for high-quality content",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[ParallelTools(enable_search=True, enable_extract=True)],
    description=dedent("""\
        You are the Parallel Researcher — an agent that uses semantic search to find
        high-quality, relevant content from across the web for the given business profile.
        """),
    instructions=dedent("""\
        1. Use Parallel's search and extract tools to find highly relevant, quality content.
        2. Focus on authoritative sources, in-depth articles, and expert analysis for the given business profile.
        3. Provide context and summaries of the most valuable findings.
        4. Include links to all sources.
        5. Do not include more than 5 search queries for the parallel_search tool.
        """),
    add_history_to_context=True,
    markdown=True,
    db=demo_db,
)

# ============================================================================
# Create Writer and Reviewer Agents
# ============================================================================
writer = Agent(
    name="Business Profile Writer",
    role="Synthesize search results into a business profile",
    model=OpenAIChat(id="gpt-5"),
    output_schema=BusinessProfileOutput,
    description=dedent("""\
        You are the Business Profile Writer — an agent that synthesizes search results into a business profile.
        """),
    instructions=dedent("""\
        **Input:** The search results from the Search Phase.
        **Output:** A well-structured and engaging business profile.
        **Instructions:**
        1. Analyze and consolidate all the search results that you have received.
        2. Identify key themes, insights, and important details for the given business profile.
        3. Structure the content logically with clear sections and sub-sections.
        4. Write in a clear, engaging style appropriate for the business profile.
        5. Include relevant citations and links from the search results.
        """),
    add_history_to_context=True,
    markdown=True,
    db=demo_db,
)


async def consolidate_business_profile_step_function(input: StepInput) -> StepOutput:
    """Consolidate the search results into a business profile"""
    # Get all previous step outputs
    previous_step_outputs: Optional[Dict[str, StepOutput]] = input.previous_step_outputs
    # Get the parallel step output
    parallel_step_output: Optional[StepOutput] = (
        previous_step_outputs.get("Search Phase") if previous_step_outputs else None
    )
    # Get the list of step outputs from the parallel step
    parallel_step_output_list: Optional[List[StepOutput]] = parallel_step_output.steps if parallel_step_output else None
    # Create the business profile content by combining the content of the different step outputs
    business_profile_content = f"Please use the following extracted search results create a comprehensive business profile for the business profile input: {str(input.input)}. \n\n"
    if parallel_step_output_list and len(parallel_step_output_list) > 0:
        for step_output in parallel_step_output_list:
            business_profile_content += f"## {step_output.step_name} \n\n{step_output.content}\n\n"

        return StepOutput(content=business_profile_content, success=True)

    return StepOutput(content="No business profile content found", success=False)


# ============================================================================
# Create Workflow Steps
# ============================================================================
web_research_step = Step(
    name="Web Research",
    agent=web_researcher,
)
parallel_search_step = Step(
    name="Parallel Search",
    agent=parallel_search_agent,
)
search_steps: List[Step] = [web_research_step, parallel_search_step]


business_profile_consolidation_step = Step(
    name="Consolidate Business Profile",
    executor=consolidate_business_profile_step_function,
)

writer_step = Step(
    name="Business Profile Writer",
    agent=writer,
)

# ============================================================================
# Create the Workflow
# ============================================================================
business_profile_workflow = Workflow(
    name="Business Profile Workflow",
    description=dedent("""\
        A parallel workflow that searches the web for information from multiple sources simultaneously,
        then synthesizes the information into a business profile for the given business.
        """),
    input_schema=BusinessProfileInput,
    steps=[
        Parallel(*search_steps, name="Search Phase"),  # type: ignore
        business_profile_consolidation_step,
        writer_step,
    ],
    db=demo_db,
)
