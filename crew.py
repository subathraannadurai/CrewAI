from pathlib import Path
from typing import Optional

from crewai import Crew

from agents import create_agents
from analysis import AnalysisPackage
from config import Config, get_config
from exporter import GTMExporter
from logger import WorkflowLogger
from tasks import create_tasks


class GTMWorkflow:
    """Main orchestrator for the GTM planning workflow."""

    def __init__(self, config: Optional[Config] = None, logger: Optional[WorkflowLogger] = None):
        self.config = config or get_config()
        self.logger = logger or WorkflowLogger(log_file=self.config.log_file, log_level=self.config.log_level)

        # Create output directory
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

        # Initialize agents and tasks
        self.agents_dict = create_agents(self.config)
        self.tasks_dict = create_tasks(self.agents_dict)

        # Initialize analysis package
        self.analysis_package: Optional[AnalysisPackage] = None

    def run(self, brief: str, product_name: str = "New Product", export_formats: list = None) -> dict:
        """
        Run the full GTM planning workflow.

        Args:
            brief: The product/market brief
            product_name: Name of the product
            export_formats: List of export formats ['markdown', 'json', 'docs', 'pdf']

        Returns:
            Dictionary with results and output paths
        """
        if export_formats is None:
            export_formats = ["json", "markdown"]

        self.logger.logger.info(f"Starting GTM workflow for {product_name}")
        self.analysis_package = AnalysisPackage(brief=brief, product_name=product_name)

        try:
            # Create crew with all agents and tasks
            crew = Crew(
                agents=[
                    self.agents_dict["head_planner"],
                    self.agents_dict["research_agent"],
                    self.agents_dict["analyst_agent"],
                    self.agents_dict["strategy_agent"],
                ],
                tasks=[
                    self.tasks_dict["orchestration"],  # Head planner orchestrates everything
                    self.tasks_dict["research"],
                    self.tasks_dict["analysis"],
                    self.tasks_dict["gtm"],
                ],
                verbose=True,
                memory=False,
                cache_enabled=False,
            )

            # Run the crew
            metric = self.logger.start_task("GTM_Workflow", "head_planner")
            result = crew.kickoff(inputs={"brief": brief, "product_name": product_name})
            self.logger.complete_task(metric, estimated_tokens=2000)

            # Store result
            workflow_output = str(result)
            self.analysis_package.market_insights["workflow_output"] = workflow_output

            # Export results
            exports = self._export_results(product_name, export_formats)

            return {
                "success": True,
                "product_name": product_name,
                "workflow_output": workflow_output,
                "exports": exports,
                "metrics": self.logger.get_summary(),
            }

        except Exception as e:
            self.logger.logger.error(f"Workflow failed: {str(e)}")
            metric = self.logger.start_task("GTM_Workflow_Error", "head_planner")
            self.logger.complete_task(metric, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "metrics": self.logger.get_summary(),
            }

    def _export_results(self, product_name: str, formats: list) -> dict:
        """Export workflow results to specified formats."""
        exporter = GTMExporter(self.analysis_package, config=self.config)
        exports = {}

        if "json" in formats:
            json_path = f"{self.config.output_dir}/{product_name}_research.json"
            exporter.to_json(json_path)
            exports["json"] = json_path
            self.logger.logger.info(f"Exported JSON to {json_path}")

        if "markdown" in formats:
            md_path = f"{self.config.output_dir}/{product_name}_gtm_plan.md"
            exporter.to_markdown_file(md_path)
            exports["markdown"] = md_path
            self.logger.logger.info(f"Exported Markdown to {md_path}")

        if "docs" in formats and self.config.google_creds_path:
            try:
                docs_result = exporter.to_google_docs(
                    title=f"GTM Plan: {product_name}",
                    folder_id=self.config.google_docs_folder_id,
                )
                exports["google_docs"] = docs_result
                self.logger.logger.info(f"Exported to Google Docs: {docs_result['url']}")
            except Exception as e:
                self.logger.logger.error(f"Failed to export to Google Docs: {str(e)}")

        if "pdf" in formats:
            try:
                pdf_path = f"{self.config.output_dir}/{product_name}_gtm_plan.pdf"
                exporter.to_pdf(pdf_path)
                exports["pdf"] = pdf_path
                self.logger.logger.info(f"Exported PDF to {pdf_path}")
            except ImportError:
                self.logger.logger.warning("reportlab not installed; skipping PDF export")

        return exports

    def get_summary(self) -> dict:
        """Get workflow summary including metrics."""
        return self.logger.get_summary()

    def save_summary(self, filepath: str = "workflow_summary.json"):
        """Save workflow summary to file."""
        self.logger.save_summary(output_file=filepath)
