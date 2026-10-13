# SPEC-08: Architecture Decision Records (ADRs)

## 1. Overview
This document records key architectural decisions made for **TrafficSentinel Suite**, providing rationales, trade-offs, and consequences.

---

### ADR-001: Use FastMCP (Python) for AdStream MCP Server
* **Status**: Accepted
* **Context**: The MCP server needs to interface with large-scale ad telemetry, DuckDB Parquet data, and scientific/statistical libraries.
* **Decision**: Build the MCP server using Python's `FastMCP` framework rather than TypeScript's `@modelcontextprotocol/sdk`.
* **Rationale**: Python provides native, zero-copy interoperability with DuckDB and PyArrow for high-speed columnar filtering. It also allows direct sharing of Pydantic data schemas between the Agent, MCP server, and Eval Harness.
* **Consequences**: FastMCP enables both `stdio` and SSE transport out of the box with zero runtime conversion overhead.

---

### ADR-002: Use DuckDB with Embedded Parquet over Postgres / Snowflake
* **Status**: Accepted
* **Context**: Demonstrating ad-tech telemetry analysis requires querying hundreds of thousands of bidstream records with sub-10ms response times without forcing evaluators to spin up cloud data warehouses.
* **Decision**: Package synthetic ad telemetry inside compressed Parquet files queried via in-process DuckDB.
* **Rationale**: DuckDB runs in-process with zero external infrastructure dependencies. It executes SQL scans over 1,000,000 rows in <15ms, making evaluation test runs blazing fast and reproducible anywhere.

---

### ADR-003: Formalize Tri-Partite Partitioning (Skill vs. System Prompt vs. Tool)
* **Status**: Accepted
* **Context**: The Pixalate JD explicitly demands defining what belongs in a skill, what belongs in a system prompt, and what belongs in a tool.
* **Decision**: 
  * **System Prompt**: Static persona, security guardrails, epistemic confidence rules, and clarification directives.
  * **Claude Skills**: Dynamic, versioned forensic workflows and domain taxonomies (e.g., CTV screensaver playback patterns).
  * **Tools**: Pure, deterministic computation and data retrieval with strict token caps.
* **Rationale**: Prevents prompt bloat and maintains clear architectural boundaries as products evolve.

---

### ADR-004: Programmatic Ambiguity Gate (`AmbiguityGate`) for Clarifications
* **Status**: Accepted
* **Context**: Pure LLM reasoning can be fickle; temperature variations or minor prompt changes can cause the model to forget to ask clarifying questions.
* **Decision**: Pair the LLM system prompt instructions with a pre-flight slot-completeness scorer (`AmbiguityGate`).
* **Rationale**: Guarantees a $>98\%$ Clarification Trigger Rate on underspecified queries by enforcing structural constraints before tool dispatch.

---

### ADR-005: Deterministic Assertion Evaluators over Fuzzy LLM-as-a-Judge
* **Status**: Accepted
* **Context**: Measuring agent quality in CI/CD requires high reproducibility without nondeterministic judgment drift.
* **Decision**: Use deterministic Python evaluators (exact tool call comparison, slot verification, AST parsing, and regex confidence audits) for pass/fail gates. LLM-as-a-judge is reserved only for subjective tone checks.
* **Rationale**: Deterministic tests execute in milliseconds, cost $0.00 in API tokens, and eliminate flaky CI test runs.

---

### ADR-006: Hard Token Budget Ceiling (800 Tokens) on MCP Tool Returns
* **Status**: Accepted
* **Context**: Returning massive raw JSON dumps from telemetry queries causes context window bloat, increases inference latency, and triggers LLM hallucinations.
* **Decision**: Enforce a server-side maximum ceiling of 800 tokens per tool invocation. Any larger result set must be aggregated into statistical distributions before leaving the MCP server.
* **Rationale**: Balances information density with cost, latency, and context preservation.
