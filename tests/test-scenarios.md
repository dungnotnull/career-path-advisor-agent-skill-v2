# Test Scenarios — Career Path Advisor (staged skills & goals)

Skill: `career-path-advisor` · idea #70 · cluster `career-education`
Minimum 5 scenarios; each lists Setup → Expected Behavior → Pass Criteria.

## Scenario 1: Happy-path full evaluation
- **Setup:** A representative career, learning & skills artifact is submitted for full audit.
- **Expected behavior:** Harness runs all stages, scores 6 dimensions against WEF Future of Jobs skills taxonomy (+others), and returns a report with a prioritized roadmap.
- **Pass criteria:** Report contains scoring table, challenge notes, roadmap with impact/effort, and graded citations.

## Scenario 2: Ambiguous / incomplete input
- **Setup:** User submits a partial artifact missing key context.
- **Expected behavior:** Intake sub-skill detects gaps and asks targeted clarifying questions before scoring.
- **Pass criteria:** Skill asks ≤5 focused questions; does not fabricate missing data.

## Scenario 3: Offline / degraded research mode
- **Setup:** WebSearch/WebFetch are unavailable during the run.
- **Expected behavior:** Skill falls back to SECOND-KNOWLEDGE-BRAIN.md and labels the degradation in the output.
- **Pass criteria:** Output explicitly flags fallback mode; still produces a scored report.

## Scenario 4: Challenge phase changes the verdict
- **Setup:** Initial scoring is over-optimistic on one dimension.
- **Expected behavior:** Devil's-advocate sub-skill surfaces ≥3 counter-arguments and at least one score is revised.
- **Pass criteria:** Challenge section documents the revision and its rationale.

## Scenario 5: Roadmap-only request
- **Setup:** User asks only 'what should I fix first?'
- **Expected behavior:** Skill returns the prioritized roadmap section ranked by impact/effort.
- **Pass criteria:** Output is the roadmap table alone, correctly ranked, traceable to framework basis.

## Regression Checklist
- [ ] All 6 dimensions appear in the scoring table.
- [ ] At least one named framework cited per run.
- [ ] Evidence tiers labeled on every external claim.


- [ ] Roadmap items ranked by impact × effort.
