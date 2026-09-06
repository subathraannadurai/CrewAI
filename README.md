# CrewAI GTM Planning Multi-Agent Workflow

A comprehensive, production-ready multi-agent system for market research and go-to-market (GTM) planning using CrewAI.

## Overview

This system automates the GTM planning process by orchestrating four specialized AI agents:

1. **Head Planner** - Orchestrator and documenter
   - Coordinates the entire workflow
   - Synthesizes outputs into a cohesive GTM plan
   - Ensures quality and completeness

2. **Research Agent** - Market intelligence collector
   - Finds and collects competitor data
   - Identifies market trends and customer insights
   - Gathers evidence with proper citations

3. **Analyst Agent** - Data synthesizer
   - Creates competitor comparison tables
   - Builds pricing matrices
   - Develops SWOT analysis and market insights

4. **Strategy Agent** - GTM planner
   - Identifies target ICPs (Ideal Customer Profiles)
   - Crafts value propositions and messaging
   - Defines go-to-market channels and launch plan

## Features

✅ **Multi-Agent Orchestration** - Collaborative AI agents with delegation  
✅ **Research Evidence** - All findings backed by sources with proper citations (JSON format)  
✅ **Structured Analysis** - Competitor tables, pricing matrices, SWOT, 4P/7P analysis  
✅ **Comprehensive GTM Plan** - ICPs, value proposition, messaging, channels, launch timeline  
✅ **Multiple Export Formats** - JSON, Markdown, Google Docs, PDF  
✅ **Production Monitoring** - Logging, cost tracking, latency measurement, retry logic  
✅ **Error Handling** - Graceful fallbacks and detailed error reporting  

## Project Structure

```
crewai_gtm/
├── __init__.py              # Package exports
├── config.py                # Configuration management
├── agents.py                # Agent definitions
├── tasks.py                 # Task definitions
├── analysis.py              # Data models for research and analysis
├── exporter.py              # Export to various formats (Docs, PDF, Markdown)
├── logger.py                # Logging and metrics tracking
├── crew.py                  # Main workflow orchestrator
├── main.py                  # Entry point with example
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Installation

### Prerequisites

- Python 3.10+
- OpenAI API key
- SerpAPI key (for market research)
- (Optional) Google Cloud credentials for Google Docs export
- (Optional) CrewAI API key for advanced features

### Setup

1. Clone or download the project:
```bash
cd crewai_gtm
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
export OPENAI_API_KEY="your-openai-key"
export SERPER_API_KEY="your-serpapi-key"

# Optional: for Google Docs export
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
export GOOGLE_DOCS_FOLDER_ID="your-folder-id"

# Optional: for MCP integration
export MCP_SERVER_URL="http://localhost:8000"
export MCP_API_KEY="your-mcp-key"
```

## Usage

### Quick Start

```python
from crewai_gtm import GTMWorkflow, get_config

# Get configuration from environment
config = get_config()

# Create workflow
workflow = GTMWorkflow(config=config)

# Run the workflow
result = workflow.run(
    brief="AI project management tool for SMB SaaS",
    product_name="AI-ProjectManager",
    export_formats=["json", "markdown", "docs", "pdf"]
)

# Check results
if result["success"]:
    print(f"Exports: {result['exports']}")
    print(f"Metrics: {result['metrics']}")
```

### Running from Command Line

```bash
python main.py
```

This will:
1. Initialize the workflow with environment configuration
2. Run all four agents in sequence
3. Collect research evidence with citations
4. Generate competitor analysis and SWOT
5. Create a comprehensive GTM plan
6. Export to JSON, Markdown, Google Docs, and PDF
7. Print metrics including latency and estimated cost

### Output

The workflow generates:

```
gtm_output/
├── AI-ProjectManager_research.json      # Full research data with evidence
├── AI-ProjectManager_gtm_plan.md        # Markdown version of plan
├── AI-ProjectManager_gtm_plan.pdf       # PDF export
└── workflow_summary.json                # Metrics and performance data
```

## Configuration

All configuration is managed through environment variables and `config.py`:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4 |
| `SERPER_API_KEY` | Yes | SerpAPI key for web search |
| `GOOGLE_APPLICATION_CREDENTIALS` | No | Path to Google service account JSON |
| `GOOGLE_DOCS_FOLDER_ID` | No | Drive folder ID for docs export |
| `MCP_SERVER_URL` | No | URL of MCP server for research |
| `MCP_API_KEY` | No | Bearer token for MCP requests |
| `OPENAI_MODEL_NAME` | No | Model name (default: gpt-4-turbo) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

## Architecture

### Agent Flow

```
Head Planner (Orchestrator)
├── Triggers Research Agent
│   ├── Search market data
│   ├── Find competitors
│   └── Collect evidence with citations
├── Triggers Analyst Agent
│   ├── Build competitor table
│   ├── Create pricing matrix
│   └── Develop SWOT analysis
└── Triggers Strategy Agent
    ├── Define target ICPs
    ├── Craft value proposition
    └── Plan launch channels
```

### Research Evidence Format

All research data is stored in JSON with proper citations:

```json
{
  "evidence": {
    "comp_001": {
      "id": "comp_001",
      "source_url": "https://example.com",
      "title": "Company Name",
      "snippet": "Key information...",
      "evidence_type": "web",
      "extracted_facts": {
        "pricing": "$99/month",
        "features": ["Feature A", "Feature B"]
      }
    }
  },
  "competitors": [
    {
      "name": "Competitor",
      "url": "https://competitor.com",
      "pricing_model": "SaaS",
      "evidence_ids": ["comp_001"]
    }
  ]
}
```

### Tracking & Metrics

The workflow tracks:

- **Task Duration**: Time spent on each agent task
- **Token Usage**: Estimated tokens used for cost calculation
- **Estimated Cost**: OpenAI API cost based on tokens (rough estimate)
- **Success/Failure**: Each task status and error messages
- **Retry Attempts**: Failed API calls and retries

Example metrics output:

```json
{
  "total_tasks": 4,
  "completed_tasks": 4,
  "total_duration": 45.23,
  "total_tokens": 8500,
  "total_estimated_cost": 0.1275,
  "tasks": [
    {
      "task_name": "research",
      "agent_name": "research_agent",
      "duration": 12.45,
      "status": "completed"
    }
  ]
}
```

## Error Handling & Retries

The system implements:

1. **Automatic Retries**: Failed API calls retry with exponential backoff
2. **Graceful Degradation**: Optional services (MCP, Google Docs) fail gracefully
3. **Detailed Logging**: All errors logged with context
4. **Error Recovery**: Workflow continues even if some agents partially fail

## Export Formats

### JSON
Complete research data with all evidence, structured as an `AnalysisPackage`.

### Markdown
Human-readable report with sections for:
- Executive summary
- Market overview
- Competitive landscape
- SWOT analysis
- Target ICPs
- Value proposition
- Messaging framework
- Go-to-market channels
- Launch plan
- Research evidence & citations

### Google Docs
Formatted document in Google Drive with:
- Proper heading hierarchy
- Structured sections
- Easy sharing and collaboration

### PDF
Print-ready report with:
- Professional formatting
- Colored headers
- Section breaks
- All content sections

## Development

### Adding Custom Tools

Extend the agents with custom tools:

```python
from crewai.tools import tool

@tool("Custom research")
def custom_research(query: str) -> str:
    """Your custom research tool."""
    # Implementation
    return result

# Add to agents in agents.py
agent = Agent(..., tools=[custom_research])
```

### Extending Analysis

Add new analysis types to `analysis.py`:

```python
@dataclass
class CustomAnalysis:
    """Your custom analysis data."""
    pass

class AnalysisPackage:
    def add_custom_analysis(self, analysis: CustomAnalysis):
        # Store and export your custom analysis
        pass
```

## Performance Optimization

- **Cache**: CrewAI caches agent responses (disable with `cache_enabled=False`)
- **Parallel Tasks**: Agents can be configured to run in parallel
- **Token Limits**: Configure `max_tokens` per agent to control costs
- **Timeout**: Set request timeouts to prevent hanging

## Troubleshooting

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY="sk-..."
```

### "SerpAPI key not provided"
```bash
export SERPER_API_KEY="your-key"
# or
export SERPAPI_KEY="your-key"
```

### Google Docs export fails
- Ensure service account has Drive and Docs API access
- Check `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON
- Verify folder ID is correct

### PDF export fails
Install reportlab:
```bash
pip install reportlab
```

## Best Practices

1. **Start Small**: Test with a brief product description before complex research
2. **Monitor Costs**: Check `workflow_summary.json` to track API spending
3. **Save Evidence**: Always export JSON to preserve citations
4. **Version Control**: Keep GTM plans in version control with timestamps
5. **Review Outputs**: AI-generated content should be reviewed by humans
6. **Error Monitoring**: Set up alerts on failed tasks in production

## Advanced Usage

### Custom Configuration

```python
from crewai_gtm import Config, GTMWorkflow

config = Config(
    model_name="gpt-4-turbo",
    temperature=0.5,
    max_retries=5,
    output_dir="./my_output"
)
workflow = GTMWorkflow(config=config)
```

### Processing Existing Research

```python
from crewai_gtm import AnalysisPackage

# Load previous research
analysis = AnalysisPackage.from_json("previous_research.json")

# Generate new exports
from crewai_gtm import GTMExporter
exporter = GTMExporter(analysis)
exporter.to_google_docs("My Plan", folder_id="folder-123")
```

### Batch Processing

```python
from crewai_gtm import GTMWorkflow, get_config

workflow = GTMWorkflow(config=get_config())

products = [
    ("AI-Manager", "AI project management tool"),
    ("Smart-CRM", "AI-powered CRM for SMBs"),
]

for product_name, brief in products:
    result = workflow.run(brief=brief, product_name=product_name)
    print(f"{product_name}: {result['success']}")
```

## Cost Estimation

Typical GTM planning workflow costs:

- **Research phase**: ~2,000 tokens → ~$0.03
- **Analysis phase**: ~3,000 tokens → ~$0.045
- **GTM planning**: ~2,000 tokens → ~$0.03
- **Total**: ~7,000 tokens → ~$0.105

Actual costs vary based on:
- Model complexity (gpt-4 vs gpt-4-turbo)
- Research depth (number of competitors, market size)
- Number of API retries
- Export formats

## Support

For issues or questions:
1. Check error logs in `gtm_workflow.log`
2. Review `workflow_summary.json` for metrics
3. Enable verbose logging with `log_level="DEBUG"`

## License

MIT License - See LICENSE file

## Contributing

Contributions welcome! Please:
1. Test changes locally
2. Update documentation
3. Follow existing code style
4. Add unit tests for new features

---

**Last Updated**: July 2026  
**Version**: 1.0.0
