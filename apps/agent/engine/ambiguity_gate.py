"""
TrafficSentinel AI — Interactive Ambiguity Gate & Clarification Engine
Prevents premature execution by identifying underspecified queries and generating focused multiple-choice clarifications.
Codified according to SPEC-02.
"""

import re
from typing import Dict, Any, List, Optional
import sys
import os

SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if SUITE_ROOT not in sys.path:
    sys.path.insert(0, SUITE_ROOT)

from packages.shared_types.models import ClarificationPayload, ClarificationOption

class AmbiguityGate:
    """Evaluates slot completeness for incoming investigation prompts."""

    KNOWN_PLATFORMS = ["roku", "firetv", "appletv", "androidtv"]
    KNOWN_STORES = ["google_play", "apple_appstore", "roku_channel_store"]

    @classmethod
    def evaluate(cls, query: str, context_history: Optional[List[Dict[str, str]]] = None) -> ClarificationPayload:
        q_lower = query.lower()

        # Combine with context history if available
        full_text = q_lower
        if context_history:
            for turn in context_history:
                full_text += " " + turn.get("content", "").lower()

        # -------------------------------------------------------------
        # 1. Child Privacy & COPPA Inquiries
        # -------------------------------------------------------------
        if any(w in full_text for w in ["coppa", "kid", "child", "privacy"]):
            app_match = re.search(r'(com\.[a-z0-9_\.]+|tv\.[a-z0-9_\.]+)', full_text)
            has_store = any(s in full_text for s in ["app store", "google play", "store", "ios", "android"])
            if app_match and (app_match.group(1).startswith("tv.appletv") or app_match.group(1).startswith("com.android")):
                has_store = True

            missing_slots = []
            if not app_match:
                missing_slots.append("app_id_or_bundle")
            if not has_store:
                missing_slots.append("app_store_platform")

            if missing_slots:
                return ClarificationPayload(
                    needs_clarification=True,
                    completeness_score=0.40,
                    missing_slots=missing_slots,
                    primary_question="Which application bundle and app store should I audit for child privacy & COPPA compliance?",
                    suggested_options=[
                        ClarificationOption(id="opt_kidsplay", label="tv.appletv.kidsplay (Apple App Store)", description="Audit child-directed CTV learning app"),
                        ClarificationOption(id="opt_android_kid", label="com.androidtv.streamio.2 (Google Play)", description="Audit mobile/CTV player ad tags")
                    ]
                )

        # -------------------------------------------------------------
        # 2. CTV App Forensic Inquiries
        # -------------------------------------------------------------
        if any(w in full_text for w in ["ctv", "streammaster", "cinemahub", "streamio", "channel", "smart tv", "screensaver", "entropy", "loop", "video"]):
            detected_platform = next((p for p in cls.KNOWN_PLATFORMS if p in full_text), None)
            bundle_match = re.search(r'(com\.[a-z0-9_\.]+|tv\.[a-z0-9_\.]+)', full_text)

            missing_slots = []
            if not detected_platform:
                missing_slots.append("platform")
            if not bundle_match and not any(name in full_text for name in ["streammaster", "cinemahub", "streamio", "kidsplay"]):
                missing_slots.append("bundle_id_or_app_name")

            if missing_slots:
                options = [
                    ClarificationOption(id="opt_roku", label="Roku Channel (e.g., com.streammaster.roku)", description="Audit screensaver loop & SSAI proxy diversity"),
                    ClarificationOption(id="opt_firetv", label="Amazon FireTV (e.g., com.firetv.cinemahub)", description="Audit hardware UA entropy & background playback"),
                    ClarificationOption(id="opt_androidtv", label="AndroidTV (e.g., com.androidtv.streamio.0)", description="Audit device header consistency")
                ]
                return ClarificationPayload(
                    needs_clarification=True,
                    completeness_score=0.40,
                    missing_slots=missing_slots,
                    primary_question="Which Connected TV (CTV) platform and application bundle should I investigate?",
                    suggested_options=options
                )

        # -------------------------------------------------------------
        # 3. Bidstream Anomaly & RTB Inquiries
        # -------------------------------------------------------------
        if any(w in full_text for w in ["bid", "rtb", "auction", "seller", "duplication"]):
            seller_match = re.search(r'(seller_[0-9]{3})', full_text)
            if not seller_match:
                return ClarificationPayload(
                    needs_clarification=True,
                    completeness_score=0.35,
                    missing_slots=["seller_id"],
                    primary_question="Which SSP seller ID should I scan for bid duplication and RTB auction anomalies?",
                    suggested_options=[
                        ClarificationOption(id="opt_seller_000", label="seller_000", description="Scan for auction duplication clusters"),
                        ClarificationOption(id="opt_seller_001", label="seller_001", description="Scan for suspicious IP CIDR flooding")
                    ]
                )

        # -------------------------------------------------------------
        # 4. Publisher IVT Inquiries
        # -------------------------------------------------------------
        if any(w in full_text for w in ["publisher", "ivt", "traffic", "sivt", "givt", "domain", "supply chain"]):
            pub_match = re.search(r'(pub_[0-9]{4}|[a-z0-9\-]+\.(?:com|net|org))', full_text)
            has_timeframe = any(t in full_text for t in ["day", "week", "month", "september", "q3", "historical", "recent", "quarter"])

            missing_slots = []
            if not pub_match:
                missing_slots.append("publisher_id_or_domain")
            if not has_timeframe:
                missing_slots.append("timeframe")

            if "publisher_id_or_domain" in missing_slots:
                options = [
                    ClarificationOption(id="opt_pub_0042", label="Publisher pub_0042 (stream-bad-actor.net)", description="Known elevated SIVT domain"),
                    ClarificationOption(id="opt_pub_0001", label="Publisher pub_0001 (premium-publisher-1.com)", description="High-volume premium inventory"),
                    ClarificationOption(id="opt_pub_0088", label="Publisher pub_0088 (ad-laundering-media.com)", description="Critical session hijacking suspect")
                ]
                return ClarificationPayload(
                    needs_clarification=True,
                    completeness_score=0.30,
                    missing_slots=missing_slots,
                    primary_question="Which specific publisher ID or domain would you like me to audit for Invalid Traffic (IVT)?",
                    suggested_options=options
                )

        # -------------------------------------------------------------
        # 5. Vague / Ultra-Short Inquiries (e.g., "Audit for fraud", "Supply chain")
        # -------------------------------------------------------------
        if len(query.strip().split()) <= 4 and not re.search(r'(pub_[0-9]{4}|com\.[a-z0-9\._]+|seller_[0-9]{3})', full_text):
            return ClarificationPayload(
                needs_clarification=True,
                completeness_score=0.15,
                missing_slots=["target_entity", "investigation_type"],
                primary_question="Could you clarify the target of your investigation? What entity and fraud category should I inspect?",
                suggested_options=[
                    ClarificationOption(id="opt_pub", label="Programmatic Publisher IVT Audit", description="GIVT vs. SIVT breakdown on web/app inventory"),
                    ClarificationOption(id="opt_ctv", label="Connected TV (CTV) App Forensics", description="Screensaver playback & device spoofing"),
                    ClarificationOption(id="opt_bid", label="Bidstream Anomaly Scan", description="RTB auction duplication & IP cluster abuse"),
                    ClarificationOption(id="opt_coppa", label="COPPA Child Safety Audit", description="Persistent ID tracking on kids apps")
                ]
            )

        # -------------------------------------------------------------
        # Request is Complete
        # -------------------------------------------------------------
        return ClarificationPayload(
            needs_clarification=False,
            completeness_score=1.0,
            missing_slots=[],
            primary_question=""
        )
