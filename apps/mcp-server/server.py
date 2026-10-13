"""
AdStream MCP Server — Production FastMCP Entrypoint
Exposes ad-tech telemetry, IVT forensics, and COPPA auditing tools via Model Context Protocol.
"""

import os
import sys
from typing import Optional

# Ensure local tools module is on path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from tools.telemetry_tools import (
    inspect_publisher_ivt_tool,
    audit_ctv_telemetry_tool,
    query_bidstream_anomalies_tool,
    verify_coppa_compliance_tool,
)
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP(
    name="AdStream-MCP",
    instructions="""
    AdStream MCP provides programmatic ad-tech telemetry, invalid traffic (IVT) metrics,
    CTV application forensics, and child safety compliance auditing.
    Always pass exact bundle IDs and platform names when calling tools.
    """
)

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
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    breakdown: Optional[str] = "summary"
) -> dict:
    return inspect_publisher_ivt_tool(publisher_id, start_date, end_date, breakdown)


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
    platform: str,
    lookback_days: int = 7
) -> dict:
    return audit_ctv_telemetry_tool(bundle_id, platform, lookback_days)


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
    anomaly_type: Optional[str] = None,
    min_confidence: float = 0.70
) -> dict:
    return query_bidstream_anomalies_tool(seller_id, anomaly_type, min_confidence)


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
    store: str
) -> dict:
    return verify_coppa_compliance_tool(app_id, store)


if __name__ == "__main__":
    mcp.run()
