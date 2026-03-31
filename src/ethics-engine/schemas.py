"""Pydantic schemas for Ethics Engine API."""

from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class ScenarioContext(BaseModel):
    """Context for an ethical scenario."""
    environment: Optional[str] = None
    robot_type: Optional[str] = None
    urgency: Optional[Literal["low", "medium", "high", "critical"]] = "medium"
    humans_nearby: bool = False
    safety_critical: bool = False
    custom: Optional[Dict[str, Any]] = None


class EthicsRequest(BaseModel):
    """Request to resolve an ethical scenario."""
    scenario: str = Field(..., description="Description of the ethical dilemma")
    context: Optional[ScenarioContext] = None
    frameworks: Optional[List[str]] = Field(
        default=None,
        description="Specific frameworks to invoke (auto-select if None)"
    )
    return_reasoning: bool = True
    mode: Literal["reasoning", "fast_decision"] = "reasoning"


class ReasoningStep(BaseModel):
    """A single step in the reasoning chain."""
    framework: str = Field(..., description="Ethical framework used")
    principle: str = Field(..., description="Core principle applied")
    argument: str = Field(..., description="Reasoning argument")
    philosophers: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


class FrameworkMatch(BaseModel):
    """Information about a matched framework."""
    id: str
    name: str
    philosophers: List[str]
    description: str
    best_for: List[str]


class AsimovComparison(BaseModel):
    """Comparison to Asimov's Laws."""
    law1_conflict: bool = False
    law2_conflict: bool = False
    law3_conflict: bool = False
    explanation: str = ""


class EthicsResponse(BaseModel):
    """Response from ethics engine."""
    request_id: str
    scenario: str
    conclusion: Literal[
        "APPROVAL",
        "CONDITIONAL_ACCEPTANCE", 
        "NEUTRAL",
        "REFUSAL",
        "CONDITIONAL_REFUSAL",
        "HUMAN_REVIEW_REQUIRED"
    ]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning_chain: List[ReasoningStep]
    frameworks_invoked: List[str]
    synthesis: str
    conclusions: List[str]
    asimov_comparison: Optional[AsimovComparison] = None
    uncertainty: Optional[str] = None
    next_steps: List[str] = Field(default_factory=list)
    human_review_recommended: bool = False
    reasoning_time_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CompareRequest(BaseModel):
    """Request to compare multiple actions."""
    actions: List[str]
    scenario: str
    context: Optional[ScenarioContext] = None
    frameworks: Optional[List[str]] = None


class CompareResult(BaseModel):
    """Result of comparing actions."""
    action: str
    score: float
    recommendation: str
    key_reasoning: str


class CompareResponse(BaseModel):
    """Response from action comparison."""
    request_id: str
    results: List[CompareResult]
    best_action: str
    alignment_score: float


class FeedbackRequest(BaseModel):
    """Feedback on a decision outcome."""
    request_id: str
    agent_decision: str
    outcome: str
    feedback: Optional[str] = None


class AuditEntry(BaseModel):
    """Audit log entry."""
    timestamp: datetime
    request_id: str
    agent_id: str
    scenario: str
    conclusion: str
    reasoning_summary: str
    frameworks: List[str]
