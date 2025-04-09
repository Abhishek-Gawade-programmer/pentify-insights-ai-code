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


def suggest_chart_type(data: Union[str, Dict[str, List[Any]]]) -> Dict[str, Any]:
    """
    Analyzes SQL query results and suggests appropriate chart type and configuration.

    Args:
        data: JSON string or dictionary containing the query results

    Returns:
        dict: A dictionary with chart suggestion including:
            - chart_type: The recommended chart type ('bar', 'pie', 'line', or 'table')
            - reason: Explanation for why this chart type was selected
            - config: Suggested configuration parameters for the chart
    """
    # Convert data to DataFrame if it's a JSON string
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            return {
                "chart_type": "table",
                "reason": "Could not parse data as JSON",
                "config": {},
            }

    # Convert to DataFrame for analysis
    try:
        df = pd.DataFrame(data)
    except:
        return {
            "chart_type": "table",
            "reason": "Data could not be converted to DataFrame",
            "config": {},
        }

    # If we don't have enough data for a chart
    if len(df) < 2:
        return {
            "chart_type": "table",
            "reason": "Not enough data points for visualization",
            "config": {},
        }

    # If we don't have at least two columns for x/y values
    if len(df.columns) < 2:
        return {
            "chart_type": "table",
            "reason": "Need at least two columns for visualization",
            "config": {},
        }

    # Get column types
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = [
        col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])
    ]

    # If no numeric columns, can't make a standard chart
    if not numeric_cols:
        return {
            "chart_type": "table",
            "reason": "No numeric data available for visualization",
            "config": {},
        }

    # Choose appropriate chart based on data characteristics

    # Case 1: Time series data - use line chart
    if date_cols and numeric_cols:
        return {
            "chart_type": "line",
            "reason": "Time series data detected - line chart is best for showing trends over time",
            "config": {
                "x_col": date_cols[0],
                "y_col": numeric_cols[0],
                "title": f"{numeric_cols[0]} over Time",
                "x_label": date_cols[0],
                "y_label": numeric_cols[0],
            },
        }

    # Case 2: Distribution/proportion data with few categories (2-7) - use pie chart
    if (
        categorical_cols
        and numeric_cols
        and 2 <= len(df[categorical_cols[0]].unique()) <= 7
    ):
        return {
            "chart_type": "pie",
            "reason": "Distribution data with few categories - pie chart shows proportion effectively",
            "config": {
                "label_col": categorical_cols[0],
                "value_col": numeric_cols[0],
                "title": f"Distribution of {numeric_cols[0]} by {categorical_cols[0]}",
            },
        }

    # Case 3: Categorical comparison - use bar chart
    if categorical_cols and numeric_cols:
        # Check if we need a horizontal bar chart (for long category names)
        horizontal = max(len(str(x)) for x in df[categorical_cols[0]].unique()) > 10

        return {
            "chart_type": "bar",
            "reason": "Categorical comparison data - bar chart is best for comparing values across categories",
            "config": {
                "x_col": categorical_cols[0],
                "y_col": numeric_cols[0],
                "title": f"{numeric_cols[0]} by {categorical_cols[0]}",
                "x_label": categorical_cols[0],
                "y_label": numeric_cols[0],
                "horizontal": horizontal,
                "sort_values": True,
            },
        }

    # Default: use bar chart for generic numeric data
    return {
        "chart_type": "bar",
        "reason": "Generic numeric data - bar chart is a safe default visualization",
        "config": {
            "x_col": df.columns[0],
            "y_col": numeric_cols[0],
            "title": f"{numeric_cols[0]} Analysis",
            "x_label": df.columns[0],
            "y_label": numeric_cols[0],
        },
    }


def visualize_sql_results(
    data: Union[str, Dict[str, List[Any]]],
    chart_type: Optional[str] = None,
    title: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Helper function to visualize SQL query results with the most appropriate chart type.

    Args:
        data: JSON string or dictionary containing the query results
        chart_type: Optional chart type to override automatic detection ('bar', 'pie', 'line')
        title: Optional chart title
        **kwargs: Additional parameters to pass to the chart creation function

    Returns:
        str: Path to the saved chart image or explanation why visualization couldn't be created
    """
    # If chart_type is not specified, suggest one based on the data
    if not chart_type:
        suggestion = suggest_chart_type(data)
        chart_type = suggestion["chart_type"]

        # Use suggested config if not provided in kwargs
        for key, value in suggestion["config"].items():
            if key not in kwargs:
                kwargs[key] = value

        # Use suggested title if not provided
        if not title and "title" in suggestion["config"]:
            title = suggestion["config"]["title"]

    # Ensure we have a chart title
    if not title:
        title = "Data Visualization"

    # Create the appropriate chart based on chart_type
    if chart_type == "bar":
        return create_bar_chart(
            data=data,
            title=title,
            x_label=kwargs.get("x_label", "Category"),
            y_label=kwargs.get("y_label", "Value"),
            filename=kwargs.get("filename", "sql_bar_chart.png"),
            color=kwargs.get("color", "blue"),
            horizontal=kwargs.get("horizontal", False),
            sort_values=kwargs.get("sort_values", False),
        )
    elif chart_type == "pie":
        return create_pie_chart(
            data=data,
            title=title,
            filename=kwargs.get("filename", "sql_pie_chart.png"),
            colors=kwargs.get("colors", None),
            explode=kwargs.get("explode", None),
            autopct=kwargs.get("autopct", "%1.1f%%"),
        )
    elif chart_type == "line":
        return create_line_chart(
            data=data,
            title=title,
            x_label=kwargs.get("x_label", "X Axis"),
            y_label=kwargs.get("y_label", "Y Axis"),
            filename=kwargs.get("filename", "sql_line_chart.png"),
            color=kwargs.get("color", "blue"),
            marker=kwargs.get("marker", "o"),
            linestyle=kwargs.get("linestyle", "-"),
        )
    else:
        return "No appropriate visualization could be created for this data"


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
        model = OpenAIChat(
            id="gpt-4o-mini",
            api_key="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",
        )
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
            visualize_sql_results,  # Add the new helper function
        ],
        add_history_to_messages=True,
        num_history_responses=3,
        add_datetime_to_instructions=True,
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
         dedent(
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
        16. ALWAYS visualize numerical results with charts using one of these methods:
            a. Use the `visualize_sql_results` function to automatically create the most appropriate chart type for the data.
               Example: visualize_sql_results(data=query_result, title="My Chart Title")
            
            b. Or for more control, use one of these specific chart functions:
               - `create_bar_chart` for comparing values across categories
               - `create_pie_chart` for showing composition or distribution of data
               - `create_line_chart` for showing trends over time
               
            c. NEVER just display raw tabular results without a visualization when the data is suitable for charts
            
            d. Make sure to include descriptive titles and labels for all charts

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
        - For numerical results, ALWAYS create visualizations using `visualize_sql_results` or the specific chart creation tools.
        - NEVER return query results without visualization if they are suitable for charts.
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
