"""
Unit Tests for TrafficSentinel Suite FastAPI REST Gateway
Verifies endpoints for investigation, evals, regression comparisons, and DuckDB telemetry feeds.
"""

import os
import sys
import pytest
from starlette.testclient import TestClient

SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SUITE_ROOT not in sys.path:
    sys.path.insert(0, SUITE_ROOT)

from apps.agent.api import app

client = TestClient(app)

def test_api_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "HEALTHY"

def test_api_investigate_clarification():
    payload = {
        "session_id": "test_api_sess",
        "query": "Check if StreamMaster app is committing fraud",
        "prompt_version": "v1.0"
    }
    resp = client.post("/api/investigate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_clarification"] is True
    assert data["clarification_payload"] is not None

def test_api_investigate_complete():
    payload = {
        "session_id": "test_api_sess_2",
        "query": "Audit Roku channel com.streammaster.roku over the past 7 days",
        "prompt_version": "v1.0"
    }
    resp = client.post("/api/investigate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_clarification"] is False
    assert "audit_ctv_telemetry" in data["tools_called"]

def test_api_eval_compare():
    resp = client.get("/api/eval/compare")
    assert resp.status_code == 200
    data = resp.json()
    assert data["incident_id"] == "REG-2026-IVT-04"
    assert data["ci_gate_action"] == "BLOCKED"
    assert data["delta"]["clarification_trigger_rate"] == -100.0

def test_api_telemetry_publishers():
    resp = client.get("/api/telemetry/publishers?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert "publisher_id" in data[0]
