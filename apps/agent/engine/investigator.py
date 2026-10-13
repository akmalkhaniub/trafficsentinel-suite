"""
TrafficSentinel AI — Master Investigator Agent
Coordinates AmbiguityGate, AntiInjectionGuard, AdStream MCP Tools, and Calibrated Confidence.
Codified according to SPEC-01, SPEC-02, and SPEC-05.
"""

import os
import sys
import re
from typing import Dict, Any, List, Optional

SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MCP_SERVER_DIR = os.path.join(SUITE_ROOT, "apps", "mcp-server")
if MCP_SERVER_DIR not in sys.path:
    sys.path.insert(0, MCP_SERVER_DIR)
if SUITE_ROOT not in sys.path:
    sys.path.insert(0, SUITE_ROOT)

from packages.shared_types.models import InvestigationRequest, InvestigationResponse, ClarificationPayload
from apps.agent.engine.ambiguity_gate import AmbiguityGate
from apps.agent.engine.anti_injection import AntiInjectionGuard
from tools.telemetry_tools import (
    inspect_publisher_ivt_tool,
    audit_ctv_telemetry_tool,
    query_bidstream_anomalies_tool,
    verify_coppa_compliance_tool,
)

class TrafficSentinelAgent:
    """Master Investigator Agent handling client requests with clarification and safety bounds."""

    def __init__(self, prompt_version: str = "v1.0"):
        self.prompt_version = prompt_version
        self.prompts_dir = os.path.join(SUITE_ROOT, "apps", "agent", "prompts")
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        prompt_filename = f"system_prompt_{self.prompt_version}.txt"
        prompt_path = os.path.join(self.prompts_dir, prompt_filename)
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "You are TrafficSentinel AI."

    def execute(self, request: InvestigationRequest) -> InvestigationResponse:
        query = request.query.strip()

        # -------------------------------------------------------------
        # 1. Anti-Injection Gate
        # -------------------------------------------------------------
        is_adversarial, flagged_patterns, sanitized_query = AntiInjectionGuard.sanitize_and_check(query)
        if is_adversarial:
            return InvestigationResponse(
                session_id=request.session_id,
                is_clarification=False,
                content="Investigation request rejected: Malicious or adversarial instruction pattern detected. System directives cannot be modified.",
                anti_injection_flags=flagged_patterns,
                calibrated_confidence="NORMAL",
                total_tokens_consumed=45
            )

        # -------------------------------------------------------------
        # 2. Interactive Clarification Gate (AmbiguityGate)
        # -------------------------------------------------------------
        # Note: If running on regressed prompt v1.1, the agent skips clarification and guesses!
        if "regressed" not in self.prompt_version.lower():
            clarification: ClarificationPayload = AmbiguityGate.evaluate(sanitized_query, request.context_history)
            if clarification.needs_clarification:
                options_text = ""
                if clarification.suggested_options:
                    options_text = "\n\nSuggested options:\n" + "\n".join(
                        f" - **{opt.label}**: {opt.description or ''}"
                        for opt in clarification.suggested_options
                    )
                content = (
                    f"**Clarification Required:** {clarification.primary_question}\n"
                    f"*(Missing parameters: {', '.join(clarification.missing_slots)})*{options_text}"
                )
                return InvestigationResponse(
                    session_id=request.session_id,
                    is_clarification=True,
                    content=content,
                    clarification_payload=clarification,
                    total_tokens_consumed=120
                )

        # -------------------------------------------------------------
        # 3. Request is Complete (or Regressed Agent Guessed) -> Execute Tools
        # -------------------------------------------------------------
        tools_called = []
        calibrated_confidence = "NORMAL"
        report_sections = []

        q_lower = sanitized_query.lower()

        # COPPA Check
        if "coppa" in q_lower or "kid" in q_lower or "child" in q_lower or "privacy" in q_lower:
            app_match = re.search(r'(com\.[a-z0-9_\.]+|tv\.[a-z0-9_\.]+)', q_lower)
            app_id = app_match.group(1) if app_match else "tv.appletv.kidsplay"
            tool_res = verify_coppa_compliance_tool(app_id, "apple_appstore")
            tools_called.append("verify_coppa_compliance")

            report_sections.append(
                f"### Child Privacy & COPPA Compliance Audit: {app_id}\n"
                f"- **Child Directed:** {tool_res['is_child_directed']}\n"
                f"- **Compliance Status:** {tool_res['compliance_status']}\n"
                f"- **Identifiers Shared:** {', '.join(tool_res['persistent_identifiers_shared']) or 'None'}\n"
                f"- **UNICEF Trust Risk Score:** {tool_res['unicef_trust_risk_score']}/100"
            )

        # CTV Telemetry
        elif any(k in q_lower for k in ["ctv", "streammaster", "cinemahub", "streamio", "roku", "firetv", "androidtv", "appletv", "screensaver"]):
            bundle_match = re.search(r'(com\.[a-z0-9_\.]+|tv\.[a-z0-9_\.]+)', q_lower)
            bundle_id = bundle_match.group(1) if bundle_match else "com.streammaster.roku"
            platform = "roku"
            for p in ["androidtv", "firetv", "appletv", "roku"]:
                if p in q_lower:
                    platform = p
                    break

            tool_res = audit_ctv_telemetry_tool(bundle_id, platform)
            tools_called.append("audit_ctv_telemetry")

            if tool_res.get("status") == "SUCCESS":
                screensaver = tool_res["screensaver_playback_ratio"]
                entropy = tool_res["user_agent_entropy_score"]
                confidence = tool_res["forensic_confidence"]

                report_sections.append(
                    f"### CTV Forensic Audit: {tool_res['app_name']} ({bundle_id}) on {platform.upper()}\n"
                    f"- **Screensaver Playback Ratio:** {screensaver*100:.1f}%\n"
                    f"- **User-Agent Entropy:** {entropy:.2f}\n"
                    f"- **SSAI Proxy Diversity:** {tool_res['ssai_server_ip_diversity']} IPs\n"
                    f"- **Forensic Confidence Score:** {confidence:.2f}"
                )

                if screensaver > 0.40 and entropy > 0.80:
                    calibrated_confidence = "CONFIRMED_HIGH_RISK"
                    report_sections.append(
                        "\n**Forensic Finding:** High-severity SIVT anomaly detected. The application exhibits "
                        "abnormal screensaver ad firing combined with high user-agent entropy consistent with automated device spoofing. "
                        "Recommendation: Exclude inventory from programmatic CTV buying flights pending manual review."
                    )
                else:
                    report_sections.append(
                        "\n**Forensic Finding:** Telemetry indicates normal baseline playback behavior. No deceptive loop patterns detected."
                    )

        # Publisher IVT
        elif any(k in q_lower for k in ["pub_", "publisher", "ivt", "sivt", "givt", "traffic"]):
            pub_match = re.search(r'(pub_[0-9]{4})', q_lower)
            pub_id = pub_match.group(1) if pub_match else "pub_0042"

            tool_res = inspect_publisher_ivt_tool(pub_id)
            tools_called.append("inspect_publisher_ivt")

            if tool_res.get("status") == "SUCCESS":
                sivt = tool_res["sivt_rate"]
                givt = tool_res["givt_rate"]
                tier = tool_res["risk_tier"]

                report_sections.append(
                    f"### Publisher IVT Audit: {pub_id} ({tool_res['domain']})\n"
                    f"- **Total Impressions:** {tool_res['total_impressions']:,}\n"
                    f"- **General IVT (GIVT):** {givt*100:.2f}%\n"
                    f"- **Sophisticated IVT (SIVT):** {sivt*100:.2f}%\n"
                    f"- **Top SIVT Signature:** {tool_res['top_sivt_category']}\n"
                    f"- **Risk Classification:** {tier}"
                )

                if tier in ["HIGH", "CRITICAL"]:
                    calibrated_confidence = "CONFIRMED_HIGH_RISK"
                    report_sections.append(
                        f"\n**Forensic Assessment:** Telemetry reveals elevated Sophisticated Invalid Traffic ({sivt*100:.2f}%), "
                        f"primarily driven by {tool_res['top_sivt_category']}. Inventory warrants review under MRC SIVT guidelines."
                    )
                else:
                    report_sections.append(
                        f"\n**Forensic Assessment:** Publisher traffic is within acceptable industry thresholds ({sivt*100:.2f}% SIVT). "
                        "No systematic fraud scheme identified."
                    )

        # Bidstream Anomalies
        else:
            seller_match = re.search(r'(seller_[0-9]{3})', q_lower)
            seller_id = seller_match.group(1) if seller_match else "seller_000"
            tool_res = query_bidstream_anomalies_tool(seller_id)
            tools_called.append("query_bidstream_anomalies")
            report_sections.append(
                f"### Bidstream Auction Anomaly Scan: {seller_id}\n"
                f"- **Status:** {tool_res['status']}\n"
                f"- **Clusters Detected:** {len(tool_res.get('anomaly_clusters', []))}"
            )

        # Non-Overstatement Guardrail check
        content = "\n\n".join(report_sections)
        for forbidden in ["guaranteed fraud", "undeniably malicious", "100% scam", "criminal scam"]:
            if forbidden in content.lower():
                content = content.replace(forbidden, "observed anomaly")

        return InvestigationResponse(
            session_id=request.session_id,
            is_clarification=False,
            content=content,
            tools_called=tools_called,
            calibrated_confidence=calibrated_confidence,
            total_tokens_consumed=350
        )
