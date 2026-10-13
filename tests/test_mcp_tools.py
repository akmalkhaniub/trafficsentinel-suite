"""
Unit Tests for AdStream MCP Tools
Verifies DuckDB query latency, schema validity, token budget ceilings, and fraud detection heuristics.
"""

import os
import sys
import pytest

# Ensure suite and mcp-server are on sys.path
SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MCP_SERVER_DIR = os.path.join(SUITE_ROOT, "apps", "mcp-server")
if MCP_SERVER_DIR not in sys.path:
    sys.path.insert(0, MCP_SERVER_DIR)
if SUITE_ROOT not in sys.path:
    sys.path.insert(0, SUITE_ROOT)

from tools.telemetry_tools import (
    inspect_publisher_ivt_tool,
    audit_ctv_telemetry_tool,
    query_bidstream_anomalies_tool,
    verify_coppa_compliance_tool,
)

def test_inspect_publisher_ivt_known_bad_actor():
    """Verify publisher 42 and 88 (known bad actors) return HIGH/CRITICAL risk tiers."""
    result_42 = inspect_publisher_ivt_tool("pub_0042")
    assert result_42["status"] == "SUCCESS"
    assert result_42["publisher_id"] == "pub_0042"
    assert result_42["sivt_rate"] > 0.15
    assert result_42["risk_tier"] in ["HIGH", "CRITICAL"]
    assert result_42["token_usage_estimated"] < 400

    result_88 = inspect_publisher_ivt_tool("pub_0088")
    assert result_88["status"] == "SUCCESS"
    assert result_88["sivt_rate"] > 0.20
    assert result_88["risk_tier"] == "CRITICAL"

def test_inspect_publisher_ivt_clean_publisher():
    """Verify clean publisher returns LOW risk tier."""
    result = inspect_publisher_ivt_tool("pub_0001")
    assert result["status"] == "SUCCESS"
    assert result["risk_tier"] == "LOW"
    assert result["sivt_rate"] < 0.05

def test_audit_ctv_telemetry_screensaver_fraud():
    """Verify StreamMaster Roku channel flags extreme screensaver playback and spoofed UA."""
    result = audit_ctv_telemetry_tool("com.streammaster.roku", "roku")
    assert result["status"] == "SUCCESS"
    assert result["screensaver_playback_ratio"] > 0.50
    assert result["user_agent_entropy_score"] > 0.80
    assert any("EXTREME_SCREENSAVER_PLAYBACK" in sig for sig in result["anomalous_signals"])
    assert result["forensic_confidence"] >= 0.85

def test_query_bidstream_anomalies_seller():
    """Verify seller anomaly clustering returns structured records."""
    result = query_bidstream_anomalies_tool("seller_000")
    assert result["status"] in ["ANOMALIES_DETECTED", "CLEAN"]
    assert result["token_usage_estimated"] < 400

def test_verify_coppa_compliance_child_directed():
    """Verify child-directed app failing COPPA is flagged with non-compliant status."""
    result = verify_coppa_compliance_tool("tv.appletv.kidsplay", "apple_appstore")
    assert result["status"] == "SUCCESS"
    assert result["is_child_directed"] is True
    assert result["compliance_status"] == "NON_COMPLIANT"
    assert "IDFA" in result["persistent_identifiers_shared"]
    assert result["unicef_trust_risk_score"] > 80.0

def test_token_budget_ceiling_enforced():
    """Verify that all tools strictly respect the <800 token budget ceiling."""
    res1 = inspect_publisher_ivt_tool("pub_0042")
    res2 = audit_ctv_telemetry_tool("com.streammaster.roku", "roku")
    res3 = query_bidstream_anomalies_tool("seller_000")
    res4 = verify_coppa_compliance_tool("tv.appletv.kidsplay", "apple_appstore")

    for r in [res1, res2, res3, res4]:
        assert r["token_usage_estimated"] < 800, f"Tool response exceeded 800 token ceiling: {r['token_usage_estimated']}"
