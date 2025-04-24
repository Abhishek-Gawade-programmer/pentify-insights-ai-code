"""🏎️ SQL Agent - Your AI Data Analyst!

This advanced example shows how to build a sophisticated text-to-SQL system that
leverages Agentic RAG to provide deep insights into any data.

Example queries to try:
- "Who are the top 5 drivers with the most race wins?"
- "Compare Mercedes vs Ferrari performance in constructors championships"
- "Show me the progression of fastest lap times at Monza"
- "Which drivers have won championships with multiple teams?"
- "What tracks have hosted the most races?"
- "Show me Lewis Hamilton's win percentage by season"

Examples with table joins:
- "How many races did the championship winners win each year?"
- "Compare the number of race wins vs championship positions for constructors in 2019"
- "Show me Lewis Hamilton's race wins and championship positions by year"
- "Which drivers have both won races and set fastest laps at Monaco?"
- "Show me Ferrari's race wins and constructor championship positions from 2015-2020"

View the README for instructions on how to run the application.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
from textwrap import dedent
from typing import Optional, Dict, List, Any, Union

from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.knowledge.json import JSONKnowledgeBase
from agno.knowledge.text import TextKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools.sql import SQLTools
from agno.vectordb.pgvector import PgVector

from prompts import AGENT_DESCRIPTION, INSTRUCTIONS, ADDITIONAL_CONTEXT
from tools import visualize_streamlit_data, suggest_chart_type

# ************* Database Connection *************
db_url = "postgresql://neondb_owner:npg_hgMT6X1KNUBa@ep-fragrant-sky-a1l6ctkh-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
# *******************************

# ************* Paths *************
cwd = Path(__file__).parent
knowledge_dir = cwd.joinpath("knowledge")

# *******************************

# ************* Storage & Knowledge *************
agent_storage = PostgresAgentStorage(
    db_url=db_url,
    # Store agent sessions in the ai.sql_agent_sessions table
    table_name="sql_agent_sessions",
    schema="ai",
)
agent_knowledge = CombinedKnowledgeBase(
    sources=[
        # Reads text files, SQL files, and markdown files
        TextKnowledgeBase(
            path=knowledge_dir,
            formats=[".txt", ".sql", ".md"],
        ),
        # Reads JSON files
        JSONKnowledgeBase(path=knowledge_dir),
    ],
    # Store agent knowledge in the ai.sql_agent_knowledge table
    vector_db=PgVector(
        db_url=db_url,
        table_name="sql_agent_knowledge",
        schema="ai",
        # Use OpenAI embeddings
        embedder=OpenAIEmbedder(id="text-embedding-3-large"),
    ),
    # 5 references are added to the prompt
    num_documents=5,
)


# *******************************


def get_sql_agent(
    user_id: Optional[str] = None,
    model_id: str = "openai:gpt-4o",
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """Returns an instance of the SQL Agent.

    Args:
        user_id: Optional user identifier
        debug_mode: Enable debug logging
        model_id: Model identifier in format 'provider:model_name'
    """
    # Parse model provider and name
    provider, model_name = model_id.split(":")

    # Select appropriate model class based on provider
    if provider == "openai":
        model = OpenAIChat(id="o4-mini-2025-04-16")
    else:
        raise ValueError(f"Unsupported model provider: {provider}")

    # Create SQL tools with custom visualization functions
    sql_tools = SQLTools(db_url=db_url)

    return Agent(
        name="SQL Agent",
        model=model,
        user_id=user_id,
        session_id=session_id,
        storage=agent_storage,
        knowledge=agent_knowledge,
        # Enable Agentic RAG i.e. the ability to search the knowledge base on-demand
        search_knowledge=True,
        # Enable the ability to read the chat history
        read_chat_history=True,
        # Enable the ability to read the tool call history
        read_tool_call_history=True,
        # Add tools to the agent
        tools=[sql_tools, visualize_streamlit_data, suggest_chart_type],
        add_history_to_messages=True,
        num_history_responses=3,
        add_datetime_to_instructions=True,
        debug_mode=debug_mode,
        description=AGENT_DESCRIPTION,
        instructions=INSTRUCTIONS,
        additional_context=ADDITIONAL_CONTEXT,
        reasoning=True,
        telemetry=False,
    )
