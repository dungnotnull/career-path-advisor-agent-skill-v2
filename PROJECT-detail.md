# PROJECT-detail.md — Career Path Advisor (staged skills & goals)

## Executive Summary
`career-path-advisor` is a Claude Skill in the **Career, Learning & Skills** cluster (idea #70). It acts as a career strategist and organizational psychologist who designs staged, evidence-based career roadmaps across industries. It runs a research-first, evidence-graded harness that profiles the input, selects named world-renowned frameworks, scores the subject across 6 dimensions, challenges its own conclusions, and emits a professional deliverable with a prioritized improvement roadmap.

## Problem Statement
People drift through careers without a staged plan tied to market demand. This skill builds a multi-horizon career roadmap with skill gaps, milestones and goals scored against recognized career-development frameworks.

Domain context: practitioners in career, learning & skills need decisions grounded in citable, current methodology rather than ad-hoc opinion. This skill enforces the evidence hierarchy (Systematic Review > Meta-Analysis > RCT > Cohort > Expert Opinion > Blog) and keeps its knowledge current through a weekly crawl.

## Target Users & Use Cases
- **Trigger example A:** User says *"Evaluate / score / optimize my career path advisor"* → skill runs the full harness and returns a scored report + roadmap.
- **Trigger example B:** User provides an artifact (document, dataset, design, plan) → skill audits it against the frameworks below.
- **Trigger example C:** User asks *"What should I improve first?"* → skill returns the impact/effort-ranked roadmap section only.

## Harness Architecture
```
USER INPUT
   |
   v
[Stage 1] sub-profile-intake  --> scoped profile / context
   |
   v
[Stage 2] sub-framework-selector  --> selected frameworks (WEF Future of Jobs skills taxonomy, ...)
   |
   v
[Stage 3] RESEARCH (WebSearch/WebFetch) --> evidence pack  (fallback: SECOND-KNOWLEDGE-BRAIN.md)
   |
   v
[Stage 4] sub-scoring-engine  --> 6-dimension score
   |
   v
[Stage 5] sub-improvement-roadmap  --> challenge / validation
   |
   v
[Stage 6] MAIN HARNESS --> final deliverable (score table + prioritized roadmap)
```

## Full Sub-Skill Catalog

### sub-profile-intake
- **Purpose:** Capture current role, skills, constraints, values and target horizon to anchor the roadmap.
- **Inputs:** scoped context from prior stage + user artifact
- **Outputs:** structured findings passed to the next stage
- **Tools used:** Read, WebSearch, WebFetch, Write
- **Quality gate:** output must be evidence-linked and complete before the harness advances

### sub-framework-selector
- **Purpose:** Choose the career-development frameworks that fit the user's stage and goals (anchors, T-shape, OKR).
- **Inputs:** scoped context from prior stage + user artifact
- **Outputs:** structured findings passed to the next stage
- **Tools used:** Read, WebSearch, WebFetch, Write
- **Quality gate:** output must be evidence-linked and complete before the harness advances

### sub-scoring-engine
- **Purpose:** Score the current trajectory across the six dimensions against WEF/O*NET demand data.
- **Inputs:** scoped context from prior stage + user artifact
- **Outputs:** structured findings passed to the next stage
- **Tools used:** Read, WebSearch, WebFetch, Write
- **Quality gate:** output must be evidence-linked and complete before the harness advances

### sub-improvement-roadmap
- **Purpose:** Produce a 30/90/365-day + 3-year staged plan with skills, milestones and learning resources.
- **Inputs:** scoped context from prior stage + user artifact
- **Outputs:** structured findings passed to the next stage
- **Tools used:** Read, WebSearch, WebFetch, Write
- **Quality gate:** output must be evidence-linked and complete before the harness advances

## Skill File Format Specification
Frontmatter schema (all skill files):
```yaml
---
name: career-path-advisor            # or sub-<name>
description: <one-line summary shown in /help>
---
```
Required sections in `main.md`: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates.

## E2E Execution Flow
1. Parse user request and artifact; if ambiguous, ask targeted intake questions.
2. Run `sub-profile-intake` to build the scoped profile.
3. Run `sub-framework-selector` to lock frameworks: WEF Future of Jobs skills taxonomy, Edgar Schein's Career Anchors, Super's Life-Career Rainbow, T-shaped skills model....
4. Research: issue WebSearch queries (future of work skills demand; career development framework; labor market skills trends); WebFetch top authoritative hits; grade evidence. On failure, fall back to SECOND-KNOWLEDGE-BRAIN.md and label the degradation.
5. Run `sub-scoring-engine` to score the 6 dimensions.
6. Run `sub-improvement-roadmap` challenge pass.


8. Synthesize the final deliverable.

## Scoring Dimensions
1. Goal clarity & realism
2. Skill-gap coverage
3. Market demand alignment
4. Milestone sequencing
5. Transferable-skill leverage
6. Risk & resilience

Each dimension is scored 0–5 with an evidence citation and a one-line justification; the overall score is the weighted mean (weights set by `sub-framework-selector`).

## SECOND-KNOWLEDGE-BRAIN Integration
- **Sources:** ArXiv (econ.GN, cs.CY); WEF Future of Jobs Report, LinkedIn Economic Graph / Workforce Reports, O*NET OnLine occupational data, BLS Occupational Outlook Handbook, McKinsey/Deloitte future-of-work research.
- **Crawl config:** weekly cron via `tools/knowledge_updater.py` (crawl4ai).
- **Append format:** scored entries (title, authors, year, DOI/URL, key finding, relevance) added to the Knowledge Update Log with a date stamp and dedup by URL/DOI hash.

## Supporting Tools Spec
`tools/knowledge_updater.py`:
- **Inputs:** search queries (above), ArXiv categories, last-run timestamp.
- **Outputs:** appended entries in `SECOND-KNOWLEDGE-BRAIN.md`.
- **Schedule:** weekly.

## Quality Gates (must all be TRUE before final output)
- Every dimension scored with a cited source or explicit fallback label.
- At least one framework from the catalog explicitly applied.
- Challenge phase documented (≥3 counter-arguments considered).


- Roadmap items carry impact + effort ratings.

## Test Scenarios (summary; full set in tests/)
1. Happy-path full audit of a typical career, learning & skills artifact.
2. Ambiguous/incomplete input → intake clarification path.
3. Offline/degraded mode → graceful fallback to knowledge brain.
4. Edge artifact stress test (adversarial input).
5. Roadmap-only request → returns prioritized recommendations.

## Key Design Decisions
1. Framework-grounded scoring only — no ad-hoc criteria.
2. Research-first with explicit graceful degradation.
3. Mandatory challenge phase before synthesis.
4. Impact/effort roadmap is always the final artifact.
5. Self-improving knowledge base via weekly crawl.
