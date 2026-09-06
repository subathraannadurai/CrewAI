from typing import Any

from crewai import Agent
from crewai.tools import tool

try:
    from crewai_tools import GoogleDocsExporter, MCPResearchTool, SerpAPITool  # type: ignore[import-not-found]
except ImportError:
    GoogleDocsExporter = None
    MCPResearchTool = None
    SerpAPITool = None

from config import Config


class _FallbackSerpTool:
    """Fallback search wrapper that uses serpapi when crewai_tools is unavailable."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, num: int = 5) -> list[dict[str, Any]]:
        try:
            from serpapi import GoogleSearch
        except ImportError as exc:
            raise RuntimeError("serpapi is not installed") from exc

        params = {"q": query, "num": num, "api_key": self.api_key}
        response = GoogleSearch(params).get_dict()
        return response.get("organic_results", [])


def create_agents(config: Config) -> dict:
    """Create and return all agents for the GTM workflow."""

    # Initialize tools
    llm = config.get_llm()

    if SerpAPITool is not None:
        serp_tool = SerpAPITool(api_key=config.serper_api_key)
    else:
        serp_tool = _FallbackSerpTool(api_key=config.serper_api_key)

    mcp_tool = None
    if config.mcp_server_url and MCPResearchTool is not None:
        mcp_tool = MCPResearchTool(mcp_url=config.mcp_server_url, api_key=config.mcp_api_key)

    docs_exporter = None
    if config.google_creds_path and GoogleDocsExporter is not None:
        docs_exporter = GoogleDocsExporter(credentials_file=config.google_creds_path)

    # Wrapper tools for CrewAI
    @tool("Search market data")
    def search_market_data(query: str, num_results: int = 5) -> str:
        """Search for market data using SerpAPI."""
        try:
            results = serp_tool.search(query, num=num_results)
            formatted = "\n".join([f"- {r['title']}: {r['link']}\n  {r['snippet']}" for r in results])
            return formatted
        except Exception as e:
            return f"Error searching: {str(e)}"

    @tool("Research via MCP")
    def research_via_mcp(brief: str, questions: list) -> str:
        """Call MCP server for research."""
        if not mcp_tool:
            return "MCP tool not configured."
        try:
            response = mcp_tool.research(brief=brief, questions=questions)
            return str(response)
        except Exception as e:
            return f"Error calling MCP: {str(e)}"

    # Define agents
    agent_kwargs = {"verbose": True}
    if llm is not None:
        agent_kwargs["llm"] = llm

    head_planner = Agent(
        role="Head Planner",
        goal="Orchestrate market research and GTM planning by coordinating other agents and synthesizing outputs into a cohesive plan.",
        backstory="You are an experienced product strategist who excels at planning and documentation. "
        "You break down complex GTM challenges into actionable research tasks and synthesize findings into a comprehensive strategy.",
        tools=[search_market_data],
        allow_delegation=True,
        **agent_kwargs,
    )

    research_agent = Agent(
        role="Research Agent",
        goal="Find and collect market research evidence including competitors, pricing, market size, and customer insights.",
        backstory="You are a thorough market researcher with expertise in competitive intelligence. "
        "You excel at finding credible sources, extracting relevant data, and organizing evidence with proper citations.",
        tools=[search_market_data, research_via_mcp] if mcp_tool else [search_market_data],
        **agent_kwargs,
    )

    analyst_agent = Agent(
        role="Analyst Agent",
        goal="Synthesize research findings into structured analysis: competitor comparisons, pricing matrices, SWOT, and market insights.",
        backstory="You are a business analyst with strong analytical skills. "
        "You excel at structuring data, identifying patterns, and creating clear comparisons and visualizations.",
        tools=[],
        **agent_kwargs,
    )

    strategy_agent = Agent(
        role="Strategy Agent",
        goal="Create a comprehensive GTM plan with target ICPs, value proposition, messaging, go-to-market channels, and launch timeline.",
        backstory="You are a GTM strategist with deep experience launching products. "
        "You excel at identifying target segments, crafting compelling messaging, and defining executable go-to-market strategies.",
        tools=[],
        **agent_kwargs,
    )

    return {
        "head_planner": head_planner,
        "research_agent": research_agent,
        "analyst_agent": analyst_agent,
        "strategy_agent": strategy_agent,
        "tools": {
            "search": search_market_data,
            "mcp_research": research_via_mcp,
            "docs_exporter": docs_exporter,
        },
    }
