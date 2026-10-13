---
name: ctv-spoofing
description: Forensic playbook for detecting Connected TV (CTV) application spoofing, screensaver impression laundering, and Server-Side Ad Insertion (SSAI) proxy fraud.
---

# Connected TV (CTV) Spoofing Skill

## Overview
Connected TV advertising commands high CPMs ($20 - $50+), making it the primary target for organized ad-fraud rings.

## Primary CTV Fraud Vectors
1. **Screensaver / Standby Playback**:
   - The CTV app continues fetching and playing video ads 24/7 even after the consumer turns off the television display.
   - Anomaly indicator: `screensaver_playback_ratio > 0.35` (35%+ of impressions occurring during screen standby).
2. **Device Hardware Spoofing**:
   - Mobile phones or cloud Linux instances emitting fake user-agent strings masquerading as Roku, Apple TV, or FireTV hardware.
   - Anomaly indicator: `user_agent_entropy_score > 0.75` (high variance in hardware parameters).
3. **SSAI Proxy Concentration**:
   - Legitimate SSAI routes through diverse edge servers. Fraud rings route fake traffic through a handful of data-center proxies.
   - Anomaly indicator: `ssai_server_ip_diversity < 10` for high-volume apps.

## Investigation Procedure
1. Verify `bundle_id` and `platform` (Roku, FireTV, Apple TV, Android TV). If missing, ask for platform clarification.
2. Invoke `audit_ctv_telemetry(bundle_id=..., platform=...)`.
3. Check for the three critical anomaly flags above.
4. If multiple indicators match, report confirmed SIVT signature with specific forensic numbers.
