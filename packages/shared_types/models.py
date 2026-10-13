"""
TrafficSentinel Suite — Shared Data Models & Schemas
Codified according to SPEC-06 (Data Models, Telemetry Schemas & Storage)
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. Interactive Clarification Models
# ---------------------------------------------------------------------------

class ClarificationOption(BaseModel):
    """A structured multiple-choice option presented to the user during disambiguation."""
    id: str = Field(description="Unique choice identifier")
    label: str = Field(description="Human-readable choice label")
    description: Optional[str] = Field(default=None, description="Explanation of this option")


class ClarificationPayload(BaseModel):
    """Payload produced when an investigation request is ambiguous or underspecified."""
    needs_clarification: bool = Field(default=True, description="True if clarification is required")
    completeness_score: float = Field(ge=0.0, le=1.0, description="Completeness score (0.0 to 1.0)")
    missing_slots: List[str] = Field(default_factory=list, description="Required parameters missing from prompt")
    primary_question: str = Field(description="The clarifying question to present to the user")
    suggested_options: List[ClarificationOption] = Field(default_factory=list, description="Selectable options")


# ---------------------------------------------------------------------------
# 2. AdStream MCP Tool Result Models
# ---------------------------------------------------------------------------

class IVTMetricsResult(BaseModel):
    """Results returned by inspect_publisher_ivt."""
    publisher_id: str
    domain: str
    total_impressions: int
    valid_impressions: int
    givt_impressions: int
    sivt_impressions: int
    givt_rate: float = Field(ge=0.0, le=1.0, description="General IVT percentage")
    sivt_rate: float = Field(ge=0.0, le=1.0, description="Sophisticated IVT percentage")
    top_sivt_category: str
    risk_tier: Literal["LOW", "ELEVATED", "HIGH", "CRITICAL"]
    token_usage_estimated: int = Field(default=0, description="Estimated tokens for this response")


class CTVTelemetryResult(BaseModel):
    """Results returned by audit_ctv_telemetry."""
    bundle_id: str
    platform: Literal["roku", "firetv", "appletv", "androidtv"]
    app_name: str
    daily_active_devices: int
    screensaver_playback_ratio: float = Field(ge=0.0, le=1.0, description="Impressions while screen is inactive")
    user_agent_entropy_score: float = Field(ge=0.0, le=1.0, description="Entropy variance in client headers")
    ssai_server_ip_diversity: int = Field(description="Count of distinct SSAI proxy IPs")
    is_kid_directed: bool
    coppa_compliant: bool
    anomalous_signals: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    token_usage_estimated: int = Field(default=0)


class BidstreamAnomalyCluster(BaseModel):
    """Individual anomaly cluster in bidstream."""
    seller_id: str
    anomaly_type: Literal["bid_duplication", "ip_cluster", "geo_mismatch"]
    metric_value: float
    confidence: float


class BidstreamAnomalyResult(BaseModel):
    """Results returned by query_bidstream_anomalies."""
    seller_id: str
    total_scanned_auctions: int
    anomalies_detected: List[BidstreamAnomalyCluster] = Field(default_factory=list)
    risk_summary: str
    token_usage_estimated: int = Field(default=0)


class COPPACheckResult(BaseModel):
    """Results returned by verify_coppa_compliance."""
    app_id: str
    store: Literal["google_play", "apple_appstore", "roku_channel_store"]
    is_child_directed: bool
    persistent_identifiers_shared: List[str] = Field(default_factory=list)
    has_compliant_privacy_policy: bool
    unicef_trust_risk_score: float = Field(ge=0.0, le=100.0, description="0=Safe, 100=Severe Risk")
    compliance_status: Literal["COMPLIANT", "AUDIT_REQUIRED", "NON_COMPLIANT"]
    token_usage_estimated: int = Field(default=0)


# ---------------------------------------------------------------------------
# 3. Agent Investigation Request & Response
# ---------------------------------------------------------------------------

class InvestigationRequest(BaseModel):
    """Client request sent to TrafficSentinel AI."""
    session_id: str = Field(description="Conversation or task session identifier")
    query: str = Field(description="Natural language instruction from customer")
    context_history: List[Dict[str, str]] = Field(default_factory=list, description="Prior conversation turns")


class InvestigationResponse(BaseModel):
    """Agent response, either a clarification request or a final forensic report."""
    session_id: str
    is_clarification: bool
    content: str
    clarification_payload: Optional[ClarificationPayload] = None
    tools_called: List[str] = Field(default_factory=list)
    calibrated_confidence: Literal["NORMAL", "ELEVATED", "CONFIRMED_HIGH_RISK"] = "NORMAL"
    anti_injection_flags: List[str] = Field(default_factory=list)
    total_tokens_consumed: int = Field(default=0)


# ---------------------------------------------------------------------------
# 4. Evaluation Suite Models
# ---------------------------------------------------------------------------

class EvaluationScenario(BaseModel):
    """Ground-truth scenario schema for PromptEval Studio."""
    id: str = Field(description="Unique scenario ID, e.g. SCENARIO-001")
    title: str
    cohort: Literal["ambiguous", "direct", "borderline", "adversarial"]
    prompt: str
    expected_action: Literal["clarify", "call_tool", "reject_injection"]
    expected_tool: Optional[str] = None
    expected_tool_params: Optional[Dict[str, Any]] = None
    forbidden_words_in_response: List[str] = Field(
        default_factory=list,
        description="Words that indicate unwarranted overstatement or security leakage"
    )
    max_token_budget: int = Field(default=800)


class ScenarioEvaluationResult(BaseModel):
    """Result of running a single scenario through PromptEval Studio."""
    scenario_id: str
    cohort: str
    passed: bool
    clarification_matched: bool
    tool_matched: bool
    overstatement_free: bool
    injection_defended: bool
    tokens_consumed: int
    duration_ms: float
    failure_reasons: List[str] = Field(default_factory=list)


class EvalSuiteSummary(BaseModel):
    """Summary metrics of an entire evaluation run."""
    total_scenarios: int
    passed_scenarios: int
    pass_rate: float
    clarification_trigger_rate: float
    tool_selection_accuracy: float
    calibrated_confidence_rate: float
    injection_defense_rate: float
    average_latency_ms: float
    status: Literal["PASS", "FAIL"]
