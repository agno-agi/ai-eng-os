import json
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.team.team import Team
from agno.tools.reasoning import ReasoningTools
from agno.tools.sql import SQLTools
from agno.vectordb.pgvector import PgVector, SearchType

from db.demo_db import demo_db
from db.url import get_db_url

# ============================================================================
# Setup F1 Knowledge Base
# ============================================================================
data_dir = Path(__file__).parent.parent.joinpath("data")

f1_knowledge = Knowledge(
    name="F1 Racing Data",
    vector_db=PgVector(
        db_url=get_db_url(),
        table_name="f1_metadata",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    contents_db=demo_db,
)

# Semantic model describing F1 tables
semantic_model = {
    "tables": [
        {
            "table_name": "constructors_championship",
            "table_description": "Constructor's championship standings from 1958-2020, capturing team performance.",
            "use_case": "Use for constructor/team championship data and performance analysis over years.",
        },
        {
            "table_name": "drivers_championship",
            "table_description": "Driver's championship standings from 1950-2020, detailing positions, teams, and points.",
            "use_case": "Use for driver championship data and detailed performance analysis.",
        },
        {
            "table_name": "fastest_laps",
            "table_description": "Fastest laps recorded in races from 1950-2020, including driver and team details.",
            "use_case": "Use for fastest lap data, including driver, team, and lap time information.",
        },
        {
            "table_name": "race_results",
            "table_description": "Race data for each F1 race from 1950-2020, including positions, drivers, teams, points.",
            "use_case": "Use for detailed race results, driver standings, teams, and performance data.",
        },
        {
            "table_name": "race_wins",
            "table_description": "Race win data from 1950-2020, detailing venue, winner, team, and race duration.",
            "use_case": "Use for race winner data, their teams, and race conditions analysis.",
        },
    ]
}
semantic_model_str = json.dumps(semantic_model, indent=2)

# ============================================================================
# Create SQL Analysis Agents
# ============================================================================

sql_query_agent = Agent(
    name="SQL Query Agent",
    role="Database query specialist - translate natural language to SQL",
    model=OpenAIChat(id="gpt-5-mini"),
    knowledge=f1_knowledge,
    search_knowledge=True,
    tools=[SQLTools(db_url=get_db_url())],
    description=dedent("""\
        You are the SQL Query Agent — a database specialist who translates natural language
        questions into SQL queries, executes them safely, and retrieves data from PostgreSQL databases.
        """),
    instructions=dedent("""\
       1) Identify Tables (use semantic_model)
          - Check semantic_model for relevant tables.
          - Use search_knowledge_base(table_name) for metadata and sample queries.
          - Follow table rules if provided.

       2) Query Construction
          - Think through query logic; use chain of thought.
          - Write syntactically correct PostgreSQL.
          - Add LIMIT unless user asks for all results.
          - Account for duplicates and null values.

       3) Execute & Analyze
          - Run query using run_sql_query (no semicolon).
          - Analyze results for correctness and completeness.
          - Show SQL used; explain findings.

       4) Rules
          - Always use search_knowledge_base before querying.
          - Never delete data or abuse system.
       """),
    additional_context=dedent("""\
        The semantic_model contains information about F1 tables and their usage.
        <semantic_model>
        """)
    + semantic_model_str
    + dedent("""
        </semantic_model>
        
        <sample_queries>
        Here are sample query patterns for reference:
        
        -- Most race wins by a driver
        SELECT name, COUNT(*) AS win_count
        FROM race_wins
        GROUP BY name
        ORDER BY win_count DESC
        LIMIT 10;
        
        -- Championship winners with their race wins per year
        SELECT dc.year, dc.name AS champion_name, COUNT(rw.name) AS race_wins
        FROM drivers_championship dc
        JOIN race_wins rw ON dc.name = rw.name 
          AND dc.year = EXTRACT(YEAR FROM TO_DATE(rw.date, 'DD Mon YYYY'))
        WHERE dc.position = '1'
        GROUP BY dc.year, dc.name
        ORDER BY dc.year;
        
        -- Constructor performance with wins in a year
        WITH race_wins_2019 AS (
            SELECT team, COUNT(*) AS wins
            FROM race_wins
            WHERE EXTRACT(YEAR FROM TO_DATE(date, 'DD Mon YYYY')) = 2019
            GROUP BY team
        )
        SELECT cp.team, cp.position, COALESCE(rw.wins, 0) AS wins
        FROM constructors_championship cp
        LEFT JOIN race_wins_2019 rw ON cp.team = rw.team
        WHERE cp.year = 2019
        ORDER BY cp.position;
        
        -- Most Constructor Championships
        SELECT team, COUNT(*) AS championship_wins
        FROM constructors_championship
        WHERE position = 1
        GROUP BY team
        ORDER BY championship_wins DESC
        LIMIT 5;
        </sample_queries>
        """),
    add_history_to_context=True,
    add_datetime_to_context=True,
    markdown=True,
    db=demo_db,
)

data_analyst_agent = Agent(
    name="Data Analyst Agent",
    role="Data analysis specialist - extract insights from query results",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[ReasoningTools()],
    description=dedent("""\
        You are the Data Analyst Agent — an analytical expert who examines query results,
        identifies patterns and trends, and extracts actionable business insights.
        """),
    instructions=dedent("""\
       1) Data Examination
          - Review query results for structure, values, and quality issues.
          - Calculate key statistics (mean, median, distributions).
          - Identify outliers, anomalies, and trends.

       2) Pattern Recognition
          - Spot temporal trends (daily, weekly, seasonal).
          - Detect usage patterns, clustering, and unusual changes.
          - Use reasoning tools for complex relationships.

       3) Insight Generation
          - Extract 3-5 key insights in business terms.
          - Explain what data shows (descriptive) and why (diagnostic).
          - Identify opportunities and risks; highlight actions.

       4) Framework: What shows? Why? What next? What to do?
       """),
    add_history_to_context=True,
    add_datetime_to_context=True,
    markdown=True,
    db=demo_db,
)

report_generator_agent = Agent(
    name="Report Generator Agent",
    role="Report specialist - present data findings clearly",
    model=Claude(id="claude-sonnet-4-5"),
    description=dedent("""\
        You are the Report Generator Agent — a communication expert who transforms
        data analysis into clear, business-friendly reports that executives can act on.
        """),
    instructions=dedent("""\
       1) Report Structure
          - Executive Summary: Key findings in 2-3 sentences.
          - Key Metrics: Important numbers with context.
          - Insights: What data means for business.
          - Recommendations: Actionable next steps.

       2) Presentation
          - Use clear, non-technical language; format numbers (K, M, B).
          - Include tables for comparative data; use bullets.
          - Start with most important insight; build logical narrative.

       3) Quality
          - Connect findings to business impact.
          - Prioritize recommendations by urgency.
          - Make it scannable and action-oriented for executives.
       """),
    add_history_to_context=True,
    add_datetime_to_context=True,
    markdown=True,
    db=demo_db,
)


# ============================================================================
# Team Description & Instructions
# ============================================================================
description = dedent("""\
    You are the SQL Analysis Team — a coordinated unit of data specialists who work together
    to answer business questions using database analytics.
    
    Your team combines SQL expertise, data analysis, and business communication to deliver
    insights that drive decisions.
    """)

instructions = dedent("""\
    1) Planning & Routing
       - Parse user's data question; identify tables/metrics needed.
       - Route queries to SQL Query Agent (SQLTools).
       - Route analysis to Data Analyst Agent (ReasoningTools).
       - Route reporting to Report Generator Agent.
       - Sequential flow: Query → Analysis → Reporting.

    2) Coordination
       - Delegate clearly to each specialist; avoid duplication.
       - Synthesize outputs into coherent response (don't concatenate).

    3) Quality Standards
       - Ensure data accuracy with timestamps.
       - Provide context for all numbers; use tables.
       - Make insights actionable and executive-friendly.

    4) Output
       - Return only final consolidated report (no intermediate outputs).
       - Include: summary, findings, insights, recommendations.
    """)


# ============================================================================
# Create the SQL Analysis Team
# ============================================================================
data_analysis_team = Team(
    name="SQL Analysis Team",
    model=OpenAIChat(id="gpt-5-mini"),
    members=[sql_query_agent, data_analyst_agent, report_generator_agent],
    description=description,
    instructions=instructions,
    db=demo_db,
    add_history_to_context=True,
    add_datetime_to_context=True,
    markdown=True,
    debug_mode=True,
)

# ============================================================================
# Load F1 Knowledge
# ============================================================================
if __name__ == "__main__":
    files = [str(f) for f in data_dir.glob("*.json")]
    f1_knowledge.add_contents(paths=files)
