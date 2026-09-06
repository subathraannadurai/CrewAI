import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TaskMetric:
    """Metrics for a single task execution."""

    task_name: str
    agent_name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: float = 0.0
    estimated_tokens: int = 0
    estimated_cost: float = 0.0
    status: str = "running"
    error: Optional[str] = None

    def complete(self, estimated_tokens: int = 0, status: str = "completed", error: Optional[str] = None):
        """Mark task as complete."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.estimated_tokens = estimated_tokens
        self.estimated_cost = self._estimate_cost(estimated_tokens)
        self.status = status
        self.error = error

    @staticmethod
    def _estimate_cost(tokens: int, model: str = "gpt-4-turbo") -> float:
        """Estimate cost based on tokens (rough estimate for gpt-4-turbo)."""
        # gpt-4-turbo: ~$0.01 per 1k input tokens, $0.03 per 1k output tokens
        # Rough estimate: $0.015 per 1k tokens average
        return (tokens / 1000) * 0.015


class WorkflowLogger:
    """Logger for the GTM workflow with metrics tracking."""

    def __init__(self, log_file: str = "gtm_workflow.log", log_level: str = "INFO"):
        self.log_file = log_file
        self.log_level = log_level
        self.metrics: List[TaskMetric] = []
        self.session_start = datetime.now()

        # Configure Python logger
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def start_task(self, task_name: str, agent_name: str) -> TaskMetric:
        """Start logging a task."""
        metric = TaskMetric(task_name=task_name, agent_name=agent_name)
        self.metrics.append(metric)
        self.logger.info(f"Starting task: {task_name} (agent: {agent_name})")
        return metric

    def complete_task(self, metric: TaskMetric, estimated_tokens: int = 0, error: Optional[str] = None):
        """Mark a task as complete."""
        status = "error" if error else "completed"
        metric.complete(estimated_tokens=estimated_tokens, status=status, error=error)
        log_level = logging.ERROR if error else logging.INFO
        self.logger.log(
            log_level,
            f"Task {metric.task_name} completed in {metric.duration:.2f}s "
            f"(tokens: {estimated_tokens}, cost: ${metric.estimated_cost:.4f})",
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all tasks."""
        total_duration = sum(m.duration for m in self.metrics)
        total_cost = sum(m.estimated_cost for m in self.metrics)
        total_tokens = sum(m.estimated_tokens for m in self.metrics)
        session_duration = (datetime.now() - self.session_start).total_seconds()

        return {
            "session_start": self.session_start.isoformat(),
            "session_duration_seconds": session_duration,
            "total_tasks": len(self.metrics),
            "completed_tasks": sum(1 for m in self.metrics if m.status == "completed"),
            "failed_tasks": sum(1 for m in self.metrics if m.status == "error"),
            "total_duration": total_duration,
            "total_tokens": total_tokens,
            "total_estimated_cost": total_cost,
            "tasks": [asdict(m) for m in self.metrics],
        }

    def save_summary(self, output_file: str = "workflow_summary.json"):
        """Save summary to JSON file."""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(self.get_summary(), f, indent=2)
        self.logger.info(f"Workflow summary saved to {output_file}")

    def log_event(self, level: str, message: str, **kwargs):
        """Log a custom event."""
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        if kwargs:
            message = f"{message} | {json.dumps(kwargs)}"
        log_func(message)
