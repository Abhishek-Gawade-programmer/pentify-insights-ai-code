from typing import Optional, Dict, List, Any, Union
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import json


cwd = Path(__file__).parent
output_dir = cwd.joinpath("output")

# Create the output directory if it does not exist
output_dir.mkdir(parents=True, exist_ok=True)


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
