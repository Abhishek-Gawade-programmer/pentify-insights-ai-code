import asyncio
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters


async def chat_response_streamer(run_response):
    content = ""
    async for run_response_chunk in run_response:
        content += run_response_chunk.content
    return content


async def run_agent(message: str):
    """Run the filesystem agent with the given message."""

    # Create the MCP server parameters
    mcp_server_cmd = "/home/abhishek/ai-code/pentify-insights-ai-code/venv/bin/python"
    mcp_server_args = [
        "/home/abhishek/ai-code/pentify-insights-ai-code/hubspot_integration/mcp_server.py"
    ]

    server_params = StdioServerParameters(
        command=mcp_server_cmd,
        args=mcp_server_args,
    )

    async with MCPTools(server_params=server_params) as mcp_tools:
        agent = Agent(
            model=OpenAIChat(id="gpt-4o"),
            tools=[mcp_tools],
            instructions=dedent(
                """\
                You are a filesystem assistant. Help users explore files and directories.

                - Navigate the filesystem to answer questions
                - Use the list_allowed_directories tool to find directories that you can access
                - Provide clear context about files you examine
                - Use headings to organize your responses
                - Be concise and focus on relevant information\
            """
            ),
            markdown=True,
            show_tool_calls=True,
        )

        # Run the agent
        run_response = await agent.arun(message, stream=True)
        return await chat_response_streamer(run_response)


# Example usage
if __name__ == "__main__":
    # Basic example - exploring project license

    AGENT_RESPONSE = asyncio.run(
        run_agent("can you tell me company name for  Id 40281911407  hubspot")
    )
    print(AGENT_RESPONSE)
    # asyncio.run(chat_response_streamer(AGENT_RESPONSE))

    # print(asyncio.run(chat_response_streamer(AGENT)))
