---
name: sub-improvement-roadmap
description: (career-path-advisor) Produce a 30/90/365-day + 3-year staged plan with skills, milestones and learning resources.
---

# Sub-skill: improvement-roadmap

## Purpose
Produce a 30/90/365-day + 3-year staged plan with skills, milestones and learning resources.

## When the Harness Calls This
Stage matching `sub-improvement-roadmap` in the `career-path-advisor` main workflow.

## Inputs
- The user's artifact and any scoped context from prior stages.
- Relevant frameworks: WEF Future of Jobs skills taxonomy, Edgar Schein's Career Anchors, Super's Life-Career Rainbow, T-shaped skills model....

## Procedure
1. Read the incoming context and the artifact.
2. Apply the relevant framework(s) for this stage.
3. Use WebSearch/WebFetch to verify any factual claim; grade evidence by tier.
4. Produce structured output for the next stage.

## Outputs
- Structured findings (markdown) passed to the next harness stage.
- Explicit citations or a labeled fallback to `SECOND-KNOWLEDGE-BRAIN.md`.

## Quality Gate
- Output is complete, evidence-linked, and within scope.
- No unsupported claims; ready for the next stage.
