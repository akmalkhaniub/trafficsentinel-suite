---
name: ivt-investigation
description: Forensic playbook for analyzing programmatic Invalid Traffic (IVT), distinguishing General IVT (GIVT) from Sophisticated IVT (SIVT) according to MRC guidelines.
---

# IVT Investigation Skill

## Overview
This skill guides the agent in conducting structured forensic investigations into programmatic ad inventory.

## Classification Standards (Media Rating Council - MRC)
1. **General Invalid Traffic (GIVT)**:
   - Routine, non-malicious or easily detected automated traffic.
   - Known search engine web crawlers, data center proxy egress, routine health checks.
   - Metric threshold: GIVT < 2.0% is industry standard across web and in-app display.
2. **Sophisticated Invalid Traffic (SIVT)**:
   - Malicious, deceptive traffic designed to evade detection.
   - Hidden WebViews, hijacked user sessions, impression laundering, auto-refreshing background tabs.
   - Metric threshold:
     - SIVT < 4.0%: Clean / Normal baseline.
     - SIVT 4.0% - 15.0%: Elevated / Requires continuous monitoring.
     - SIVT > 15.0%: High risk of fraudulent ad laundering.

## Standard Investigation Procedure
1. Verify that the user has specified a `publisher_id` or domain. If ambiguous, trigger `AmbiguityGate`.
2. Call `inspect_publisher_ivt(publisher_id=...)` via AdStream MCP.
3. Compare GIVT vs. SIVT ratios.
4. Report findings with calibrated epistemic confidence:
   - Always state exact percentage metrics and primary SIVT category.
   - Never use emotional or non-forensic language ("scam", "thief", "guaranteed fraud").
