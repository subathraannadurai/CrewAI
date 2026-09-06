#!/usr/bin/env python
"""
Main entry point for the GTM Planning Workflow.

Usage:
    python main.py

Environment variables required:
    - AZURE_API_KEY
    - SERPER_API_KEY (or SERPAPI_KEY)

Optional environment variables:
    - MCP_SERVER_URL
    - MCP_API_KEY
    - GOOGLE_APPLICATION_CREDENTIALS
    - GOOGLE_DOCS_FOLDER_ID
"""

import json
import sys
from pathlib import Path

from crew import GTMWorkflow
from config import get_config
from logger import WorkflowLogger


def main():
    """Run the GTM planning workflow."""

    # Sample product brief
    brief = """
    Product: AI-powered project management tool designed for SMB SaaS companies
    Market: Small and medium-sized B2B SaaS companies (10-500 employees)
    Goal: Create a comprehensive go-to-market plan
    
    Key Requirements:
    - Identify primary competitors and their positioning
    - Analyze pricing strategies in the market
    - Develop target customer profiles
    - Create messaging and positioning strategy
    - Plan launch approach and timeline
    """

    product_name = "AI-Project-Manager"

    print("=" * 80)
    print("GTM Planning Workflow - Multi-Agent System")
    print("=" * 80)
    print(f"\nProduct: {product_name}")
    print(f"Brief: {brief[:100]}...\n")

    try:
        # Get configuration
        config = get_config()
        print(f"✓ Configuration loaded")
        print(f"  - Model: {config.model_name}")
        print(f"  - Output dir: {config.output_dir}")
        print(f"  - Max retries: {config.max_retries}\n")

        # Initialize workflow
        logger = WorkflowLogger(log_file=config.log_file, log_level=config.log_level)
        workflow = GTMWorkflow(config=config, logger=logger)
        print(f"✓ Workflow initialized")
        print(f"  - Agents: Head Planner, Research, Analyst, Strategy")
        print(f"  - Tasks: Orchestration, Research, Analysis, GTM Planning\n")

        # Run workflow
        print("Starting workflow execution...")
        print("-" * 80)

        result = workflow.run(
            brief=brief,
            product_name=product_name,
            export_formats=["json", "markdown", "docs", "pdf"],  # All formats
        )

        print("-" * 80)

        if result["success"]:
            print("\n✓ Workflow completed successfully!")
            print(f"\nOutputs:")
            for fmt, path in result["exports"].items():
                print(f"  - {fmt}: {path}")

            # Print metrics
            metrics = result["metrics"]
            print(f"\nMetrics:")
            print(f"  - Total tasks: {metrics['total_tasks']}")
            print(f"  - Completed: {metrics['completed_tasks']}")
            print(f"  - Duration: {metrics['total_duration']:.2f}s")
            print(f"  - Estimated cost: ${metrics['total_estimated_cost']:.4f}")
            print(f"  - Tokens used: {metrics['total_tokens']}")

            # Save summary
            summary_file = f"{config.output_dir}/workflow_summary.json"
            workflow.save_summary(filepath=summary_file)
            print(f"\nSummary saved to: {summary_file}")

        else:
            print(f"\n✗ Workflow failed: {result['error']}")
            sys.exit(1)

    except ValueError as e:
        print(f"\n✗ Configuration error: {str(e)}")
        print("\nRequired environment variables:")
        print("  - AZURE_API_KEY")
        print("  - SERPER_API_KEY (or SERPAPI_KEY)")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
