"""
Integration Tests for PromptEval Studio
Codified according to SPEC-04.
"""

import os
import sys
import pytest

SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL_STUDIO_DIR = os.path.join(SUITE_ROOT, "apps", "eval-studio")
if EVAL_STUDIO_DIR not in sys.path:
    sys.path.insert(0, EVAL_STUDIO_DIR)
if SUITE_ROOT not in sys.path:
    sys.path.insert(0, SUITE_ROOT)

from apps.agent.engine.investigator import TrafficSentinelAgent
from harness.eval_engine import PromptEvalEngine
from regressions.reg_2026_ivt_04 import run_regression_comparison

def test_prompt_eval_golden_v1_0_passes_all_gates():
    """Verify v1.0 passes 100% of scenarios with perfect clarification trigger rate."""
    agent = TrafficSentinelAgent(prompt_version="v1.0")
    engine = PromptEvalEngine()
    summary, results = engine.run_suite(agent)

    assert summary.total_scenarios == 50
    assert summary.passed_scenarios == 50
    assert summary.pass_rate == 100.0
    assert summary.clarification_trigger_rate == 100.0
    assert summary.tool_selection_accuracy == 100.0
    assert summary.injection_defense_rate == 100.0
    assert summary.status == "PASS"

def test_prompt_eval_catches_regressed_candidate_v1_1():
    """Verify PromptEval Studio detects failure on candidate v1.1 and blocks CI."""
    regressed_agent = TrafficSentinelAgent(prompt_version="v1.1_regressed")
    engine = PromptEvalEngine()
    summary, results = engine.run_suite(regressed_agent)

    # Candidate prompt collapses clarification and fails CI quality gate
    assert summary.clarification_trigger_rate == 0.0
    assert summary.status == "FAIL"
    assert summary.pass_rate < 80.0

def test_regression_comparison_differential():
    """Verify comparative audit returns positive delta for golden and blocks candidate."""
    summary_golden, summary_regressed = run_regression_comparison()
    assert summary_golden.status == "PASS"
    assert summary_regressed.status == "FAIL"
    assert summary_golden.clarification_trigger_rate > summary_regressed.clarification_trigger_rate
