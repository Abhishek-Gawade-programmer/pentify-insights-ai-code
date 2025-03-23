from typing import Optional, Dict, List, Any, Union
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import json
import streamlit as st


cwd = Path(__file__).parent
output_dir = cwd.joinpath("output")

# Create the output directory if it does not exist
output_dir.mkdir(parents=True, exist_ok=True)


# *******************************
def create_bar_chart(
    data: str,
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
        data: JSON string containing the data for the chart.
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
    data_dict = json.loads(data) if isinstance(data, str) else data

    df = pd.DataFrame(data_dict)

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
    data: str,
    title: str,
    filename: str = "pie_chart.png",
    colors: Optional[List[str]] = None,
    explode: Optional[List[float]] = None,
    autopct: str = "%1.1f%%",
) -> str:
    """
    Create a pie chart from the provided data and save it as a PNG file.

    Args:
        data: JSON string containing the data for the chart.
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
    data_dict = json.loads(data) if isinstance(data, str) else data

    df = pd.DataFrame(data_dict)

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
    data: str,
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
        data: JSON string containing the data for the chart.
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
    data_dict = json.loads(data) if isinstance(data, str) else data

    df = pd.DataFrame(data_dict)

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


def suggest_chart_type(data: str) -> Dict[str, Any]:
    """
    Analyzes SQL query results and suggests appropriate chart type and configuration.

    Args:
        data: JSON string containing the query results

    Returns:
        dict: A dictionary with chart suggestion including:
            - chart_type: The recommended chart type ('bar', 'pie', 'line', 'area', 'map', or 'table')
            - reason: Explanation for why this chart type was selected
            - config: Suggested configuration parameters for the chart
    """
    # Convert data to DataFrame if it's a JSON string
    try:
        data_dict = json.loads(data) if isinstance(data, str) else data
    except:
        return {
            "chart_type": "table",
            "reason": "Could not parse data as JSON",
            "config": {},
        }

    # Convert to DataFrame for analysis
    try:
        df = pd.DataFrame(data_dict)
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

    # Check for geo data (latitude and longitude) for map visualization
    has_lat = any(col.lower() in ["lat", "latitude"] for col in df.columns)
    has_lon = any(col.lower() in ["lon", "long", "longitude"] for col in df.columns)

    # Case 0: Geo data - use map
    if has_lat and has_lon:
        lat_col = next(col for col in df.columns if col.lower() in ["lat", "latitude"])
        lon_col = next(
            col for col in df.columns if col.lower() in ["lon", "long", "longitude"]
        )
        return {
            "chart_type": "map",
            "reason": "Geographic data detected - map is best for showing spatial distribution",
            "config": {
                "lat_col": lat_col,
                "lon_col": lon_col,
                "title": "Geographic Distribution",
            },
        }

    # Case 1: Time series data - use line chart
    if date_cols and numeric_cols:
        return {
            "chart_type": "line",
            "reason": "Time series data detected - line chart is best for showing trends over time",
            "config": {
                "x": date_cols[0],
                "y": numeric_cols[0],
                "title": f"{numeric_cols[0]} over Time",
            },
        }

    # Case 2: Area chart for cumulative or stacked data
    if (date_cols or len(numeric_cols) > 1) and len(numeric_cols) > 1:
        return {
            "chart_type": "area",
            "reason": "Multiple numeric series detected - area chart shows stacked or cumulative values well",
            "config": {
                "x": date_cols[0] if date_cols else df.index.name or "index",
                "y": numeric_cols,
                "title": "Data Trends",
            },
        }

    # Case 3: Categorical comparison - use bar chart
    if categorical_cols and numeric_cols:
        return {
            "chart_type": "bar",
            "reason": "Categorical comparison data - bar chart is best for comparing values across categories",
            "config": {
                "x": categorical_cols[0],
                "y": numeric_cols[0],
                "title": f"{numeric_cols[0]} by {categorical_cols[0]}",
                "color": categorical_cols[0] if len(categorical_cols) > 1 else None,
            },
        }

    # Default: use bar chart for generic numeric data
    return {
        "chart_type": "bar",
        "reason": "Generic numeric data - bar chart is a safe default visualization",
        "config": {
            "x": df.columns[0],
            "y": numeric_cols[0],
            "title": f"{numeric_cols[0]} Analysis",
        },
    }


def visualize_streamlit_data(
    data: str,
    chart_type: Optional[str] = None,
    title: Optional[str] = None,
    x: Optional[str] = None,
    y: Optional[Union[str, List[str]]] = None,
    color: Optional[Union[str, List[str]]] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    use_container_width: bool = True,
    horizontal: bool = False,
    stack: Optional[Union[bool, str]] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Visualize data using Streamlit's chart components based on the data and chart type.

    Args:
        data: JSON string containing the data for the chart
        chart_type: Type of chart to create ('bar', 'line', 'area', 'map', or 'table')
        title: Title for the chart
        x: Column name for x-axis data
        y: Column name(s) for y-axis data (can be a list for multiple series)
        color: Column name for color encoding or list of colors
        lat: Column name for latitude data (for map charts)
        lon: Column name for longitude data (for map charts)
        use_container_width: Whether to expand chart to container width
        horizontal: Whether to make a horizontal bar chart
        stack: How to stack bars ('normalize', 'center', 'layered', True, False, or None)
        width: Desired chart width in pixels (when use_container_width is False)
        height: Desired chart height in pixels

    Returns:
        dict: Information about the visualization including chart_type and success status
    """
    # Convert data to DataFrame if it's a JSON string
    try:
        data_dict = json.loads(data) if isinstance(data, str) else data
        df = pd.DataFrame(data_dict)
    except Exception as e:
        return {
            "chart_type": "table",
            "success": False,
            "error": f"Failed to convert data to DataFrame: {str(e)}",
        }

    # If chart_type is not specified, suggest one based on the data
    if not chart_type:
        suggestion = suggest_chart_type(data)
        chart_type = suggestion["chart_type"]

        # Use suggested config if not provided
        if not x and "x" in suggestion["config"]:
            x = suggestion["config"].get("x")
        if not y and "y" in suggestion["config"]:
            y = suggestion["config"].get("y")
        if not color and "color" in suggestion["config"]:
            color = suggestion["config"].get("color")
        if not lat and "lat_col" in suggestion["config"]:
            lat = suggestion["config"].get("lat_col")
        if not lon and "lon_col" in suggestion["config"]:
            lon = suggestion["config"].get("lon_col")
        if not title and "title" in suggestion["config"]:
            title = suggestion["config"].get("title")

    # Ensure we have a chart title
    if title:
        st.markdown(f"### {title}")

    try:
        # Create the appropriate chart based on chart_type
        if chart_type == "bar":
            chart = st.bar_chart(
                data=df,
                x=x,
                y=y,
                color=color,
                horizontal=horizontal,
                stack=stack,
                width=width,
                height=height,
                use_container_width=use_container_width,
            )
            return {"chart_type": "bar", "success": True}

        elif chart_type == "line":
            chart = st.line_chart(
                data=df,
                x=x,
                y=y,
                color=color,
                width=width,
                height=height,
                use_container_width=use_container_width,
            )
            return {"chart_type": "line", "success": True}

        elif chart_type == "area":
            chart = st.area_chart(
                data=df,
                x=x,
                y=y,
                color=color,
                width=width,
                height=height,
                use_container_width=use_container_width,
            )
            return {"chart_type": "area", "success": True}

        elif chart_type == "map":
            # For map charts, prepare the data
            if lat and lon:
                # Select only the columns needed for the map
                map_data = df[[lat, lon]].copy()
                # Rename columns to lat/lon if they aren't already
                map_data.columns = ["lat", "lon"] + [
                    c for c in map_data.columns if c not in [lat, lon]
                ]
            else:
                # Look for standard latitude/longitude column names
                lat_col = next(
                    (c for c in df.columns if c.lower() in ["lat", "latitude"]), None
                )
                lon_col = next(
                    (
                        c
                        for c in df.columns
                        if c.lower() in ["lon", "long", "longitude"]
                    ),
                    None,
                )

                if lat_col and lon_col:
                    map_data = df[[lat_col, lon_col]].copy()
                    map_data.columns = ["lat", "lon"] + [
                        c for c in map_data.columns if c not in [lat_col, lon_col]
                    ]
                else:
                    return {
                        "chart_type": "table",
                        "success": False,
                        "error": "Could not identify latitude and longitude columns for map",
                    }

            st.map(map_data, use_container_width=use_container_width)
            return {"chart_type": "map", "success": True}

        else:
            # Default to a table if no suitable chart type is found
            st.dataframe(df, use_container_width=use_container_width)
            return {"chart_type": "table", "success": True}

    except Exception as e:
        # If visualization fails, show the data as a table
        st.error(f"Failed to create {chart_type} chart: {str(e)}")
        st.dataframe(df, use_container_width=use_container_width)
        return {
            "chart_type": "table",
            "success": False,
            "error": str(e),
        }
