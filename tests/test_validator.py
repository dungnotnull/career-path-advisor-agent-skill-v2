# -*- coding: utf-8 -*-
"""
test_validator.py — Comprehensive validation framework for career-path-advisor scenarios.

Implements the 5 required test scenarios with proper validation, scoring calibration,
and regression testing as specified in tests/test-scenarios.md
"""

import os
import sys
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class ScenarioType(Enum):
    """Test scenario types as defined in test-scenarios.md"""
    HAPPY_PATH = "happy_path_full_evaluation"
    AMBIGUOUS_INPUT = "ambiguous_incomplete_input"
    OFFLINE_MODE = "offline_degraded_mode"
    CHALLENGE_PHASE = "challenge_phase_changes"
    ROADMAP_ONLY = "roadmap_only_request"


@dataclass
class ValidationCriteria:
    """Validation criteria for test scenarios."""
    dimension_count: int = 6
    min_framework_citations: int = 1
    min_challenge_arguments: int = 3
    max_intake_questions: int = 5
    evidence_tiers_required: bool = True
    impact_effort_required: bool = True
    fallback_label_required: bool = False


@dataclass
class TestResult:
    """Test execution result."""
    scenario: str
    passed: bool
    score: float
    criteria_met: Dict[str, bool]
    issues: List[str]
    execution_time_ms: float
    timestamp: str


class OutputValidator:
    """Validates skill output against quality gates and requirements."""

    def __init__(self, criteria: ValidationCriteria = None):
        self.criteria = criteria or ValidationCriteria()

    def validate_dimension_table(self, output: str) -> Dict[str, Any]:
        """Validate that all 6 dimensions are present in scoring table."""
        required_dimensions = [
            "goal clarity",
            "skill-gap coverage",
            "market demand alignment",
            "milestone sequencing",
            "transferable-skill leverage",
            "risk & resilience"
        ]

        found = []
        missing = []

        output_lower = output.lower()
        for dimension in required_dimensions:
            if dimension in output_lower:
                found.append(dimension)
            else:
                missing.append(dimension)

        return {
            'passed': len(missing) == 0,
            'found': found,
            'missing': missing,
            'count': len(found)
        }

    def validate_framework_citations(self, output: str) -> Dict[str, Any]:
        """Validate that at least one named framework is cited."""
        frameworks = [
            "WEF Future of Jobs",
            "Edgar Schein's Career Anchors",
            "Super's Life-Career Rainbow",
            "T-shaped skills",
            "SMART",
            "OKR",
            "O*NET",
            "70-20-10"
        ]

        cited = []
        output_lower = output.lower()

        for framework in frameworks:
            if framework.lower() in output_lower or framework.split()[0].lower() in output_lower:
                cited.append(framework)

        return {
            'passed': len(cited) >= self.criteria.min_framework_citations,
            'cited_frameworks': cited,
            'count': len(cited)
        }

    def validate_challenge_phase(self, output: str) -> Dict[str, Any]:
        """Validate that challenge phase has minimum arguments."""
        # Look for challenge/devil's advocate section
        challenge_section = None

        patterns = [
            r'#{2,3}\s*(?:challenge|devil.?s.?advocate|counter.?argument)',
            r'challenge\s*(?:phase|section)',
            r'counter.?arguments?\s*(?:considered|noted)'
        ]

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                # Extract content after this header
                challenge_section = output[match.start():match.start()+2000]
                break

        if not challenge_section:
            return {
                'passed': False,
                'argument_count': 0,
                'issues': ['No challenge section found']
            }

        # Count arguments (look for bullet points, numbered lists, or "challenge" keyword)
        argument_patterns = [
            r'[\-\*]\s+(?:challenge|counter|argument|concern)',
            r'\d+\.\s+(?:challenge|counter|argument|concern)',
            r'(?:however|alternatively|conversely|on the other hand)',
        ]

        total_args = 0
        for pattern in argument_patterns:
            matches = re.findall(pattern, challenge_section, re.IGNORECASE)
            total_args += len(matches)

        # Also count list items in challenge section
        list_items = re.findall(r'[\-\*]\s+\w+\s*:', challenge_section)
        total_args += len(list_items)

        return {
            'passed': total_args >= self.criteria.min_challenge_arguments,
            'argument_count': total_args,
            'section_found': True
        }

    def validate_roadmap_format(self, output: str) -> Dict[str, Any]:
        """Validate roadmap has impact/effort ratings and proper format."""
        # Look for roadmap section
        roadmap_patterns = [
            r'#{2,3}\s*(?:improvement\s+)?roadmap',
            r'prioritized\s+roadmap',
            r'30\s*\/\s*90\s*\/\s*365'
        ]

        roadmap_section = None
        for pattern in roadmap_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                roadmap_section = output[match.start():]
                break

        if not roadmap_section:
            return {
                'passed': False,
                'issues': ['No roadmap section found']
            }

        # Check for impact/effort columns
        has_impact = bool(re.search(r'impact\s*\([^)]*\)', roadmap_section, re.IGNORECASE))
        has_effort = bool(re.search(r'effort\s*\([^)]*\)', roadmap_section, re.IGNORECASE))

        # Check for framework basis column
        has_framework = bool(re.search(r'framework\s*basis', roadmap_section, re.IGNORECASE))

        # Check for table structure
        has_table = bool(re.search(r'\|.*\|', roadmap_section))

        # Check for ranking (numbers or priorities)
        has_ranking = bool(re.search(r'[#\d]+\s+\w+', roadmap_section))

        return {
            'passed': has_impact and has_effort and has_framework,
            'has_impact': has_impact,
            'has_effort': has_effort,
            'has_framework': has_framework,
            'has_table': has_table,
            'has_ranking': has_ranking
        }

    def validate_evidence_grading(self, output: str) -> Dict[str, Any]:
        """Validate evidence tiers are labeled on external claims."""
        evidence_tiers = [
            'systematic review',
            'meta-analysis',
            'rct',
            'cohort',
            'expert opinion',
            'industry report'
        ]

        found_tiers = []
        output_lower = output.lower()

        for tier in evidence_tiers:
            if tier in output_lower:
                found_tiers.append(tier)

        # Look for evidence section or citations
        has_citations = bool(re.search(r'#{2,3}\s*(?:sources?|evidence|citations?|references?)', output, re.IGNORECASE))
        has_bracketed_citations = bool(re.search(r'\[\d+\]', output))

        return {
            'passed': len(found_tiers) > 0 or has_citations or has_bracketed_citations,
            'found_tiers': found_tiers,
            'has_citations_section': has_citations,
            'has_bracketed_citations': has_bracketed_citations
        }

    def validate_fallback_label(self, output: str) -> Dict[str, Any]:
        """Validate graceful degradation label is present in offline mode."""
        fallback_indicators = [
            r'fallback\s*mode',
            r'offline\s*mode',
            r'degraded\s*(?:research|search)',
            r'using\s*cached\s*knowledge',
            r'second.?knowledge.?brain'
        ]

        found = []
        for pattern in fallback_indicators:
            if re.search(pattern, output, re.IGNORECASE):
                found.append(pattern)

        return {
            'passed': len(found) > 0,
            'found_patterns': found
        }

    def validate_score_range(self, output: str) -> Dict[str, Any]:
        """Validate that scores are within 0-5 range."""
        # Look for scores in various formats
        score_patterns = [
            r'score\s*[:\-]\s*(\d+\.?\d*)\s*/\s*5',
            r'score\s*[:\-]\s*(\d+\.?\d*)\s*\(\s*0\s*-\s*5',
            r'\|\s*\d+\.?\d*\s*\|.*score',
        ]

        scores = []
        for pattern in score_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            scores.extend([float(m) for m in matches])

        # Also check dimension table rows
        dimension_scores = re.findall(r'\|\s*(\d+\.?\d*)\s*\|\s*(?:goal|skill|market|milestone|transferable|risk)', output, re.IGNORECASE)
        scores.extend([float(s) for s in dimension_scores])

        valid_scores = [s for s in scores if 0 <= s <= 5]

        return {
            'passed': len(valid_scores) > 0 and all(0 <= s <= 5 for s in valid_scores),
            'scores_found': valid_scores,
            'count': len(valid_scores)
        }

    def run_all_validations(self, output: str, scenario_type: ScenarioType) -> Dict[str, Any]:
        """Run all applicable validations for a scenario."""
        validations = {
            'dimension_table': self.validate_dimension_table(output),
            'framework_citations': self.validate_framework_citations(output),
            'challenge_phase': self.validate_challenge_phase(output),
            'roadmap_format': self.validate_roadmap_format(output),
            'evidence_grading': self.validate_evidence_grading(output),
            'score_range': self.validate_score_range(output)
        }

        # Scenario-specific validations
        if scenario_type == ScenarioType.OFFLINE_MODE:
            validations['fallback_label'] = self.validate_fallback_label(output)

        return validations


class ScenarioExecutor:
    """Execute and validate test scenarios."""

    def __init__(self):
        self.validator = OutputValidator()
        self.results = []

    def execute_scenario(self, scenario_type: ScenarioType, input_data: Dict[str, Any]) -> TestResult:
        """Execute a single test scenario with validation."""
        import time

        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"Executing: {scenario_type.value}")
        print('='*60)

        try:
            # Simulate skill execution (in production, this would call the actual skill)
            output = self._simulate_skill_execution(scenario_type, input_data)

            # Run validations
            validations = self.validator.run_all_validations(output, scenario_type)

            # Calculate overall pass/fail
            all_passed = all(v.get('passed', False) for v in validations.values())

            # Compile criteria met
            criteria_met = {k: v.get('passed', False) for k, v in validations.items()}

            # Identify issues
            issues = []
            for name, result in validations.items():
                if not result.get('passed', False):
                    issues.append(f"{name}: {result.get('issues', ['Failed validation'])}")

            execution_time = (time.time() - start_time) * 1000

            result = TestResult(
                scenario=scenario_type.value,
                passed=all_passed,
                score=self._calculate_score(validations),
                criteria_met=criteria_met,
                issues=issues,
                execution_time_ms=execution_time,
                timestamp=datetime.now().isoformat()
            )

            self.results.append(result)

            # Print summary
            print(f"Status: {'✓ PASS' if result.passed else '✗ FAIL'}")
            print(f"Score: {result.score:.1f}/100")
            if issues:
                print("Issues:")
                for issue in issues:
                    print(f"  - {issue}")

            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            print(f"Error executing scenario: {e}")

            return TestResult(
                scenario=scenario_type.value,
                passed=False,
                score=0.0,
                criteria_met={},
                issues=[f"Execution error: {str(e)}"],
                execution_time_ms=execution_time,
                timestamp=datetime.now().isoformat()
            )

    def _simulate_skill_execution(self, scenario_type: ScenarioType, input_data: Dict[str, Any]) -> str:
        """Simulate skill execution for testing purposes."""
        # In production, this would call the actual skill via the Skill tool

        if scenario_type == ScenarioType.HAPPY_PATH:
            return self._happy_path_output()
        elif scenario_type == ScenarioType.AMBIGUOUS_INPUT:
            return self._ambiguous_input_response()
        elif scenario_type == ScenarioType.OFFLINE_MODE:
            return self._offline_mode_output()
        elif scenario_type == ScenarioType.CHALLENGE_PHASE:
            return self._challenge_phase_output()
        elif scenario_type == ScenarioType.ROADMAP_ONLY:
            return self._roadmap_only_output()
        else:
            return "# Generic Output\n\nBasic skill output."

    def _happy_path_output(self) -> str:
        """Generate output for happy path scenario."""
        return """# Career Path Advisor — Evaluation Report

## 1. Executive Summary
- Overall score: 4.2 / 5
- Top 3 strengths: Market demand alignment, Transferable skills, Clear milestones
- Top 3 priority fixes: Skill-gap coverage, Risk mitigation, Goal specificity

## 2. Scoring Table
| Dimension | Score (0-5) | Evidence / Framework | Justification |
|-----------|-------------|----------------------|---------------|
| Goal clarity & realism | 4.0 | SMART goal-setting framework | Goals are specific and time-bound |
| Skill-gap coverage | 3.0 | O*NET competency model | Some critical gaps identified |
| Market demand alignment | 4.5 | WEF Future of Jobs 2024 | Strong alignment with growing fields |
| Milestone sequencing | 4.0 | 70-20-10 development model | Logical progression with practical application |
| Transferable-skill leverage | 4.5 | T-shaped skills model | Excellent cross-functional applicability |
| Risk & resilience | 3.5 | Career Anchors theory | Moderate resilience planning |

## 3. Detailed Findings
The career plan shows strong alignment with WEF Future of Jobs skills taxonomy, particularly in analytical thinking and flexibility. The application of SMART goal-setting principles provides clear structure...

## 4. Challenge / Devil's-Advocate Notes
- **Counter-argument 1**: The current plan may overestimate the speed of industry adoption for AI skills
- **Counter-argument 2**: Limited consideration of geographic market variations
- **Counter-argument 3**: Insufficient backup planning for economic downturns
- **Revised assessment**: Reduced market demand score from 4.8 to 4.5 based on adoption timing concerns

## 5. Prioritized Improvement Roadmap
| # | Recommendation | Impact (H/M/L) | Effort (H/M/L) | Framework basis |
|---|----------------|----------------|----------------|-----------------|
| 1 | Fill critical skill gaps in AI/ML | H | M | O*NET competency model |
| 2 | Add geographic market research | H | L | WEF regional analysis |
| 3 | Develop economic resilience plan | M | H | Career Anchors theory |
| 4 | Strengthen industry certifications | M | M | Skills-based hiring |
| 5 | Enhance networking activities | L | M | 70-20-10 model |

## 6. Sources & Evidence Grade
1. WEF Future of Jobs Report 2024 - Industry Report (2.5)
2. O*NET OnLine Database - Expert Consensus (3.0)
3. Edgar Schein Career Anchors Research - Expert Opinion (2.0)
"""

    def _ambiguous_input_response(self) -> str:
        """Generate response for ambiguous input scenario."""
        return """# Career Path Advisor — Intake Clarification

To provide an accurate evaluation, I need clarification on a few key areas:

## Clarifying Questions
1. **Current Role**: What is your current job title and industry?
2. **Time Horizon**: Are you planning for the next 1, 3, or 5 years?
3. **Primary Goal**: Are you seeking advancement within your current field, a career pivot, or entering a new field?
4. **Skills Focus**: Which technical or soft skills are you most interested in developing?
5. **Constraints**: Are there any geographic, financial, or time constraints I should consider?

Once you provide these details, I'll conduct a comprehensive evaluation using established frameworks like WEF Future of Jobs and Edgar Schein's Career Anchors.
"""

    def _offline_mode_output(self) -> str:
        """Generate output for offline/degraded mode scenario."""
        return """# Career Path Advisor — Evaluation Report (Degraded Mode)

> **Note**: This evaluation was generated in fallback mode using cached knowledge base (SECOND-KNOWLEDGE-BRAIN.md) due to research tool unavailability. Some data may not reflect the most current market conditions.

## 1. Executive Summary
- Overall score: 3.8 / 5 (based on cached knowledge)
- **Degradation**: Limited to knowledge base data up to 2026-06-18

## 2. Scoring Table
| Dimension | Score (0-5) | Evidence / Framework | Justification |
|-----------|-------------|----------------------|---------------|
| Goal clarity & realism | 3.5 | SMART goal-setting | Based on cached framework data |
| Skill-gap coverage | 3.0 | O*NET competency model | Using cached competency definitions |
| Market demand alignment | 4.0 | WEF Future of Jobs (cached) | Based on 2024 data from knowledge base |

[... continues with full analysis using cached data ...]

**Fallback Mode Active**: Real-time research unavailable. Recommendations based on knowledge base as of 2026-06-18.
"""

    def _challenge_phase_output(self) -> str:
        """Generate output demonstrating challenge phase revisions."""
        return """# Career Path Advisor — Evaluation Report

## 4. Challenge / Devil's-Advocate Notes

### Initial Assessment Concerns
The initial scoring was optimistic about the transition timeline.

### Counter-Arguments Considered
1. **Industry Timing Risk**: The target industry may face automation disruption within 18 months, reducing entry-level opportunities
2. **Credential Competition**: Top-tier certifications increasingly require 2+ years experience, not immediately achievable
3. **Geographic Saturation**: Primary target markets show 40% increase in qualified candidates, reducing competitive advantage

### Revisions Made
- **Market demand alignment**: Reduced from 4.8 to 3.5 (industry timing concerns)
- **Milestone sequencing**: Reduced from 4.5 to 3.8 (credential timeline adjusted)
- **Risk & resilience**: Reduced from 4.0 to 3.0 (multiple vulnerabilities identified)

### Updated Assessment
The career path requires more conservative timelines and contingency planning. Recommendations now include skill diversification and geographic flexibility.

"""

    def _roadmap_only_output(self) -> str:
        """Generate roadmap-only output for focused request."""
        return """# Prioritized Improvement Roadmap

Based on your career evaluation, here are the high-priority recommendations ranked by impact vs. effort:

| # | Recommendation | Impact (H/M/L) | Effort (H/M/L) | Framework basis | Timeline |
|---|----------------|----------------|----------------|-----------------|----------|
| 1 | Obtain cloud architecture certification | H | M | O*NET competency model | 90 days |
| 2 | Develop AI/ML fundamentals | H | H | WEF Future of Jobs taxonomy | 180 days |
| 3 | Build portfolio of migration projects | H | M | 70-20-10 development model | 90 days |
| 4 | Join professional cloud community | M | L | T-shaped networking | 30 days |
| 5 | Obtain security clearance | M | H | Industry requirement | 120 days |

**Quick Wins** (High Impact, Low Effort):
- Professional certification study groups
- Internal cross-training opportunities

**Strategic Investments** (High Impact, High Effort):
- Advanced cloud architecture training
- AI/ML specialization
"""

    def _calculate_score(self, validations: Dict[str, Any]) -> float:
        """Calculate overall quality score from validations."""
        weights = {
            'dimension_table': 20,
            'framework_citations': 15,
            'challenge_phase': 20,
            'roadmap_format': 20,
            'evidence_grading': 15,
            'score_range': 10
        }

        total_score = 0.0
        total_weight = 0.0

        for name, validation in validations.items():
            if name in weights:
                weight = weights[name]
                if validation.get('passed', False):
                    total_score += weight
                total_weight += weight

        return (total_score / total_weight * 100) if total_weight > 0 else 0.0

    def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all 5 required test scenarios."""
        print("\n" + "="*60)
        print("CAREER PATH ADVISOR — TEST SCENARIO EXECUTION")
        print("="*60)

        # Define scenario inputs
        scenarios = [
            (ScenarioType.HAPPY_PATH, {
                'artifact': 'Complete career plan document',
                'context': 'Full evaluation requested'
            }),
            (ScenarioType.AMBIGUOUS_INPUT, {
                'artifact': 'Partial information with gaps',
                'context': 'Limited context provided'
            }),
            (ScenarioType.OFFLINE_MODE, {
                'artifact': 'Standard career plan',
                'context': 'Research tools unavailable'
            }),
            (ScenarioType.CHALLENGE_PHASE, {
                'artifact': 'Overly optimistic career plan',
                'context': 'Challenge phase expected'
            }),
            (ScenarioType.ROADMAP_ONLY, {
                'artifact': 'Existing evaluation',
                'context': 'Prioritized roadmap request'
            })
        ]

        # Execute each scenario
        for scenario_type, input_data in scenarios:
            self.execute_scenario(scenario_type, input_data)

        # Compile results
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print("\n" + "="*60)
        print(f"SCENARIO RESULTS: {passed}/{total} passed")
        print("="*60)

        for result in self.results:
            status = "✓" if result.passed else "✗"
            print(f"{status} {result.scenario}: {result.score:.1f}/100 - {len(result.issues)} issues")

        return {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'results': [r.__dict__ for r in self.results],
            'success_rate': passed / total if total > 0 else 0
        }


def main():
    """Main entry point for scenario testing."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate career-path-advisor test scenarios')
    parser.add_argument('--output', '-o', default='scenario_results.json', help='Output JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    executor = ScenarioExecutor()
    results = executor.run_all_scenarios()

    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {args.output}")

    # Exit with appropriate code
    return 0 if results['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
