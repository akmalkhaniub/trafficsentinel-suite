# SPEC-06: Data Models, Telemetry Schemas, & Storage Architecture

## 1. Executive Summary
`SPEC-06` defines the data models, analytical tables, and evaluation schemas utilized across **TrafficSentinel Suite**.

To guarantee sub-second execution during investigations and evals without requiring massive external databases, the data tier utilizes:
1. **DuckDB**: Fast, in-process analytical SQL engine reading compressed Parquet files.
2. **Pydantic v2**: Type-safe Python models enforcing strict serialization, validation, and JSON Schema generation.

---

## 2. Analytical Telemetry Tables (DuckDB / Parquet)

### Table 1: `publisher_ivt_daily`
Stores aggregated daily Invalid Traffic metrics per publisher domain.
```sql
CREATE TABLE publisher_ivt_daily (
    date DATE NOT NULL,
    publisher_id VARCHAR NOT NULL,
    domain VARCHAR NOT NULL,
    total_impressions BIGINT NOT NULL,
    valid_impressions BIGINT NOT NULL,
    givt_impressions BIGINT NOT NULL,    -- General Invalid Traffic (data centers, bots)
    sivt_impressions BIGINT NOT NULL,    -- Sophisticated Invalid Traffic (laundering, hijacking)
    givt_rate DOUBLE NOT NULL,           -- givt_impressions / total_impressions
    sivt_rate DOUBLE NOT NULL,           -- sivt_impressions / total_impressions
    top_sivt_category VARCHAR,           -- 'hidden_ad', 'device_spoof', 'click_spam'
    PRIMARY KEY (date, publisher_id)
);
```

### Table 2: `ctv_app_telemetry`
Stores hardware and playback diagnostics for CTV apps across Roku, FireTV, and Apple TV.
```sql
CREATE TABLE ctv_app_telemetry (
    bundle_id VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,          -- 'roku', 'firetv', 'appletv', 'androidtv'
    app_name VARCHAR NOT NULL,
    daily_active_devices INT NOT NULL,
    screensaver_playback_ratio DOUBLE,  -- Ad impressions fired while screen is in standby
    user_agent_entropy_score DOUBLE,   -- Entropy variance in client headers (0.0 to 1.0)
    ssai_server_ip_diversity INT,       -- Number of distinct SSAI proxies
    is_kid_directed BOOLEAN NOT NULL,   -- Children's app indicator
    coppa_compliant BOOLEAN NOT NULL,
    last_audited_timestamp TIMESTAMP NOT NULL,
    PRIMARY KEY (bundle_id, platform)
);
```

### Table 3: `bidstream_auction_anomalies`
Stores high-frequency anomaly clusters detected in programmatic RTB streams.
```sql
CREATE TABLE bidstream_auction_anomalies (
    id VARCHAR PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    seller_id VARCHAR NOT NULL,
    exchange_id VARCHAR NOT NULL,
    anomaly_type VARCHAR NOT NULL,      -- 'bid_duplication', 'ip_cluster', 'geo_mismatch'
    duplicated_bid_ratio DOUBLE,
    suspicious_cidr_prefix VARCHAR,
    anomaly_confidence DOUBLE NOT NULL
);
```

---

## 3. Pydantic v2 Data Models (Agent & MCP Interfaces)

### Clarification Request Model
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ClarificationOption(BaseModel):
    id: str = Field(description="Unique choice identifier")
    label: str = Field(description="Human readable choice for the client")

class ClarificationPayload(BaseModel):
    needs_clarification: bool = True
    missing_slots: List[str] = Field(description="List of slots that failed completeness check")
    primary_question: str = Field(description="The clarifying question to present to the user")
    suggested_options: List[ClarificationOption] = Field(default_factory=list)
```

### Evaluation Result Model
```python
class ScenarioEvaluationResult(BaseModel):
    scenario_id: str
    scenario_cohort: str # 'ambiguous' | 'direct' | 'borderline' | 'adversarial'
    clarification_triggered: bool
    expected_clarification: bool
    tool_invoked: Optional[str]
    expected_tool: Optional[str]
    parameters_matched: bool
    overstatement_detected: bool
    tokens_consumed: int
    passed: bool
    failure_reason: Optional[str] = None
```
