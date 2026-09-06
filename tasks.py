from crewai import Task


def create_tasks(agents: dict) -> dict:
    """Create and return all tasks for the GTM workflow."""

    research_task = Task(
        description="""
        Conduct comprehensive market research for the given product brief. Your tasks:
        1. Identify 3-5 leading competitors in the market
        2. For each competitor, find:
           - Company positioning and target market
           - Pricing model and pricing tiers
           - Key features and differentiators
           - Strengths and weaknesses based on customer reviews or market perception
        3. Research the overall market size and growth trends
        4. Identify key customer pain points and needs
        5. Gather evidence with proper citations (URLs, sources)
        
        Return results in structured JSON with evidence_ids linking to sources.
        """,
        agent=agents["research_agent"],
        expected_output="JSON object with competitors array, market data, and evidence references",
    )

    analysis_task = Task(
        description="""
        Analyze the research findings and create structured outputs. Your tasks:
        1. Build a competitor comparison table with features, pricing, positioning
        2. Create a pricing matrix showing different competitors' pricing strategies
        3. Develop a SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) for the target product
        4. Identify market segments and customer personas
        5. Extract key market insights and trends
        
        Ensure all analysis is backed by evidence and cite sources.
        """,
        agent=agents["analyst_agent"],
        expected_output="Structured analysis with competitor tables, pricing matrix, SWOT, and market insights",
    )

    gtm_task = Task(
        description="""
        Create a comprehensive Go-To-Market (GTM) plan based on the research and analysis. Your plan should include:
        1. Target ICPs (Ideal Customer Profiles) - 2-3 primary segments with descriptions
        2. Value Proposition - clear, compelling value statement
        3. Messaging Framework - key messages for each segment
        4. Go-To-Market Channels - recommended channels (sales, marketing, partnerships, etc.) with rationale
        5. Launch Plan - phased approach with milestones and timeline
        6. Success Metrics - KPIs and measurement approach
        
        Base all recommendations on the research and competitive analysis.
        """,
        agent=agents["strategy_agent"],
        expected_output="Comprehensive GTM plan with ICPs, messaging, channels, and launch timeline",
    )

    orchestration_task = Task(
        description="""
        You are the Head Planner. Orchestrate the entire workflow and synthesize outputs:
        1. Kick off the Research Agent to gather market intelligence
        2. Once research is complete, trigger the Analyst Agent to synthesize findings
        3. Once analysis is ready, trigger the Strategy Agent to develop the GTM plan
        4. Review all outputs for completeness and coherence
        5. Create a final GTM planning document that synthesizes all findings
        6. Ensure all outputs are properly formatted and ready for export
        
        Your final output should be a comprehensive GTM document ready for export to Google Docs.
        """,
        agent=agents["head_planner"],
        expected_output="Final GTM plan document with all research, analysis, and strategy components",
    )

    return {
        "research": research_task,
        "analysis": analysis_task,
        "gtm": gtm_task,
        "orchestration": orchestration_task,
    }
