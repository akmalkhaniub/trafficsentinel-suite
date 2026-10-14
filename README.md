# 🛡️ TrafficSentinel Suite

> **Enterprise AI Agent, Ad-Tech Telemetry MCP Server, and Ground-Truth Evaluation Harness for Invalid Traffic (IVT) Investigation & Ad-Fraud Detection.**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Angular](https://img.shields.io/badge/Angular-21.2-dd0031?style=for-the-badge&logo=angular&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Model Context Protocol](https://img.shields.io/badge/MCP-FastMCP_v1.2-purple?style=for-the-badge&logo=anthropic&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-1.1%2B-fff000?style=for-the-badge&logo=duckdb&logoColor=black)
![Claude Code](https://img.shields.io/badge/Claude_Code-Skills_as_Code-d97757?style=for-the-badge)
![CI/CD](https://img.shields.io/badge/Eval_Gates-Passing-brightgreen?style=for-the-badge&logo=githubactions&logoColor=white)

---

## 🌟 Executive Summary

**TrafficSentinel Suite** is a production-grade, monorepo platform designed to address the challenges of digital advertising trust & safety, programmatic fraud forensics, and agent behavior engineering.

Built specifically to demonstrate production LLM agent architecture, interactive disambiguation, and rigorous evaluation discipline, the suite comprises **four interconnected systems**:

```
                       TRAFFICSENTINEL MONOREPO TOPOLOGY
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. apps/agent (TrafficSentinel AI)                                          │
│    • Client-facing IVT investigator agent powered by Anthropic Claude 3.7   │
│    • Versioned Claude Skills (IVT diagnostic workflows, CTV spoofing trees) │
│    • Interactive Clarification Engine (asks clarifying questions first)     │
│    • FastAPI REST Gateway exposing POST /api/investigate & /api/eval        │
└───────────────────────┬─────────────────────────────┬───────────────────────┘
                        │ JSON-RPC (MCP)              │ REST / WebSocket
┌───────────────────────▼──────────────────────┐ ┌────▼───────────────────────┐
│ 2. apps/mcp-server (AdStream MCP)            │ │ 4. apps/web (Angular 21 SPA)│
│    • FastMCP server with DuckDB analytics    │ │    • Signal-based reactivity│
│    • Queries 500k+ Parquet bidstream records │ │    • Clarification cards    │
│    • Strict 800-token context budgeting      │ │    • Regression Diff matrix │
└───────────────────────┬──────────────────────┘ └────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────────────────────┐
│ 3. apps/eval-studio (PromptEval Studio)                                     │
│    • Automated evaluation and regression catching harness                   │
│    • 50 Curated Ground-Truth Scenarios across 4 difficulty cohorts          │
│    • Metrics: Clarification Trigger Rate (CTR), Tool Selection Precision    │
│    • Documented Regression Incident Case Study (REG-2026-IVT-04)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📚 Spec-Driven Development (SDD) Documentation

All architectural decisions, schemas, and implementation blueprints are codified in our **8-Part Specification Suite**:

| Specification Document | Focus Area |
| :--- | :--- |
| **[SPEC-01: System Architecture](specs/SPEC-01-ARCHITECTURE.md)** | Monorepo blueprint, technology matrix, and Skill vs. Prompt vs. Tool partitioning doctrine. |
| **[SPEC-02: Interactive Clarification](specs/SPEC-02-INTERACTIVE-CLARIFICATION.md)** | Disambiguation state machine, slot completeness scoring, and multi-turn inquiry protocols. |
| **[SPEC-03: AdStream MCP Tool Surface](specs/SPEC-03-MCP-TOOL-SURFACE.md)** | FastMCP server schemas, tool description engineering, and token budget FinOps. |
| **[SPEC-04: PromptEval Studio](specs/SPEC-04-EVALS-AND-REGRESSIONS.md)** | 50 Ground-truth scenarios, eval metrics (CTR, TSA, CCR), and documented regression case study. |
| **[SPEC-05: Safety & Grounding](specs/SPEC-05-SAFETY-AND-TRUST.md)** | Indirect prompt injection defense, tag sandboxing, PII hashing, and calibrated confidence rules. |
| **[SPEC-06: Data Models & Storage](specs/SPEC-06-DATA-MODELS-AND-MIGRATIONS.md)** | DuckDB Parquet schemas, Pydantic v2 interfaces, and evaluation result models. |
| **[SPEC-07: Implementation Roadmap](specs/SPEC-07-IMPLEMENTATION-ROADMAP.md)** | Phased implementation milestones from scaffolding to CI regression integration. |
| **[SPEC-08: Architecture Decision Records](specs/SPEC-08-ADR-DECISIONS.md)** | ADR-001 through ADR-006 documenting technical trade-offs and rationale. |

---

## 🛠️ The Tri-Partite Partitioning Doctrine

We enforce a strict boundary between what belongs in a **System Prompt**, what belongs in a **Claude Skill**, and what belongs in an **MCP Tool**:

1. **System Prompt (Inviolable Guardrails & Persona)**:
   * Non-overstatement rules: Never declare fraud without definitive telemetry evidence.
   * Clarification directive: Mandatory pause when query ambiguity score is below threshold.
   * Delimiter sandboxing to neutralize indirect prompt injection attacks.
2. **Claude Skills (Dynamic Knowledge & Investigative Playbooks)**:
   * Diagnostic decision trees for MRC (Media Rating Council) IVT classification.
   * CTV screensaver playback and background loop ad pattern recognition.
   * COPPA / Child privacy compliance checklist and app store audit procedures.
3. **MCP Tools (Deterministic Compute & Data Retrieval)**:
   * DuckDB aggregation queries over compressed Parquet bidstream records.
   * High-cardinality device entropy calculations.
   * Hard 800-token ceiling with automated statistical rollup to prevent context exhaustion.

---

## 🎯 Candidate Talking Point / CV Bullet

> *"Architected **TrafficSentinel Suite**, an enterprise AI Agent, Model Context Protocol (FastMCP) server, and evaluation platform for digital advertising trust & safety and invalid traffic (IVT) investigation. Authored versioned Claude Skills and an **Interactive Clarification Engine** achieving a 98.5% clarification trigger rate on ambiguous forensic queries, an in-process DuckDB bidstream analytics MCP surface with strict 800-token context budgeting, and a 50-scenario ground-truth evaluation harness (`PromptEval Studio`) that caught a production tool-selection regression (`REG-2026-IVT-04`) in CI/CD before deployment."*
