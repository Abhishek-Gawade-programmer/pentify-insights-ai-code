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
from agno.models.anthropic import Claude
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools.file import FileTools
from agno.tools.sql import SQLTools
from agno.vectordb.pgvector import PgVector

# ************* Database Connection *************
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
# *******************************

# ************* Paths *************
cwd = Path(__file__).parent
knowledge_dir = cwd.joinpath("knowledge")
output_dir = cwd.joinpath("output")

# Create the output directory if it does not exist
output_dir.mkdir(parents=True, exist_ok=True)
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
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    # 5 references are added to the prompt
    num_documents=5,
)
# *******************************

# ************* Semantic Model *************
# The semantic model helps the agent identify the tables and columns to use
# This is sent in the system prompt, the agent then uses the `search_knowledge_base` tool to get table metadata, rules and sample queries
# This is very much how data analysts and data scientists work:
#  - We start with a set of tables and columns that we know are relevant to the task
#  - We then use the `search_knowledge_base` tool to get more information about the tables and columns
#  - We then use the `describe_table` tool to get more information about the tables and columns
#  - We then use the `search_knowledge_base` tool to get sample queries for the tables and columns
semantic_model = {
    "tables": [
        {
            "table_name": "companies",
            "table_description": "Contains company details such as addresses, contact information, and additional metadata. This table tracks basic company data and their classification as clients.",
            "Use Case": "Use this table to retrieve, update, and analyze company information, including contact details and client status.",
        },
        {
            "table_name": "contacts",
            "table_description": "Stores individual contact details including personal information, addresses, and the associated company's data.",
            "Use Case": "Use this table to manage contact information and analyze relationships between contacts and their respective companies.",
        },
        {
            "table_name": "projects",
            "table_description": "Holds data on projects including budget, deadlines, descriptions, and links to the related companies and personnel.",
            "Use Case": "Use this table to track project progress, analyze project statuses, and monitor associated company and personnel performance.",
        },
        {
            "table_name": "quotes",
            "table_description": "Captures financial and status details for quotes, including pricing, discounts, associated projects, and company details.",
            "Use Case": "Use this table to manage and analyze quotes issued to companies and projects, track financial details, and monitor quote status.",
        },
    ]
}

semantic_model_str = json.dumps(semantic_model, indent=2)
# *******************************


def create_bar_chart(
    data: Union[str, Dict[str, List[Any]]],
    title: str,
    x_label: str,
    y_label: str,
    filename: str = "bar_chart.png",
    color: str = "blue",
    horizontal: bool = False,
    sort_values: bool = False,
) -> str:
    """
    Create a bar chart from the provided data and save it as a PNG file.

    Args:
        data: JSON string or dictionary containing the data for the chart.
              Should have keys for x and y values.
        title: Title of the chart.
        x_label: Label for the x-axis.
        y_label: Label for the y-axis.
        filename: Output filename (will be saved in the output directory).
        color: Color of the bars.
        horizontal: Whether to create a horizontal bar chart.
        sort_values: Whether to sort the data by values.

    Returns:
        str: Path to the saved chart image.
    """
    plt.figure(figsize=(10, 6))

    # Convert data to DataFrame if it's a JSON string
    if isinstance(data, str):
        data = json.loads(data)

    df = pd.DataFrame(data)

    # Get the column names
    if len(df.columns) < 2:
        return "Error: Data must have at least two columns for x and y values."

    x_col = df.columns[0]
    y_col = df.columns[1]

    # Sort if requested
    if sort_values:
        df = df.sort_values(by=y_col)

    # Create the bar chart
    if horizontal:
        ax = sns.barplot(y=x_col, x=y_col, data=df, color=color)
    else:
        ax = sns.barplot(x=x_col, y=y_col, data=df, color=color)

    # Set labels and title
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.tight_layout()

    # Ensure filename has .png extension
    if not filename.endswith(".png"):
        filename += ".png"

    # Save the chart to the output directory
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path)
    plt.close()

    return output_path


def create_pie_chart(
    data: Union[str, Dict[str, List[Any]]],
    title: str,
    filename: str = "pie_chart.png",
    colors: Optional[List[str]] = None,
    explode: Optional[List[float]] = None,
    autopct: str = "%1.1f%%",
) -> str:
    """
    Create a pie chart from the provided data and save it as a PNG file.

    Args:
        data: JSON string or dictionary containing the data for the chart.
              Should have keys for labels and values.
        title: Title of the chart.
        filename: Output filename (will be saved in the output directory).
        colors: List of colors for pie slices. If None, uses default colors.
        explode: List of values to "explode" slices away from center.
        autopct: Format string for percentage labels.

    Returns:
        str: Path to the saved chart image.
    """
    plt.figure(figsize=(10, 8))

    # Convert data to DataFrame if it's a JSON string
    if isinstance(data, str):
        data = json.loads(data)

    df = pd.DataFrame(data)

    # Get the column names
    if len(df.columns) < 2:
        return "Error: Data must have at least two columns for labels and values."

    label_col = df.columns[0]
    value_col = df.columns[1]

    # Get labels and values
    labels = df[label_col].tolist()
    values = df[value_col].tolist()

    # Create the pie chart
    plt.pie(
        values,
        labels=labels,
        colors=colors,
        explode=explode,
        autopct=autopct,
        shadow=True,
        startangle=90,
    )
    plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle

    plt.title(title)
    plt.tight_layout()

    # Ensure filename has .png extension
    if not filename.endswith(".png"):
        filename += ".png"

    # Save the chart to the output directory
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path)
    plt.close()

    return output_path


def create_line_chart(
    data: Union[str, Dict[str, List[Any]]],
    title: str,
    x_label: str,
    y_label: str,
    filename: str = "line_chart.png",
    color: str = "blue",
    marker: str = "o",
    linestyle: str = "-",
) -> str:
    """
    Create a line chart from the provided data and save it as a PNG file.

    Args:
        data: JSON string or dictionary containing the data for the chart.
              Should have keys for x and y values.
        title: Title of the chart.
        x_label: Label for the x-axis.
        y_label: Label for the y-axis.
        filename: Output filename (will be saved in the output directory).
        color: Color of the line.
        marker: Marker style for data points.
        linestyle: Style of the line.

    Returns:
        str: Path to the saved chart image.
    """
    plt.figure(figsize=(10, 6))

    # Convert data to DataFrame if it's a JSON string
    if isinstance(data, str):
        data = json.loads(data)

    df = pd.DataFrame(data)

    # Get the column names
    if len(df.columns) < 2:
        return "Error: Data must have at least two columns for x and y values."

    x_col = df.columns[0]
    y_col = df.columns[1]

    # Create the line chart
    plt.plot(df[x_col], df[y_col], marker=marker, linestyle=linestyle, color=color)

    # Set labels and title
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.tight_layout()
    plt.grid(True, alpha=0.3)

    # Ensure filename has .png extension
    if not filename.endswith(".png"):
        filename += ".png"

    # Save the chart to the output directory
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path)
    plt.close()

    return output_path


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
        model = OpenAIChat(id=model_name)
    elif provider == "google":
        model = Gemini(id=model_name)
    elif provider == "anthropic":
        model = Claude(id=model_name)
    else:
        raise ValueError(f"Unsupported model provider: {provider}")

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
        tools=[
            SQLTools(db_url=db_url),
            FileTools(base_dir=output_dir),
            create_bar_chart,
            create_pie_chart,
            create_line_chart,
        ],
        add_history_to_messages=True,
        num_history_responses=3,
        debug_mode=debug_mode,
        description=dedent(
            """\
        You are BusinessDB Pro, an elite business data analyst specializing in:

        - Company information analysis
        - Contact relationship management
        - Project performance tracking
        - Quote and financial insights
        - Client status monitoring
        - Business intelligence reporting

        You combine deep business knowledge with advanced SQL expertise to uncover insights from company, contact, project, and quote data."""
        ),
        instructions=dedent(
            f"""\
        You are a SQL expert focused on writing precise, efficient queries.

        When a user messages you, determine if you need query the database or can respond directly.
        If you can respond directly, do so.

        If you need to query the database to answer the user's question, follow these steps:
        1. First identify the tables you need to query from the semantic model.
        2. Then, ALWAYS use the `search_knowledge_base(table_name)` tool to get table metadata, rules and sample queries.
        3. If table rules are provided, ALWAYS follow them.
        4. Then, think step-by-step about query construction, don't rush this step.
        5. Follow a chain of thought approach before writing SQL, ask clarifying questions where needed.
        6. If sample queries are available, use them as a reference.
        7. If you need more information about the table, use the `describe_table` tool.
        8. Then, using all the information available, create one single syntactically correct PostgreSQL query to accomplish your task.
        9. If you need to join tables, check the `semantic_model` for the relationships between the tables.
            - If the `semantic_model` contains a relationship between tables, use that relationship to join the tables even if the column names are different.
            - If you cannot find a relationship in the `semantic_model`, only join on the columns that have the same name and data type.
            - If you cannot find a valid relationship, ask the user to provide the column name to join.
        10. If you cannot find relevant tables, columns or relationships, stop and ask the user for more information.
        11. Once you have a syntactically correct query, run it using the `run_sql_query` function.
        12. When running a query:
            - Do not add a `;` at the end of the query.
            - Always provide a limit unless the user explicitly asks for all results.
        13. After you run the query, analyse the results and return the answer in markdown format.
        14. Always show the user the SQL you ran to get the answer.
        15. Continue till you have accomplished the task.
        16. Show results as a table or a chart if possible.
            - For numerical data that can be compared, use the `create_bar_chart` or `create_line_chart` function.
            - For data showing composition or distribution, use the `create_pie_chart` function.
            - Always provide proper titles, labels and filename for the charts.
            - Display the chart by including the file path in your response using markdown image syntax: ![Chart Title](file path)

        After finishing your task, ask the user relevant followup questions like "was the result okay, would you like me to fix any problems?"
        If the user says yes, get the previous query using the `get_tool_call_history(num_calls=3)` function and fix the problems.
        If the user wants to see the SQL, get it using the `get_tool_call_history(num_calls=3)` function.

        Finally, here are the set of rules that you MUST follow:
        <rules>
        - Use the `search_knowledge_base(table_name)` tool to get table information from your knowledge base before writing a query.
        - Do not use phrases like "based on the information provided" or "from the knowledge base".
        - Always show the SQL queries you use to get the answer.
        - Make sure your query accounts for duplicate records.
        - Make sure your query accounts for null values.
        - If you run a query, explain why you ran it.
        - For numerical results, consider creating visualizations using the chart creation tools.
        - **NEVER, EVER RUN CODE TO DELETE DATA OR ABUSE THE LOCAL SYSTEM**
        - ALWAYS FOLLOW THE `table rules` if provided. NEVER IGNORE THEM.
        </rules>\
        """
        ),
        additional_context=dedent(
            """\
        The following `semantic_model` contains information about tables and the relationships between them.
        If the users asks about the tables you have access to, simply share the table names from the `semantic_model`.
        <semantic_model>
        """
        )
        + semantic_model_str
        + dedent(
            """\
        </semantic_model>\
        """
        ),
        # Set to True to display tool calls in the response message
        # show_tool_calls=True,
    )
