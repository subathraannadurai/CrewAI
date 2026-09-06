import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class CompetitorEntry:
    """A single competitor record."""

    name: str
    url: str
    positioning: str
    target_market: str
    pricing_model: str
    key_features: List[str]
    strengths: List[str]
    weaknesses: List[str]
    evidence_ids: List[str] = None

    def __post_init__(self):
        if self.evidence_ids is None:
            self.evidence_ids = []


@dataclass
class ResearchEvidence:
    """A single piece of research evidence with citation."""

    id: str
    source_url: str
    title: str
    snippet: str
    author: Optional[str] = None
    published_date: Optional[str] = None
    relevance_score: float = 0.8
    evidence_type: str = "web"  # web, report, patent, interview
    extracted_facts: Dict[str, Any] = None

    def __post_init__(self):
        if self.extracted_facts is None:
            self.extracted_facts = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class AnalysisPackage:
    """Container for all research and analysis outputs."""

    def __init__(self, brief: str, product_name: str):
        self.brief = brief
        self.product_name = product_name
        self.evidence: Dict[str, ResearchEvidence] = {}
        self.competitors: List[CompetitorEntry] = []
        self.pricing_matrix: Dict[str, Dict[str, Any]] = {}
        self.swot: Dict[str, List[str]] = {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}
        self.market_insights: Dict[str, Any] = {}
        self.icps: List[Dict[str, str]] = []
        self.value_proposition: str = ""
        self.messaging: Dict[str, str] = {}
        self.channels: List[Dict[str, Any]] = []
        self.launch_plan: List[Dict[str, Any]] = []

    def add_evidence(self, evidence: ResearchEvidence):
        """Add a piece of evidence."""
        self.evidence[evidence.id] = evidence

    def add_competitor(self, competitor: CompetitorEntry):
        """Add a competitor."""
        self.competitors.append(competitor)

    def get_competitors_table(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get competitors as a formatted table."""
        return {
            "competitors": [
                {
                    "name": c.name,
                    "url": c.url,
                    "positioning": c.positioning,
                    "target_market": c.target_market,
                    "pricing_model": c.pricing_model,
                    "key_features": c.key_features,
                    "strengths": c.strengths,
                    "weaknesses": c.weaknesses,
                }
                for c in self.competitors
            ]
        }

    def to_json(self) -> str:
        """Export full package as JSON."""
        data = {
            "brief": self.brief,
            "product_name": self.product_name,
            "evidence": {k: v.to_dict() for k, v in self.evidence.items()},
            "competitors": [asdict(c) for c in self.competitors],
            "pricing_matrix": self.pricing_matrix,
            "swot": self.swot,
            "market_insights": self.market_insights,
            "icps": self.icps,
            "value_proposition": self.value_proposition,
            "messaging": self.messaging,
            "channels": self.channels,
            "launch_plan": self.launch_plan,
        }
        return json.dumps(data, indent=2)

    def save_json(self, filepath: str):
        """Save analysis to JSON file."""
        with open(filepath, "w") as f:
            f.write(self.to_json())

    @classmethod
    def from_json(cls, filepath: str) -> "AnalysisPackage":
        """Load analysis from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        pkg = cls(data["brief"], data["product_name"])
        for evid in data.get("evidence", {}).values():
            pkg.add_evidence(ResearchEvidence(**evid))
        for comp in data.get("competitors", []):
            pkg.add_competitor(CompetitorEntry(**comp))
        pkg.pricing_matrix = data.get("pricing_matrix", {})
        pkg.swot = data.get("swot", {})
        pkg.market_insights = data.get("market_insights", {})
        pkg.icps = data.get("icps", [])
        pkg.value_proposition = data.get("value_proposition", "")
        pkg.messaging = data.get("messaging", {})
        pkg.channels = data.get("channels", [])
        pkg.launch_plan = data.get("launch_plan", [])
        return pkg


def format_swot_section(swot: Dict[str, List[str]]) -> str:
    """Format SWOT analysis as text."""
    lines = ["SWOT Analysis:\n"]
    for category, items in swot.items():
        lines.append(f"\n{category.upper()}:")
        for item in items:
            lines.append(f"  • {item}")
    return "\n".join(lines)


def format_competitors_table(competitors: List[CompetitorEntry]) -> str:
    """Format competitors as a readable table."""
    lines = ["Competitor Analysis:\n"]
    for comp in competitors:
        lines.append(f"\n{comp.name}")
        lines.append(f"  URL: {comp.url}")
        lines.append(f"  Positioning: {comp.positioning}")
        lines.append(f"  Pricing: {comp.pricing_model}")
        lines.append(f"  Key Features: {', '.join(comp.key_features)}")
    return "\n".join(lines)


def format_pricing_matrix(pricing: Dict[str, Dict[str, Any]]) -> str:
    """Format pricing matrix as text."""
    lines = ["Pricing Matrix:\n"]
    for product, details in pricing.items():
        lines.append(f"\n{product}:")
        for key, value in details.items():
            lines.append(f"  {key}: {value}")
    return "\n".join(lines)
