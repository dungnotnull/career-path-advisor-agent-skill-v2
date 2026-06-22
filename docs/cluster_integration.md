# Cluster Integration — Career-Education Shared Sub-Skills

## Overview

The `career-education` cluster shares common sub-skills across sibling skills to ensure consistency, reduce duplication, and standardize outputs. This document defines the integration patterns and shared components.

## Cluster Members

Current members of the `career-education` cluster:
1. **career-path-advisor** (idea #70) — Career strategy and roadmap planning
2. **(Future) learning-path-optimizer** — Educational content and curriculum planning
3. **(Future) skill-gap-analyzer** — Skills assessment and development planning
4. **(Future) mentor-matcher** — Professional mentoring connection strategies

## Shared Sub-Skills

### 1. Profile Intake (`sub-profile-intake-shared.md`)

**Purpose**: Capture consistent user profile data across all cluster skills.

**Standardized Inputs**:
```yaml
user_context:
  current_role: string           # Current job title/role
  industry: string              # Industry sector
  experience_years: integer      # Total years experience
  target_horizon: string         # Timeframe for goals (30/90/365/3-year)
  constraints:
    geographic: list[string]     # Location constraints
    financial: string           # Budget limitations
    time_availability: string   # Study/practice time available
  values:
    work_life_balance: integer   # 1-5 priority
    income_growth: integer       # 1-5 priority
    stability: integer           # 1-5 priority
    growth: integer              # 1-5 priority
  skills:
    technical: list[string]      # Current technical skills
    soft: list[string]          # Current soft skills
    certifications: list[string] # Professional certifications
```

**Standardized Outputs**:
```yaml
profile_summary:
  career_stage: string          # Early/Mid/Late career
  primary_goal: string          # Main objective category
  readiness_score: float        # 0-1 preparation level
  key_constraints: list[string] # Critical limiting factors
  recommended_approach: string  # Strategy type to apply
```

**Quality Gates**:
- All required fields populated or explicitly marked as N/A
- Numeric values within valid ranges
- At least 3 skills identified or user confirms skill assessment pending

### 2. Framework Selector (`sub-framework-selector-shared.md`)

**Purpose**: Apply consistent career-development frameworks across cluster skills.

**Framework Library** (shared across cluster):
```yaml
frameworks:
  career_development:
    - WEF Future of Jobs taxonomy
    - Edgar Schein's Career Anchors
    - Super's Life-Career Rainbow
    - Holland's RIASEC (optional)

  skill_development:
    - T-shaped skills model
    - Dreyfus skill acquisition model
    - 70-20-10 development model

  goal_setting:
    - SMART framework
    - OKR (Objectives and Key Results)
    - WOOP (Wish, Outcome, Obstacle, Plan)

  competency_modeling:
    - O*NET competency taxonomy
    - ESCO (European Skills, Competences, Qualifications)
    - Skills-based hiring framework

  learning_science:
    - Bloom's taxonomy
    - Deliberate practice framework
    - Spaced repetition principles
```

**Selection Logic**:
```python
def select_frameworks(user_profile, skill_type):
    """Select appropriate frameworks based on user context."""
    frameworks = []

    # Career stage determines base framework
    if user_profile['career_stage'] == 'early':
        frameworks.extend(['WEF taxonomy', 'T-shaped model'])
    elif user_profile['career_stage'] == 'mid':
        frameworks.extend(['Career Anchors', '70-20-10 model'])
    else:  # late career
        frameworks.extend(['Life-Career Rainbow', 'Competency modeling'])

    # Goal type adds specialized frameworks
    if user_profile['primary_goal'] == 'skill_transition':
        frameworks.append('O*NET competency')
    elif user_profile['primary_goal'] == 'role_advancement':
        frameworks.append('OKR framework')

    return frameworks
```

### 3. Evidence-Based Assessment (`sub-evidence-scoring-shared.md`)

**Purpose**: Standardized evidence grading and citation across cluster skills.

**Evidence Hierarchy** (consistent across cluster):
```yaml
evidence_tiers:
  tier_1_systematic: 5.0        # Systematic reviews, meta-analyses
  tier_2_experimental: 4.5       # RCTs, quasi-experimental
  tier_3_observational: 3.5      # Cohort, longitudinal studies
  tier_4_consensus: 3.0          # Expert consensus, guidelines
  tier_5_opinion: 2.0            # Expert opinion, case studies
  tier_6_industry: 2.5           # Industry reports (varies by source)
  tier_7_anecdotal: 1.0          # Blog posts, anecdotes
```

**Citation Format** (standardized across cluster):
```markdown
[Source Name](URL) — Evidence Tier: [Tier Level] — Last Updated: [Date]
```

**Quality Gates**:
- All claims >20% impact require tier 3+ evidence
- Industry reports require source authority scoring
- Claims without evidence explicitly labeled as "expert judgment"

### 4. Improvement Roadmap Generator (`sub-roadmap-generator-shared.md`)

**Purpose**: Generate consistent roadmap outputs across cluster skills.

**Standard Roadmap Format**:
```markdown
## Prioritized [Context-Specific] Roadmap

| Priority | Recommendation | Impact | Effort | Framework Basis | Timeline | Dependencies |
|----------|----------------|--------|--------|-----------------|----------|---------------|
| 1 | [Action item] | H/M/L | H/M/L | [Framework name] | [Duration] | [Prerequisites] |
```

**Impact/Effort Scoring Matrix**:
```python
def score_impact_effort(recommendation, user_profile):
    """Calculate impact and effort scores consistently."""
    # Impact factors
    impact_factors = {
        'goal_alignment': 0.3,      # Alignment with stated goals
        'market_demand': 0.25,       # External demand for skill/outcome
        'skill_transferability': 0.2, # Broad applicability
        'timing_relevance': 0.15,     # Critical path positioning
        'resource_efficiency': 0.1   # ROI on time/investment
    }

    # Effort factors
    effort_factors = {
        'time_required': 0.4,        # Hours/days to completion
        'complexity': 0.3,           # Cognitive/skill complexity
        'resource_cost': 0.2,        # Financial/infrastructure needs
        'dependency_chain': 0.1      # Prerequisite requirements
    }

    impact = sum(impact_factors[key] * score for key, score in ...)
    effort = sum(effort_factors[key] * score for key, score in ...)

    return impact, effort
```

**Timeline Standards** (consistent across cluster):
- **Quick Wins**: ≤30 days (Low/High impact, Low effort)
- **Short-term**: 30-90 days (Medium/High impact, Medium effort)
- **Medium-term**: 90-180 days (High impact, High/High effort)
- **Long-term**: 180-365 days (High impact, High effort)
- **Strategic**: 365+ days (Very High impact, Very High effort)

## Integration Patterns

### Pattern 1: Sequential Skill Execution

```yaml
workflow:
  - skill: career-path-advisor
    stage: profile_intake
    output_to: shared_profile_intake

  - skill: learning-path-optimizer
    stage: profile_intake
    input_from: shared_profile_intake
    output_to: shared_curriculum_plan

  - skill: skill-gap-analyzer
    stage: gap_analysis
    input_from: shared_profile_intake
    output_to: shared_skill_development_plan
```

### Pattern 2: Parallel Assessment with Synthesis

```yaml
workflow:
  parallel_stage:
    - skill: career-path-advisor
      output: career_roadmap

    - skill: learning-path-optimizer
      output: learning_curriculum

    - skill: skill-gap-analyzer
      output: skill_assessment

  synthesis_stage:
    - skill: career-path-advisor  # Master synthesizer
      inputs: [career_roadmap, learning_curriculum, skill_assessment]
      output: integrated_development_plan
```

### Pattern 3: Iterative Refinement Loop

```yaml
workflow:
  - skill: career-path-advisor
    stage: initial_assessment
    output: initial_roadmap

  - skill: learning-path-optimizer
    stage: resource_planning
    input: initial_roadmap
    output: resource_constraints

  - skill: career-path-advisor
    stage: refined_assessment
    input: resource_constraints
    output: refined_roadmap

  - skill: skill-gap-analyzer
    stage: detailed_analysis
    input: refined_roadmap
    output: skill_development_plan
```

## Data Exchange Format

### Standard Cluster Message Format

```json
{
  "cluster": "career-education",
  "source_skill": "career-path-advisor",
  "target_skill": "learning-path-optimizer",
  "message_type": "profile_summary",
  "timestamp": "2024-06-22T10:30:00Z",
  "data": {
    "user_profile": { /* standardized profile */ },
    "assessment_summary": { /* skill-specific summary */ },
    "recommendations": [ /* prioritized list */ ],
    "metadata": {
      "frameworks_applied": ["WEF", "O*NET"],
      "evidence_grade": 3.5,
      "confidence_level": 0.8
    }
  }
}
```

## Quality Standards (Cluster-Wide)

### Output Quality Gates
1. **Evidence Linkage**: All significant claims cite evidence tier
2. **Framework Application**: At least one named framework applied
3. **Actionability**: All recommendations include timeline and dependencies
4. **Consistency**: Terminology and scoring consistent across cluster
5. **Reproducibility**: Same inputs produce ±10% variance in outputs

### Performance Standards
1. **Response Time**: <10 seconds for standard evaluation
2. **Accuracy**: Framework applications validated quarterly
3. **Freshness**: Evidence sources reviewed weekly
4. **Reliability**: >95% successful execution rate
5. **Graceful Degradation**: Full offline capability

## Implementation Status

### Current Integration (career-path-advisor)
- [x] Shared profile intake format
- [x] Framework selector with 7 frameworks
- [x] Evidence-based assessment with tier grading
- [x] Standardized roadmap generator
- [x] Quality gate enforcement

### Future Integration (pending sibling skills)
- [ ] Create shared profile intake sub-skill for cluster
- [ ] Standardize framework selector across cluster
- [ ] Implement cluster-level evidence grading
- [ ] Develop cluster roadmap synthesis logic
- [ ] Add cluster-level quality monitoring

## Migration Path

### Phase 1: Extract Shared Components
- Move common intake logic to `sub-profile-intake-shared.md`
- Extract framework selector to shared sub-skill
- Standardize evidence grading across cluster

### Phase 2: Define Integration Points
- Specify data exchange formats
- Implement message passing protocols
- Add cluster-level orchestration

### Phase 3: Validate Cross-Skill Workflows
- Test sequential skill execution
- Validate parallel assessment synthesis
- Verify iterative refinement loops

### Phase 4: Deploy Cluster Integration
- Update all cluster skills with shared components
- Implement cluster-level monitoring
- Document integration patterns

## Benefits of Cluster Integration

1. **Consistency**: Standardized terminology and scoring across skills
2. **Efficiency**: Reduced code duplication, shared maintenance
3. **Quality**: Centralized validation and quality control
4. **Scalability**: Easy addition of new cluster skills
5. **User Experience**: Coherent multi-skill workflows

## Conclusion

The `career-education` cluster integration provides a foundation for consistent, high-quality career development guidance across multiple specialized skills. The shared sub-skills ensure standardized inputs, outputs, and quality while allowing skill-specific specialization in core logic.

**Current Status**: career-path-advisor fully implements cluster standards, ready for sibling skill integration.
