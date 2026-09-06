import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from analysis import AnalysisPackage, format_competitors_table, format_pricing_matrix, format_swot_section


class GTMExporter:
    """Export GTM plan to various formats."""

    def __init__(self, analysis_package: AnalysisPackage, config: Optional[Any] = None):
        self.analysis = analysis_package
        self.config = config

    def to_markdown(self) -> str:
        """Export GTM plan as Markdown."""
        lines = [
            f"# GTM Plan: {self.analysis.product_name}",
            "",
            "## Executive Summary",
            self.analysis.brief,
            "",
        ]

        # Market Overview Section
        if self.analysis.market_insights:
            lines.extend([
                "## Market Overview",
                json.dumps(self.analysis.market_insights, indent=2),
                "",
            ])

        # Competitive Landscape
        if self.analysis.competitors:
            lines.append("## Competitive Landscape")
            lines.append(format_competitors_table(self.analysis.competitors))
            lines.append("")

        # Pricing Analysis
        if self.analysis.pricing_matrix:
            lines.append("## Pricing Strategy")
            lines.append(format_pricing_matrix(self.analysis.pricing_matrix))
            lines.append("")

        # SWOT Analysis
        if self.analysis.swot:
            lines.append("## SWOT Analysis")
            lines.append(format_swot_section(self.analysis.swot))
            lines.append("")

        # Target ICPs
        if self.analysis.icps:
            lines.append("## Target ICPs (Ideal Customer Profiles)")
            for icp in self.analysis.icps:
                lines.append(f"\n### {icp.get('name', 'Segment')}")
                for key, value in icp.items():
                    if key != "name":
                        lines.append(f"- **{key}**: {value}")

        # Value Proposition
        if self.analysis.value_proposition:
            lines.extend([
                "",
                "## Value Proposition",
                self.analysis.value_proposition,
                "",
            ])

        # Messaging
        if self.analysis.messaging:
            lines.append("## Key Messaging")
            for audience, message in self.analysis.messaging.items():
                lines.append(f"\n### {audience}")
                lines.append(message)

        # Channels
        if self.analysis.channels:
            lines.append("\n## Go-To-Market Channels")
            for channel in self.analysis.channels:
                lines.append(f"\n### {channel.get('name', 'Channel')}")
                for key, value in channel.items():
                    if key != "name":
                        lines.append(f"- {key}: {value}")

        # Launch Plan
        if self.analysis.launch_plan:
            lines.append("\n## Launch Plan & Timeline")
            for phase in self.analysis.launch_plan:
                lines.append(f"\n### {phase.get('phase', 'Phase')}")
                lines.append(f"**Duration**: {phase.get('duration', 'TBD')}")
                if "milestones" in phase:
                    lines.append("**Milestones**:")
                    for milestone in phase["milestones"]:
                        lines.append(f"  - {milestone}")

        # Evidence Section
        if self.analysis.evidence:
            lines.append("\n## Research Evidence & Citations")
            for evid_id, evidence in self.analysis.evidence.items():
                lines.append(f"\n### {evidence.title}")
                lines.append(f"- **Source**: [{evidence.source_url}]({evidence.source_url})")
                lines.append(f"- **Type**: {evidence.evidence_type}")
                lines.append(f"- **Relevance**: {evidence.relevance_score}")
                lines.append(f"- **Summary**: {evidence.snippet}")

        return "\n".join(lines)

    def to_google_docs(self, title: str, folder_id: Optional[str] = None) -> Dict[str, str]:
        """Export to Google Docs."""
        if not self.config or not self.config.google_creds_path:
            raise ValueError("Google credentials not configured")

        from crewai_tools import GoogleDocsExporter

        exporter = GoogleDocsExporter(credentials_file=self.config.google_creds_path)
        markdown_content = self.to_markdown()

        # Convert markdown sections to Google Docs structure
        sections = self._parse_markdown_to_sections(markdown_content)
        result = exporter.create_doc_from_sections(title, sections, folder_id=folder_id)
        return result

    def to_json(self, filepath: str):
        """Export analysis to JSON."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        self.analysis.save_json(filepath)

    def to_markdown_file(self, filepath: str):
        """Save markdown to file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            f.write(self.to_markdown())

    def to_pdf(self, filepath: str):
        """Export to PDF (requires pypdf or similar)."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors

            pdf_file = SimpleDocTemplate(filepath, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
            story = []
            styles = getSampleStyleSheet()

            # Add title
            title_style = ParagraphStyle("CustomTitle", parent=styles["Heading1"], fontSize=24, textColor=colors.HexColor("#1F4788"), spaceAfter=12)
            story.append(Paragraph(f"GTM Plan: {self.analysis.product_name}", title_style))
            story.append(Spacer(1, 0.3 * inch))

            # Add executive summary
            story.append(Paragraph("Executive Summary", styles["Heading2"]))
            story.append(Paragraph(self.analysis.brief, styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))

            # Add SWOT
            if self.analysis.swot:
                story.append(PageBreak())
                story.append(Paragraph("SWOT Analysis", styles["Heading2"]))
                swot_text = format_swot_section(self.analysis.swot)
                story.append(Paragraph(swot_text.replace("\n", "<br/>"), styles["Normal"]))

            # Add competitors
            if self.analysis.competitors:
                story.append(PageBreak())
                story.append(Paragraph("Competitive Landscape", styles["Heading2"]))
                comp_text = format_competitors_table(self.analysis.competitors)
                story.append(Paragraph(comp_text.replace("\n", "<br/>"), styles["Normal"]))

            # Add value proposition
            if self.analysis.value_proposition:
                story.append(PageBreak())
                story.append(Paragraph("Value Proposition", styles["Heading2"]))
                story.append(Paragraph(self.analysis.value_proposition, styles["Normal"]))

            # Add GTM channels
            if self.analysis.channels:
                story.append(PageBreak())
                story.append(Paragraph("Go-To-Market Channels", styles["Heading2"]))
                for channel in self.analysis.channels:
                    story.append(Paragraph(f"<b>{channel.get('name')}</b>", styles["Normal"]))
                    for key, value in channel.items():
                        if key != "name":
                            story.append(Paragraph(f"• {key}: {value}", styles["Normal"]))

            # Build PDF
            pdf_file.build(story)
        except ImportError:
            raise ImportError("reportlab is required for PDF export. Install it with: pip install reportlab")

    @staticmethod
    def _parse_markdown_to_sections(markdown: str) -> List[Dict[str, Any]]:
        """Parse markdown into sections for Google Docs."""
        lines = markdown.split("\n")
        sections = []
        current_section = None

        for line in lines:
            if line.startswith("## "):
                if current_section:
                    sections.append(current_section)
                current_section = {"title": line[3:].strip(), "content": []}
            elif line.startswith("### "):
                if current_section:
                    current_section["content"].append(f"\n{line[4:].strip()}\n")
            elif current_section and line.strip():
                current_section["content"].append(line.strip())

        if current_section:
            sections.append(current_section)

        return sections
