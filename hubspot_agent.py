"""HubSpot Agent using MCP

This module creates an async Agent that correctly uses MCPTools in an async context
to interact with the HubSpot API through the Model Context Protocol.
"""

import asyncio
import os
from pathlib import Path
from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools

# Path to the MCP server script
mcp_server_script = Path(__file__).parent.joinpath("hubspot_integration/mcp_server.py")
python_interpreter = Path(__file__).parent.joinpath("venv/bin/python")


async def create_hubspot_agent():
    """Create and initialize a HubSpot agent with MCPTools properly configured in async context."""

    # Command to run the MCP server
    mcp_cmd = f"{python_interpreter} {mcp_server_script}"

    # Initialize MCPTools with the command
    async with MCPTools(mcp_cmd) as mcp_tools:
        # Create the agent with MCPTools
        agent = Agent(
            model=OpenAIChat(id="o3-mini-2025-01-31"),
            tools=[mcp_tools],
            instructions=dedent(
                """\
                You are a HubSpot assistant. You can help users with:
                
                - Searching for contacts in HubSpot
                - Getting detailed information about companies
                - Getting detailed information about deals
                
                Use the available tools to accomplish these tasks.
            """
            ),
            markdown=True,
            show_tool_calls=True,
        )

        # Return the initialized agent
        return agent


async def run_hubspot_agent(message: str):
    """Run the HubSpot agent with the given message."""
    agent = await create_hubspot_agent()
    await agent.aprint_response(message, stream=True)


if __name__ == "__main__":
    # Example usage
    asyncio.run(run_hubspot_agent("Search for contacts with the name 'John'"))
