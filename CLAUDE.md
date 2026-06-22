# CLAUDE.md — Career Path Advisor (staged skills & goals)

**Skill name:** `career-path-advisor`
**Tagline:** Career Path Advisor (staged skills & goals)
**Source idea:** #70  |  **Cluster:** `career-education` (Career, Learning & Skills)
**Current phase:** Phase 2 complete (core sub-skills + harness + quality gates). Phase 3 knowledge pipeline scaffolded.

## Problem This Skill Solves
People drift through careers without a staged plan tied to market demand. This skill builds a multi-horizon career roadmap with skill gaps, milestones and goals scored against recognized career-development frameworks.

## Harness Flow Summary
1. **Intake / scoping** → `sub-profile-intake.md` gathers context and constraints.
2. **Framework selection** → `sub-framework-selector.md` chooses the named evaluation frameworks for this case.
3. **Research / evidence** → WebSearch + WebFetch pull authoritative sources; fall back to SECOND-KNOWLEDGE-BRAIN.md if offline.
4. **Scoring / analysis** → `sub-scoring-engine.md` scores across the 6 dimensions.
5. **Challenge phase** → devil's-advocate review (`sub-improvement-roadmap.md`).
6. **Synthesis** → main harness assembles the final professional deliverable (score + prioritized roadmap).

Standard quality gates apply (see Quality Gates below).

## Sub-skills
- `skills/sub-profile-intake.md` — Capture current role, skills, constraints, values and target horizon to anchor the roadmap.
- `skills/sub-framework-selector.md` — Choose the career-development frameworks that fit the user's stage and goals (anchors, T-shape, OKR).
- `skills/sub-scoring-engine.md` — Score the current trajectory across the six dimensions against WEF/O*NET demand data.
- `skills/sub-improvement-roadmap.md` — Produce a 30/90/365-day + 3-year staged plan with skills, milestones and learning resources.

## Tools Required
- WebSearch, WebFetch (research-first evidence gathering)
- Read, Write (deliverable assembly)
- Bash / Python (run `tools/knowledge_updater.py`)

## Knowledge Sources
- ArXiv categories: econ.GN, cs.CY
- Domain sources: WEF Future of Jobs Report, LinkedIn Economic Graph / Workforce Reports, O*NET OnLine occupational data, BLS Occupational Outlook Handbook, McKinsey/Deloitte future-of-work research

## Supporting Python Tools
- `tools/knowledge_updater.py` — crawl4ai pipeline that refreshes `SECOND-KNOWLEDGE-BRAIN.md` weekly.

## Active Development Tasks
- [x] Scaffold folder + 8 required deliverables
- [x] Define 7 named evaluation frameworks
- [x] Implement 4 sub-skills (min 3)
- [ ] Wire shared cluster sub-skills across `career-education`
- [ ] First live crawl to seed SECOND-KNOWLEDGE-BRAIN knowledge log

## Reference Docs
- `PROJECT-detail.md` — full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — self-improving knowledge base
