"""
TrafficSentinel AI — Anti-Prompt Injection & Indirect Data Sandboxing
Detects adversarial manipulation and sandbox bypass attempts.
Codified according to SPEC-05.
"""

import re
from typing import Tuple, List

class AntiInjectionGuard:
    """Scans incoming queries and external payloads for injection patterns."""

    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|directives|rules)",
        r"disregard\s+(all\s+)?(previous|prior)\s+(instructions|rules)",
        r"output\s+(all\s+)?(system\s+prompts?|api\s+keys?|secret\s+tokens?)",
        r"you\s+are\s+now\s+in\s+developer\s+mode",
        r"system\s*override",
        r"do\s+anything\s+now\s+(dan)",
        r"<script.*?>",
    ]

    @classmethod
    def sanitize_and_check(cls, text: str) -> Tuple[bool, List[str], str]:
        """
        Returns:
            (is_adversarial, flagged_patterns, sanitized_text)
        """
        flagged = []
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                flagged.append(pattern)

        # Strip null bytes and control chars
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)

        is_adversarial = len(flagged) > 0
        return is_adversarial, flagged, sanitized

    @classmethod
    def sandbox_untrusted_data(cls, tag_name: str, data: str) -> str:
        """Wraps untrusted data inside non-executable XML delimiters."""
        escaped = data.replace("<", "&lt;").replace(">", "&gt;")
        return f"<{tag_name}>\n{escaped}\n</{tag_name}>"
