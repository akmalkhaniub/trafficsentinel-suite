"""
PromptEval Studio — CLI Benchmark Runner
Command-line interface to execute evaluations, generate Markdown reports, and enforce CI quality gates.
"""

import os
import sys
import argparse

SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVAL_STUDIO_DIR = os.path.join(SUITE_ROOT, "apps", "eval-studio")
if EVAL_STUDIO_DIR not in sys.path:
    sys.path.insert(0, EVAL_STUDIO_DIR)
if SUITE_ROOT not in sys.path:
    sys.path.insert(0, SUITE_ROOT)

from apps.agent.engine.investigator import TrafficSentinelAgent
from harness.eval_engine import PromptEvalEngine
from regressions.reg_2026_ivt_04 import run_regression_comparison

def main():
    parser = argparse.ArgumentParser(description="PromptEval Studio CLI")
    parser.add_argument("--version", default="v1.0", help="Prompt version to evaluate (v1.0, v1.1_regressed)")
    parser.add_argument("--compare", action="store_true", help="Run comparative regression audit (v1.0 vs v1.1)")
    args = parser.parse_args()

    if args.compare:
        run_regression_comparison()
        return

    print("================================================================================")
    print(f"PROMPTEVAL STUDIO — BENCHMARK RUN: {args.version}")
    print("================================================================================")

    agent = TrafficSentinelAgent(prompt_version=args.version)
    engine = PromptEvalEngine()
    summary, results = engine.run_suite(agent)

    print(f"Total Scenarios Evaluated: {summary.total_scenarios}")
    print(f"Passed Scenarios:          {summary.passed_scenarios}/{summary.total_scenarios} ({summary.pass_rate}%)")
    print(f"Clarification Precision:   {summary.clarification_trigger_rate}% (Target: >=95%)")
    print(f"Tool Selection Accuracy:   {summary.tool_selection_accuracy}% (Target: >=95%)")
    print(f"Non-Overstatement Score:   {summary.calibrated_confidence_rate}% (Target: 100%)")
    print(f"Anti-Injection Defense:    {summary.injection_defense_rate}% (Target: 100%)")
    print(f"Average Scenario Latency:  {summary.average_latency_ms:.2f} ms")
    print(f"Overall Quality Gate:      [{summary.status}]")
    print("================================================================================")

    if summary.status != "PASS":
        print("\n[!] CI Quality Gate Failed. Regressions detected.")
        sys.exit(1)
    else:
        print("\n[OK] All CI Quality Gates Passed. Prompt approved for production deployment.")

if __name__ == "__main__":
    main()
