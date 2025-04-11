import os
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel

from mcp.server.fastmcp import FastMCP
import mcp.types as types

# Load environment variables
load_dotenv()

# HubSpot API Configuration
HUBSPOT_API_KEY = "pat-na1-d020c13c-c99a-4e04-83cc-35fedfea9fca"
HUBSPOT_BASE_URL = "https://api.hubapi.com"

# Initialize MCP server
mcp_server = FastMCP("HubSpot MCP Server")


class HubSpotClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = HUBSPOT_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def get_contacts(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch contacts from HubSpot"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/crm/v3/objects/contacts",
                headers=self.headers,
                params={"limit": limit, "offset": offset},
            )
            if response.status_code != 200:
                raise Exception(f"HubSpot API error: {response.text}")
            return response.json()

    async def get_companies(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch companies from HubSpot"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/crm/v3/objects/companies",
                headers=self.headers,
                params={"limit": limit, "offset": offset},
            )
            if response.status_code != 200:
                raise Exception(f"HubSpot API error: {response.text}")
            return response.json()

    async def get_deals(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch deals from HubSpot"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/crm/v3/objects/deals",
                headers=self.headers,
                params={"limit": limit, "offset": offset},
            )
            if response.status_code != 200:
                raise Exception(f"HubSpot API error: {response.text}")
            return response.json()


# Initialize HubSpot client
def get_hubspot_client():
    if not HUBSPOT_API_KEY:
        raise Exception("HubSpot API key not configured")
    return HubSpotClient(HUBSPOT_API_KEY)


# Register resources
@mcp_server.resource("hubspot://contacts")
async def get_contacts_resource() -> str:
    """Get all contacts from HubSpot as a resource"""
    client = get_hubspot_client()
    contacts = await client.get_contacts()
    return str(contacts)


@mcp_server.resource("hubspot://companies")
async def get_companies_resource() -> str:
    """Get all companies from HubSpot as a resource"""
    client = get_hubspot_client()
    companies = await client.get_companies()
    return str(companies)


@mcp_server.resource("hubspot://deals")
async def get_deals_resource() -> str:
    """Get all deals from HubSpot as a resource"""
    client = get_hubspot_client()
    deals = await client.get_deals()
    return str(deals)


# Register tools
@mcp_server.tool()
async def search_contacts(query: str, limit: int = 10) -> str:
    """
    Search for contacts in HubSpot

    Args:
        query: Search term to find contacts
        limit: Maximum number of results to return
    """
    client = get_hubspot_client()
    contacts = await client.get_contacts(limit=limit)
    # Filter contacts (in a real implementation, use HubSpot's search API)
    results = [
        c for c in contacts.get("results", []) if query.lower() in str(c).lower()
    ]
    return str(results[:limit])


@mcp_server.tool()
async def get_company_details(company_id: str) -> str:
    """
    Get detailed information about a specific company

    Args:
        company_id: The HubSpot ID of the company
    """
    client = get_hubspot_client()
    companies = await client.get_companies()
    # Find the specific company (in a real implementation, use HubSpot's get by ID API)
    for company in companies.get("results", []):
        if str(company.get("id")) == company_id:
            return str(company)
    return "Company not found"


@mcp_server.tool()
async def get_deal_details(deal_id: str) -> str:
    """
    Get detailed information about a specific deal

    Args:
        deal_id: The HubSpot ID of the deal
    """
    client = get_hubspot_client()
    deals = await client.get_deals()
    # Find the specific deal (in a real implementation, use HubSpot's get by ID API)
    for deal in deals.get("results", []):
        if str(deal.get("id")) == deal_id:
            return str(deal)
    return "Deal not found"


# Register prompts
@mcp_server.prompt()
def contact_analysis_prompt(contact_name: str) -> str:
    """Create a prompt for analyzing a contact"""
    return f"""
    Please analyze the HubSpot contact with name '{contact_name}'. Consider:
    
    1. Their interaction history
    2. Deals they're associated with
    3. Their company information
    4. Potential opportunities for engagement
    
    Provide a summary with actionable insights.
    """


@mcp_server.prompt()
def company_analysis_prompt(company_name: str) -> str:
    """Create a prompt for analyzing a company"""
    return f"""
    Please analyze the HubSpot company '{company_name}'. Consider:
    
    1. Company profile and history
    2. Associated contacts
    3. Current deals and opportunities
    4. Industry position and competitive landscape
    
    Provide a summary with actionable business recommendations.
    """


if __name__ == "__main__":
    # Run the MCP server
    mcp_server.run(transport="stdio")
