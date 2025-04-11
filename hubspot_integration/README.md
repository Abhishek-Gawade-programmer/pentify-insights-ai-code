# HubSpot MCP Server

A custom Managed Content Platform (MCP) server for HubSpot API integration using the official [Model Context Protocol SDK](https://github.com/modelcontextprotocol/python-sdk). This server provides an MCP-compliant wrapper around HubSpot's API endpoints, making it easier to interact with HubSpot's CRM data from LLM-powered applications.

## Features

- Fully compliant with the Model Context Protocol
- Resources for accessing HubSpot data
- Tools for interacting with HubSpot API
- Prompts for analyzing HubSpot data
- Async API calls
- Error handling
- Environment-based configuration

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your HubSpot API key:

```
HUBSPOT_API_KEY=your_api_key_here
```

## Running the Server

To start the server, run:

```bash
python mcp_server.py
```

The server will start on `http://localhost:8000`

## MCP Resources

The server exposes the following resources:

- `hubspot://contacts` - Get all contacts from HubSpot
- `hubspot://companies` - Get all companies from HubSpot
- `hubspot://deals` - Get all deals from HubSpot

## MCP Tools

The server provides the following tools that can be called by LLMs:

- `search_contacts` - Search for contacts in HubSpot

  - Parameters:
    - `query` (required): Search term to find contacts
    - `limit` (optional, default: 10): Maximum number of results to return

- `get_company_details` - Get detailed information about a specific company

  - Parameters:
    - `company_id` (required): The HubSpot ID of the company

- `get_deal_details` - Get detailed information about a specific deal
  - Parameters:
    - `deal_id` (required): The HubSpot ID of the deal

## MCP Prompts

The server provides the following prompt templates:

- `contact_analysis_prompt` - Prompt template for analyzing a contact

  - Parameters:
    - `contact_name` (required): Name of the contact to analyze

- `company_analysis_prompt` - Prompt template for analyzing a company
  - Parameters:
    - `company_name` (required): Name of the company to analyze

## Using with LLM Applications

This server can be integrated with any LLM application that supports the Model Context Protocol. You can connect to it using the MCP client SDK:

```python
from mcp import ClientSession
from mcp.client.tcp import tcp_client

async def run():
    async with tcp_client("localhost", 8000) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available resources
            resources = await session.list_resources()
            print(resources)

            # Read a resource
            contacts, mime_type = await session.read_resource("hubspot://contacts")
            print(contacts)

            # Call a tool
            result = await session.call_tool("search_contacts",
                                            arguments={"query": "Smith", "limit": 5})
            print(result)
```

## Error Handling

The server includes proper error handling for:

- Missing API key
- Invalid API requests
- HubSpot API errors

## Security

- API key is stored in environment variables
- HTTPS is used for all HubSpot API calls
- Input validation for all tools and prompts

## About the Model Context Protocol

The Model Context Protocol (MCP) is an open standard for communication between LLM applications and backend servers. It provides a standardized way to expose resources, tools, and prompts to LLM clients.

For more information, visit [modelcontextprotocol.io](https://modelcontextprotocol.io) or check out the [GitHub repository](https://github.com/modelcontextprotocol/python-sdk).

## Contributing

Feel free to submit issues and enhancement requests!
