# SPEC-03: AdStream MCP — Model Context Protocol Tool Surface & Context Budgeting

## 1. Executive Summary
The Pixalate JD highlights:
> *"Work with engineering on MCP tool surfaces: which tools exist, how they are described, and how those descriptions drive correct selection... Engineer context strategies: what the agent sees, in what order, within what budget. Tune for cost and latency as well as accuracy."*

`SPEC-03` specifies **AdStream MCP**, a production Model Context Protocol server exposing ad-tech fraud forensics and telemetry to LLM agents with deterministic schemas, semantic description engineering, and dynamic token budgeting.

---

## 2. Server Architecture & Transports

AdStream MCP is built using **FastMCP (Python)** and supports dual transports:
1. **`stdio`**: For local CLI tools and single-tenant agent harnesses.
2. **Server-Sent Events (`SSE`)**: For multi-tenant distributed cloud swarms and remote agent invocations via HTTP.

```text
┌────────────────────────────────────────────────────────┐
│                   TrafficSentinel AI                   │
└───────────────────────────┬────────────────────────────┘
                            │ JSON-RPC 2.0 (MCP Protocol)
┌───────────────────────────▼────────────────────────────┐
│                    AdStream MCP Server                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │               Tool Routing & Security            │  │
│  └──────────┬────────────────────────────┬──────────┘  │
│             │                            │             │
│  ┌──────────▼───────────────┐ ┌──────────▼──────────┐  │
│  │  Telemetry Query Engine  │ │  Compliance Engine  │  │
│  │   (DuckDB Parquet Lake)  │ │ (COPPA & App Store) │  │
│  └──────────────────────────┘ └─────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 3. Tool Surface & Semantic Description Engineering

LLM tool routing failures almost always originate from poorly phrased tool descriptions. AdStream MCP uses **Action-Constraint-Boundary** semantic descriptions:

### Tool 1: `inspect_publisher_ivt`
```python
@mcp.tool(
    name="inspect_publisher_ivt",
    description="""
    Queries historical Invalid Traffic (IVT) metrics for a specific programmatic publisher domain or ID.
    RETURNS: GIVT % (known data center IPs, bots, crawlers) and SIVT % (app session hijacking, hidden iframes, proxy rotation).
    WHEN TO USE: Use ONLY when auditing overall domain traffic quality or publisher fraud reputation.
    DO NOT USE FOR: Individual mobile/CTV app audits (use audit_ctv_telemetry instead) or raw bidstream packet logs.
    """
)
def inspect_publisher_ivt(
    publisher_id: str,
    start_date: str, # ISO-8601 (YYYY-MM-DD)
    end_date: str,   # ISO-8601 (YYYY-MM-DD)
    breakdown: Optional[str] = "daily" # 'daily' | 'channel' | 'geo'
) -> dict: ...
```

### Tool 2: `audit_ctv_telemetry`
```python
@mcp.tool(
    name="audit_ctv_telemetry",
    description="""
    Performs forensic hardware and telemetry analysis on a Connected TV (CTV) application bundle.
    RETURNS: Hardware telemetry consistency, screensaver impression playback ratio, user-agent entropy score, and SSAI (Server-Side Ad Insertion) validation status.
    WHEN TO USE: Use when investigating suspected CTV app fraud, fake Roku/FireTV channel spoofing, or 24/7 background video loop schemes.
    """
)
def audit_ctv_telemetry(
    bundle_id: str,
    platform: str, # 'roku' | 'firetv' | 'appletv' | 'androidtv'
    lookback_days: int = 7
) -> dict: ...
```

### Tool 3: `query_bidstream_anomalies`
```python
@mcp.tool(
    name="query_bidstream_anomalies",
    description="""
    Executes high-speed DuckDB SQL scan over auction bidstream logs to detect programmatic auction manipulation.
    RETURNS: Top anomaly clusters (bid duplication rate, spoofed seller ID mismatch, suspicious IP CIDR blocks).
    WHEN TO USE: Use when the user requests investigation into sudden auction volume spikes or SSP bid laundering.
    """
)
def query_bidstream_anomalies(
    seller_id: str,
    anomaly_type: str, # 'bid_duplication' | 'ip_cluster' | 'geo_mismatch'
    min_confidence: float = 0.70
) -> dict: ...
```

### Tool 4: `verify_coppa_compliance`
```python
@mcp.tool(
    name="verify_coppa_compliance",
    description="""
    Audits a mobile or CTV app for compliance with COPPA (Children's Online Privacy Protection Act) and platform child safety rules.
    RETURNS: App age categorization, presence of persistent device identifiers (IDFA/AAID) transmitted to ad networks, and privacy policy validity score.
    WHEN TO USE: Use for UNICEF-style child privacy investigations or regulatory compliance audits.
    """
)
def verify_coppa_compliance(
    app_id: str,
    store: str # 'google_play' | 'apple_appstore' | 'roku_channel_store'
) -> dict: ...
```

---

## 4. Context Budgeting & Token FinOps Strategy

Large-scale telemetry queries can easily dump megabytes of raw JSON into an agent's context window, causing **Context Exhaustion, High Latency, and Hallucinations**.

AdStream MCP enforces a **Strict Context Budgeting Policy**:

| Stage | Raw Data Size | Filtered Context Window | Strategy |
| :--- | :--- | :--- | :--- |
| **Bidstream Scan** | 500,000 auction rows (~75 MB) | **450 tokens** | Pre-aggregate in DuckDB; return top 5 outlier clusters with standard deviations rather than raw records. |
| **IVT Breakdown** | 90 days of hourly rates (2,160 rows) | **300 tokens** | Compute summary metrics (mean GIVT, peak SIVT day, trend delta) + top 3 anomalous dates. |
| **Telemetry Audit** | 20 hardware sensor streams | **250 tokens** | Return normalized confidence scores (0.00 to 1.00) with diagnostic anomaly flags. |

### Context Defense Safeguard:
Every tool response enforces a hard token ceiling:
$$\text{Max Tool Output Tokens} \le 800 \text{ tokens}$$
If a response exceeds 800 tokens, it triggers automated server-side rollup summarization before returning to the LLM agent.
