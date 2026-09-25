---
name: sustainability-financial-materiality-agent
description: Which sustainability issues change revenue, margins, cash flows, credit or valuation, by how much and under which assumptions? Institutional buy-side research workflow with auditable evidence, calculations and human review; no autonomous trading.
license: MIT
metadata:
  author: HHFinAi
  version: "0.2.0"
---
# Sustainability-to-Financial-Materiality Analysis Agent

Use for financial materiality under a specified investment mandate. Read `AGENTS.md`, then select a route from `agent.json`. Follow `WORKFLOW.md` and the CLI research loop. Copy the entire repository, not just this file: scripts, prompts, schemas and references are required.

A compatible filesystem-enabled agent host may discover this skill; activation has not been certified for specific products. Text-only use applies the methodology manually and does not enforce the Python controls.

Scenario arithmetic is not a forecast. Financial materiality and impact materiality are separate; no universal ESG premium or automatic ESG score-to-WACC conversion.

Do not run a synthetic fixture as live research. Start with `examples/research-request-template.json`, replace every placeholder and register permitted evidence. Inspect `docs/INSTITUTIONAL_QUALITY.md` and `docs/AUDIT.md` before relying on outputs.
