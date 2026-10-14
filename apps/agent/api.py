"""
TrafficSentinel Suite — FastAPI REST Gateway
Provides HTTP endpoints for the Angular Dashboard:
- Interactive Investigator Chat & Clarification
- PromptEval Benchmark Runner & Comparative Regression Audit
- AdStream MCP Telemetry Data Feeds (DuckDB)
"""

import os
import sys
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MCP_SERVER_DIR = os.path.join(SUITE_ROOT, "apps", "mcp-server")
EVAL_STUDIO_DIR = os.path.join(SUITE_ROOT, "apps", "eval-studio")
for p in [SUITE_ROOT, MCP_SERVER_DIR, EVAL_STUDIO_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from packages.shared_types.models import (
    InvestigationRequest,
    InvestigationResponse,
    EvalSuiteSummary,
    ScenarioEvaluationResult
)
from apps.agent.engine.investigator import TrafficSentinelAgent
from harness.eval_engine import PromptEvalEngine
from regressions.reg_2026_ivt_04 import run_regression_comparison
from tools.telemetry_tools import (
    get_db_connection,
    execute_query_as_dicts,
    DATA_DIR
)

app = FastAPI(
    title="TrafficSentinel Suite API",
    description="REST Gateway for TrafficSentinel AI Agent, AdStream MCP, and PromptEval Studio",
    version="1.0.0"
)

# Enable CORS for Angular frontend (running on localhost:4200 or any port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# 1. Health & Meta Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "TrafficSentinel Suite",
        "version": "1.0.0",
        "agent": "TrafficSentinel AI (Claude 3.7)",
        "mcp": "AdStream FastMCP",
        "evals": "PromptEval Studio"
    }

# ---------------------------------------------------------------------------
# 2. Agent Interactive Investigation Endpoint
# ---------------------------------------------------------------------------
class InvestigatePayload(BaseModel):
    session_id: str = "default_session"
    query: str
    prompt_version: str = "v1.0"
    context_history: List[Dict[str, str]] = []

@app.post("/api/investigate", response_model=InvestigationResponse)
def investigate(payload: InvestigatePayload):
    agent = TrafficSentinelAgent(prompt_version=payload.prompt_version)
    req = InvestigationRequest(
        session_id=payload.session_id,
        query=payload.query,
        context_history=payload.context_history
    )
    return agent.execute(req)

# ---------------------------------------------------------------------------
# 3. PromptEval Studio Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/eval/scenarios")
def get_scenarios():
    engine = PromptEvalEngine()
    return engine.scenarios

class EvalRunPayload(BaseModel):
    prompt_version: str = "v1.0"

@app.post("/api/eval/run")
def run_evaluation(payload: EvalRunPayload):
    agent = TrafficSentinelAgent(prompt_version=payload.prompt_version)
    engine = PromptEvalEngine()
    summary, results = engine.run_suite(agent)
    return {
        "summary": summary,
        "results": results
    }

@app.get("/api/eval/compare")
def compare_regression():
    summary_golden, summary_regressed = run_regression_comparison()
    return {
        "golden_v1_0": summary_golden,
        "candidate_v1_1_regressed": summary_regressed,
        "delta": {
            "clarification_trigger_rate": round(summary_regressed.clarification_trigger_rate - summary_golden.clarification_trigger_rate, 2),
            "pass_rate": round(summary_regressed.pass_rate - summary_golden.pass_rate, 2),
            "tool_selection_accuracy": round(summary_regressed.tool_selection_accuracy - summary_golden.tool_selection_accuracy, 2)
        },
        "incident_id": "REG-2026-IVT-04",
        "root_cause": "Candidate prompt instructed model to 'infer missing details and guess parameters' rather than triggering interactive clarification on underspecified queries.",
        "ci_gate_action": "BLOCKED"
    }

# ---------------------------------------------------------------------------
# 4. AdStream MCP Telemetry Data Endpoints (DuckDB Parquet)
# ---------------------------------------------------------------------------
@app.get("/api/telemetry/publishers")
def get_publishers_telemetry(limit: int = 15):
    conn = get_db_connection()
    parquet_path = os.path.join(DATA_DIR, "publisher_ivt_daily.parquet").replace('\\', '/')
    query = f"""
        SELECT 
            publisher_id,
            arbitrary(domain) AS domain,
            sum(total_impressions) AS total_impressions,
            round(sum(givt_impressions)::DOUBLE / nullif(sum(total_impressions), 0), 4) AS givt_rate,
            round(sum(sivt_impressions)::DOUBLE / nullif(sum(total_impressions), 0), 4) AS sivt_rate,
            mode(top_sivt_category) AS top_sivt_category
        FROM '{parquet_path}'
        GROUP BY publisher_id
        ORDER BY sivt_rate DESC
        LIMIT ?
    """
    records = execute_query_as_dicts(conn, query, [limit])
    conn.close()
    return records

@app.get("/api/telemetry/ctv")
def get_ctv_telemetry():
    conn = get_db_connection()
    parquet_path = os.path.join(DATA_DIR, "ctv_app_telemetry.parquet").replace('\\', '/')
    query = f"SELECT * FROM '{parquet_path}'"
    records = execute_query_as_dicts(conn, query, [])
    conn.close()
    return records

@app.get("/api/telemetry/bidstream")
def get_bidstream_telemetry(limit: int = 20):
    conn = get_db_connection()
    parquet_path = os.path.join(DATA_DIR, "bidstream_anomalies.parquet").replace('\\', '/')
    query = f"SELECT * FROM '{parquet_path}' LIMIT ?"
    records = execute_query_as_dicts(conn, query, [limit])
    conn.close()
    return records

# ---------------------------------------------------------------------------
# 5. Mount Angular 21 Single Page Application
# ---------------------------------------------------------------------------
from starlette.staticfiles import StaticFiles

web_dist_dir = os.path.join(SUITE_ROOT, "apps", "web", "dist", "web", "browser")
if os.path.exists(web_dist_dir):
    app.mount("/", StaticFiles(directory=web_dist_dir, html=True), name="static-web")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
