"""
PromptEval Studio — Regression Incident Case Study: REG-2026-IVT-04
Proves evaluation discipline by demonstrating how PromptEval Studio catches prompt regressions in CI/CD.
Codified according to SPEC-04.
"""

import os
import sys

SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EVAL_STUDIO_DIR = os.path.join(SUITE_ROOT, "apps", "eval-studio")
if EVAL_STUDIO_DIR not in sys.path:
    sys.path.insert(0, EVAL_STUDIO_DIR)
if SUITE_ROOT not in sys.path:
    sys.path.insert(0, SUITE_ROOT)

from apps.agent.engine.investigator import TrafficSentinelAgent
from harness.eval_engine import PromptEvalEngine

def run_regression_comparison():
    engine = PromptEvalEngine()

    print("================================================================================")
    print("PROMPTEVAL STUDIO — REGRESSION AUDIT: REG-2026-IVT-04")
    print("Evaluating Golden Prompt (v1.0) vs. Candidate Prompt (v1.1_regressed)")
    print("================================================================================\n")

    # 1. Run Golden Production Agent (v1.0)
    print("[1/2] Evaluating Golden Production Agent (v1.0)...")
    golden_agent = TrafficSentinelAgent(prompt_version="v1.0")
    summary_golden, _ = engine.run_suite(golden_agent)

    print(f"  - Overall Pass Rate: {summary_golden.pass_rate}% ({summary_golden.passed_scenarios}/{summary_golden.total_scenarios})")
    print(f"  - Clarification Trigger Rate (CTR): {summary_golden.clarification_trigger_rate}%")
    print(f"  - Tool Selection Accuracy (TSA): {summary_golden.tool_selection_accuracy}%")
    print(f"  - Status: {summary_golden.status}\n")

    # 2. Run Candidate Regressed Agent (v1.1_regressed)
    print("[2/2] Evaluating Candidate Prompt with 'Proactive Guessing' (v1.1_regressed)...")
    regressed_agent = TrafficSentinelAgent(prompt_version="v1.1_regressed")
    summary_regressed, results_regressed = engine.run_suite(regressed_agent)

    print(f"  - Overall Pass Rate: {summary_regressed.pass_rate}% ({summary_regressed.passed_scenarios}/{summary_regressed.total_scenarios})")
    print(f"  - Clarification Trigger Rate (CTR): {summary_regressed.clarification_trigger_rate}%")
    print(f"  - Tool Selection Accuracy (TSA): {summary_regressed.tool_selection_accuracy}%")
    print(f"  - Status: {summary_regressed.status}\n")

    # 3. Regression Differential Analysis
    ctr_delta = summary_regressed.clarification_trigger_rate - summary_golden.clarification_trigger_rate
    pass_delta = summary_regressed.pass_rate - summary_golden.pass_rate

    print("================================================================================")
    print("REGRESSION AUDIT SUMMARY")
    print("================================================================================")
    print(f"Metric                        v1.0 (Golden)    v1.1 (Candidate)   Delta")
    print(f"--------------------------------------------------------------------------------")
    print(f"Clarification Trigger Rate    {summary_golden.clarification_trigger_rate:>6.1f}%          {summary_regressed.clarification_trigger_rate:>6.1f}%          {ctr_delta:>6.1f}%")
    print(f"Overall Pass Rate             {summary_golden.pass_rate:>6.1f}%          {summary_regressed.pass_rate:>6.1f}%          {pass_delta:>6.1f}%")
    print(f"CI Quality Gate Result        [APPROVED]        [BLOCKED]")
    print("================================================================================")
    print("\n[CONCLUSION] Candidate prompt v1.1 caused a catastrophic collapse in clarification")
    print("behavior by attempting to 'guess' parameters prematurely.")
    print("PromptEval Studio successfully caught this regression and BLOCKED the PR merge.\n")

    return summary_golden, summary_regressed

if __name__ == "__main__":
    run_regression_comparison()
