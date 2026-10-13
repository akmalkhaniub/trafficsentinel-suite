---
name: coppa-audit
description: Regulatory compliance playbook for evaluating mobile and CTV applications against the Children's Online Privacy Protection Act (COPPA) and UNICEF Child Safety benchmarks.
---

# COPPA & Child Privacy Audit Skill

## Overview
Under COPPA and global regulatory frameworks, apps directed at children under 13 cannot transmit persistent personal identifiers (IDFA, GAID, MAC addresses, IP addresses) to ad networks without verifiable parental consent.

## Critical Compliance Violations
1. **Unlawful Identifier Transmission**:
   - Sharing IDFA/GAID in bid requests for child-directed apps.
2. **Missing / Deceptive Privacy Policy**:
   - Absence of COPPA-compliant privacy policy explicitly disclosing ad tracking practices.
3. **High UNICEF Risk Score**:
   - Risk score > 75.0 indicates significant regulatory exposure and deceptive data practices.

## Investigation Procedure
1. Confirm `app_id` and `store` (Google Play, Apple App Store, Roku Channel Store).
2. Invoke `verify_coppa_compliance(app_id=..., store=...)`.
3. Check `is_child_directed` and `persistent_identifiers_shared`.
4. If non-compliant, recommend immediate ad-tag pausing and referral to legal compliance.
