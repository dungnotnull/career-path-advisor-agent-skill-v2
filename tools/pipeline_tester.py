# -*- coding: utf-8 -*-
"""
pipeline_tester.py — Test runner for knowledge update pipeline.

Validates all pipeline components including:
- ArXiv API connectivity
- Deduplication logic
- Relevance scoring
- Evidence grade detection
- Knowledge base append operations
"""

import os
import sys
import json
import tempfile
from typing import Dict, List, Any
from datetime import datetime

# Import the main pipeline
sys.path.insert(0, os.path.dirname(__file__))
from knowledge_updater import KnowledgePipeline, KnowledgeEntry, EVIDENCE_HIERARCHY


class PipelineTester:
    """Comprehensive test suite for knowledge update pipeline."""

    def __init__(self):
        self.test_results = []
        self.temp_brain_path = None

    def setup(self):
        """Set up test environment with temporary files."""
        self.temp_brain_path = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
        self.temp_brain_path.write(
            "# SECOND-KNOWLEDGE-BRAIN.md — Test Version\n"
            "## Test Setup\n"
            "- **2025-01-01** — Initial test setup.\n"
        )
        self.temp_brain_path.close()
        return self.temp_brain_path.name

    def teardown(self):
        """Clean up test files."""
        if self.temp_brain_path and os.path.exists(self.temp_brain_path.name):
            try:
                os.unlink(self.temp_brain_path.name)
            except Exception as e:
                print(f"Warning: Could not cleanup temp file: {e}")

    def run_test(self, test_name: str, test_func) -> Dict[str, Any]:
        """Run a single test and record results."""
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print('='*50)

        result = {
            'name': test_name,
            'passed': False,
            'message': '',
            'duration_ms': 0,
            'timestamp': datetime.now().isoformat()
        }

        try:
            import time
            start = time.time()
            test_func()
            result['passed'] = True
            result['message'] = 'Test passed successfully'
        except AssertionError as e:
            result['message'] = f'Assertion failed: {str(e)}'
        except Exception as e:
            result['message'] = f'Error: {str(e)}'
        finally:
            result['duration_ms'] = (time.time() - start) * 1000

        self.test_results.append(result)
        status = "✓ PASS" if result['passed'] else "✗ FAIL"
        print(f"{status}: {result['message']}")

        return result

    def test_arxiv_connectivity(self):
        """Test ArXiv API connectivity and data retrieval."""
        pipeline = KnowledgePipeline(self.temp_brain_path.name)
        entries = pipeline.fetch_arxiv_papers(max_results=5)

        assert len(entries) > 0, "Should fetch at least some ArXiv entries"
        assert all(e.title for e in entries), "All entries should have titles"
        assert all(e.url for e in entries), "All entries should have URLs"
        assert all(e.entry_hash for e in entries), "All entries should have hashes"

        print(f"Fetched {len(entries)} test entries from ArXiv")
        for entry in entries[:2]:
            print(f"  - {entry.title[:60]}...")

    def test_deduplication(self):
        """Test deduplication logic."""
        pipeline = KnowledgePipeline(self.temp_brain_path.name)

        # Create test entries with duplicates
        test_entries = [
            KnowledgeEntry(
                title="Test Paper 1",
                authors="Author A",
                year="2024",
                venue="Test Venue",
                url="https://example.com/paper1",
                abstract="Test abstract"
            ),
            KnowledgeEntry(
                title="Test Paper 1",  # Duplicate title
                authors="Author A",
                year="2024",
                venue="Test Venue",
                url="https://example.com/paper1",  # Duplicate URL
                abstract="Test abstract"
            ),
            KnowledgeEntry(
                title="Test Paper 1",  # Similar but not duplicate
                authors="Author B",
                year="2024",
                venue="Test Venue 2",
                url="https://example.com/paper2",
                abstract="Different abstract"
            )
        ]

        unique = pipeline.deduplicate_and_filter(test_entries)

        # Should deduplicate exact matches
        assert len(unique) <= 2, f"Should have at most 2 unique entries, got {len(unique)}"
        print(f"Deduplication reduced {len(test_entries)} entries to {len(unique)} unique entries")

    def test_relevance_scoring(self):
        """Test relevance scoring algorithm."""
        pipeline = KnowledgePipeline(self.temp_brain_path.name)

        high_relevance = KnowledgeEntry(
            title="Future of Work Skills Demand 2024: Career Development Framework",
            authors="Expert Researcher",
            year="2024",
            venue="WEF Future of Jobs Report",
            url="https://wef.org/report",
            abstract="This systematic review examines labor market skills trends and career anchors."
        )

        low_relevance = KnowledgeEntry(
            title="Unrelated Historical Document",
            authors="Unknown",
            year="1995",
            venue="Old Journal",
            url="https://old-journal.org/paper",
            abstract="Historical analysis with no relevance to career development."
        )

        high_score = pipeline.score_relevance(high_relevance)
        low_score = pipeline.score_relevance(low_relevance)

        assert high_score > low_score, f"High relevance ({high_score}) should score higher than low relevance ({low_score})"
        assert high_score >= 5.0, f"High relevance entry should score at least 5.0, got {high_score}"

        print(f"Relevance scores: High={high_score:.2f}, Low={low_score:.2f}")

    def test_evidence_grading(self):
        """Test evidence grade detection."""
        pipeline = KnowledgePipeline(self.temp_brain_path.name)

        systematic_review = KnowledgeEntry(
            title="Systematic Review of Career Development Interventions",
            authors="Research Team",
            year="2023",
            venue="Journal of Vocational Behavior",
            url="https://example.com/review",
            abstract="This systematic review and meta-analysis examines..."
        )

        opinion_piece = KnowledgeEntry(
            title="My Thoughts on Career Development",
            authors="Blogger",
            year="2024",
            venue="Personal Blog",
            url="https://blog.com/thoughts",
            abstract="In my opinion, career development is important..."
        )

        sr_grade = pipeline.detect_evidence_grade(systematic_review)
        blog_grade = pipeline.detect_evidence_grade(opinion_piece)

        assert sr_grade >= 4.5, f"Systematic review should have high grade, got {sr_grade}"
        assert blog_grade <= 2.0, f"Blog should have low grade, got {blog_grade}"

        print(f"Evidence grades: Systematic Review={sr_grade:.1f}, Blog={blog_grade:.1f}")

    def test_key_finding_extraction(self):
        """Test key finding extraction from abstracts."""
        pipeline = KnowledgePipeline(self.temp_brain_path.name)

        entry = KnowledgeEntry(
            title="Skills Gap Analysis",
            authors="Labor Research Institute",
            year="2024",
            venue="Labor Market Review",
            url="https://example.com/gap",
            abstract="This study examines the skills gap in technology sectors. We found that 65% of employers report difficulty finding qualified candidates. The results suggest that upskilling programs are needed."
        )

        finding = pipeline.extract_key_finding(entry)

        assert len(finding) > 20, f"Should extract a meaningful finding, got: {finding}"
        assert any(word in finding.lower() for word in ['found', 'shows', 'reveals', 'suggest']), \
            f"Finding should contain research action words, got: {finding}"

        print(f"Extracted key finding: '{finding[:100]}...'")

    def test_knowledge_base_append(self):
        """Test appending entries to knowledge base."""
        pipeline = KnowledgePipeline(self.temp_brain_path.name)

        test_entries = [
            KnowledgeEntry(
                title="Test Entry for Append",
                authors="Test Author",
                year="2024",
                venue="Test Venue",
                url="https://test.com/entry",
                abstract="Test abstract",
                relevance_score=5.0
            )
        ]

        # Get initial content size
        with open(self.temp_brain_path.name, 'r') as f:
            initial_size = len(f.read())

        # Append entries
        appended = pipeline.append_to_brain(test_entries)

        # Check content grew
        with open(self.temp_brain_path.name, 'r') as f:
            final_size = len(f.read())

        assert appended == 1, f"Should append 1 entry, got {appended}"
        assert final_size > initial_size, "Knowledge base should grow after append"
        assert 'Test Entry for Append' in open(self.temp_brain_path.name).read(), "Entry should be in file"

        print(f"Successfully appended {appended} entries to test knowledge base")

    def test_hash_generation(self):
        """Test hash generation and consistency."""
        entry1 = KnowledgeEntry(
            title="Hash Test Entry",
            authors="Test",
            year="2024",
            venue="Test",
            url="https://same-url.com/test"
        )

        entry2 = KnowledgeEntry(
            title="Different Title",
            authors="Different",
            year="2025",
            venue="Different",
            url="https://same-url.com/test"  # Same URL
        )

        # Hashes from same URL should match
        assert entry1.entry_hash == entry2.entry_hash, \
            f"Entries with same URL should have same hash: {entry1.entry_hash} vs {entry2.entry_hash}"

        print(f"Hash consistency verified: {entry1.entry_hash}")

    def test_pipeline_integration(self):
        """Test full pipeline integration."""
        pipeline = KnowledgePipeline(self.temp_brain_path.name)

        # Run limited pipeline
        results = pipeline.run_pipeline(enable_crawling=False)

        assert 'processed' in results, "Results should include processed count"
        assert 'added' in results, "Results should include added count"
        assert isinstance(results['processed'], int), "Processed count should be integer"
        assert isinstance(results['added'], int), "Added count should be integer"

        print(f"Pipeline integration test completed: {results['added']} entries added")

    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite."""
        print("\n" + "="*60)
        print("KNOWLEDGE UPDATE PIPELINE TEST SUITE")
        print("="*60)

        try:
            temp_path = self.setup()

            # Run all tests
            self.run_test("ArXiv API Connectivity", self.test_arxiv_connectivity)
            self.run_test("Deduplication Logic", self.test_deduplication)
            self.run_test("Relevance Scoring", self.test_relevance_scoring)
            self.run_test("Evidence Grading", self.test_evidence_grading)
            self.run_test("Key Finding Extraction", self.test_key_finding_extraction)
            self.run_test("Hash Generation", self.test_hash_generation)
            self.run_test("Knowledge Base Append", self.test_knowledge_base_append)
            self.run_test("Pipeline Integration", self.test_pipeline_integration)

            # Compile results
            passed = sum(1 for r in self.test_results if r['passed'])
            total = len(self.test_results)

            print("\n" + "="*60)
            print(f"TEST RESULTS: {passed}/{total} passed")
            print("="*60)

            for result in self.test_results:
                status = "✓" if result['passed'] else "✗"
                print(f"{status} {result['name']}: {result['message']}")

            return {
                'total': total,
                'passed': passed,
                'failed': total - passed,
                'results': self.test_results,
                'success_rate': passed / total if total > 0 else 0
            }

        finally:
            self.teardown()

    def save_results(self, output_path: str = 'test_results.json'):
        """Save test results to JSON file."""
        results = self.run_all_tests()

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nTest results saved to {output_path}")
        return results


def main():
    """Main entry point for pipeline testing."""
    import argparse

    parser = argparse.ArgumentParser(description='Test knowledge update pipeline')
    parser.add_argument('--output', '-o', default='test_results.json', help='Output JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    tester = PipelineTester()
    results = tester.save_results(args.output)

    # Exit with appropriate code
    return 0 if results['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
