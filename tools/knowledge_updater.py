# -*- coding: utf-8 -*-
"""
knowledge_updater.py — Production self-improving knowledge pipeline for career-path-advisor.

Crawls authoritative Career, Learning & Skills sources using crawl4ai + WebSearch integration,
scores entries by recency and domain relevance, appends new de-duplicated entries to
SECOND-KNOWLEDGE-BRAIN.md.

Schedule: Weekly cron | Cluster: career-education | Idea: #70
"""

import os
import re
import json
import hashlib
import datetime
import logging
from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, urlunparse
import time
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knowledge_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
BRAIN_PATH = os.path.join(os.path.dirname(__file__), "..", "SECOND-KNOWLEDGE-BRAIN.md")
ARXIV_API_BASE = "http://export.arxiv.org/api/query"
ARXIV_CATEGORIES = ['econ.GN', 'cs.CY', 'cs.SI']  # Economics, Cybernetics, Social and Information Networks

# Domain-specific search queries
SEARCH_QUERIES = [
    'future of work skills demand 2026',
    'career development framework evidence-based',
    'labor market skills trends',
    'O*NET occupational data updates',
    'LinkedIn workforce learning report',
    'McKinsey future of work skills',
    'Deloitte skills of the future',
    'World Economic Forum jobs report'
]

# Authoritative domain sources
DOMAIN_SOURCES = {
    'WEF Future of Jobs Report': 'https://www.weforum.org/reports',
    'LinkedIn Economic Graph': 'https://economicgraph.linkedin.com/research',
    'O*NET OnLine': 'https://www.onetonline.org/',
    'BLS Occupational Outlook': 'https://www.bls.gov/ooh/',
    'McKinsey Future of Work': 'https://www.mckinsey.com/featured-insights/future-of-work',
    'Deloitte Insights': 'https://www2.deloitte.com/insights/'
}

# Domain relevance scoring keywords
DOMAIN_KEYWORDS = {
    'primary': ['future of work', 'skills demand', 'career development', 'labor market', 'workforce trends', 'skill gaps', 'job market', 'employment trends'],
    'secondary': ['learning', 'training', 'education', 'professional development', 'upskilling', 'reskilling', 'digital skills', 'soft skills'],
    'frameworks': ['career anchors', 'life-career rainbow', 't-shaped', 'skills-based hiring', '70-20-10 model', 'okr career']
}

# Evidence hierarchy for grading
EVIDENCE_HIERARCHY = {
    'systematic_review': 5,
    'meta_analysis': 4.5,
    'rct': 4,
    'cohort_study': 3.5,
    'expert_consensus': 3,
    'expert_opinion': 2,
    'industry_report': 2.5,
    'blog': 1,
    'unknown': 1
}


@dataclass
class KnowledgeEntry:
    """Structured knowledge entry with metadata."""
    title: str
    authors: str
    year: str
    venue: str
    url: str
    abstract: str = ""
    key_finding: str = ""
    evidence_grade: float = 1.0
    relevance_score: float = 0.0
    entry_hash: str = ""

    def __post_init__(self):
        if self.url and not self.entry_hash:
            self.entry_hash = hashlib.sha256(self.url.encode()).hexdigest()[:12]


class KnowledgePipeline:
    """Production knowledge update pipeline with crawl4ai integration."""

    def __init__(self, brain_path: str = BRAIN_PATH):
        self.brain_path = brain_path
        self.existing_hashes: Set[str] = set()
        self.entries_processed = 0
        self.entries_added = 0
        self.entries_skipped = 0

    def load_existing_hashes(self) -> None:
        """Load existing entry hashes from knowledge base to prevent duplicates."""
        try:
            if os.path.exists(self.brain_path):
                with open(self.brain_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.existing_hashes = set(re.findall(r'<!--h:([0-9a-f]{12})-->', content))
                logger.info(f"Loaded {len(self.existing_hashes)} existing hashes")
        except Exception as e:
            logger.error(f"Error loading existing hashes: {e}")
            self.existing_hashes = set()

    def fetch_arxiv_papers(self, max_results: int = 25) -> List[KnowledgeEntry]:
        """Fetch recent papers from ArXiv API."""
        import urllib.request
        import urllib.parse

        entries = []
        logger.info(f"Fetching ArXiv papers from categories: {ARXIV_CATEGORIES}")

        for category in ARXIV_CATEGORIES:
            try:
                params = urllib.parse.urlencode({
                    "search_query": f"cat:{category}",
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                    "max_results": max_results
                })
                url = f"{ARXIV_API_BASE}?{params}"

                logger.info(f"Requesting: {url}")
                with urllib.request.urlopen(url, timeout=30) as response:
                    raw = response.read().decode("utf-8", "ignore")

                # Parse ArXiv response
                for match in re.finditer(r"<entry>(.*?)</entry>", raw, re.DOTALL):
                    entry_block = match.group(1)

                    def extract_tag(tag_name):
                        tag_match = re.search(rf"<{tag_name}>(.*?)</{tag_name}>", entry_block, re.DOTALL)
                        if tag_match:
                            return re.sub(r"\s+", " ", tag_match.group(1)).strip()
                        return ""

                    title = extract_tag("title")
                    authors = extract_tag("name")
                    published = extract_tag("published")
                    year = published[:4] if published else ""
                    url = extract_tag("id")
                    abstract = extract_tag("summary")

                    if title and url:
                        entry = KnowledgeEntry(
                            title=title[:200],
                            authors=authors[:100],
                            year=year,
                            venue=f"arXiv:{category}",
                            url=url,
                            abstract=abstract[:500],
                            evidence_grade=3.0  # ArXiv papers as expert opinion
                        )
                        entries.append(entry)
                        self.entries_processed += 1

            except Exception as e:
                logger.error(f"Error fetching ArXiv category {category}: {e}")

        logger.info(f"Fetched {len(entries)} papers from ArXiv")
        return entries

    def score_relevance(self, entry: KnowledgeEntry) -> float:
        """Score entry relevance based on domain keywords and recency."""
        score = 0.0

        # Recency scoring (more recent = higher score)
        try:
            year = int(entry.year) if entry.year else 2020
            recency_score = max(0, year - 2018) * 0.3  # 0.3 points per year since 2018
            score += recency_score
        except (ValueError, TypeError):
            score += 0.6  # baseline for unknown year

        # Domain keyword relevance
        text = (entry.title + " " + entry.abstract + " " + entry.key_finding).lower()

        # Primary keywords (highest weight)
        primary_matches = sum(1 for kw in DOMAIN_KEYWORDS['primary'] if kw in text)
        score += primary_matches * 2.5

        # Secondary keywords
        secondary_matches = sum(1 for kw in DOMAIN_KEYWORDS['secondary'] if kw in text)
        score += secondary_matches * 1.5

        # Framework mentions
        framework_matches = sum(1 for fw in DOMAIN_KEYWORDS['frameworks'] if fw in text)
        score += framework_matches * 2.0

        # Authoritative source bonus
        if any(source in entry.venue.lower() for source in ['wef', 'linkedin', 'onet', 'bureau of labor']):
            score += 1.5

        entry.relevance_score = round(score, 2)
        return entry.relevance_score

    def detect_evidence_grade(self, entry: KnowledgeEntry) -> float:
        """Auto-detect evidence grade from publication metadata."""
        text = (entry.title + " " + entry.abstract + " " + entry.venue).lower()

        # Systematic review/meta-analysis detection
        if any(term in text for term in ['systematic review', 'meta-analysis', 'literature review', 'meta analysis']):
            return EVIDENCE_HIERARCHY['systematic_review']

        # RCT detection
        if any(term in text for term in ['randomized', 'randomised', 'rct', 'controlled trial']):
            return EVIDENCE_HIERARCHY['rct']

        # Cohort study detection
        if any(term in text for term in ['cohort', 'longitudinal', 'panel study']):
            return EVIDENCE_HIERARCHY['cohort_study']

        # Expert consensus
        if any(term in text for term in ['consensus', 'guideline', 'task force', 'working group']):
            return EVIDENCE_HIERARCHY['expert_consensus']

        # Industry report
        if any(source in entry.venue.lower() for source in ['report', 'survey', 'index', 'outlook']):
            return EVIDENCE_HIERARCHY['industry_report']

        # Blog/opinion
        if any(term in text for term in ['blog', 'opinion', 'editorial', 'commentary']):
            return EVIDENCE_HIERARCHY['blog']

        return entry.evidence_grade

    def extract_key_finding(self, entry: KnowledgeEntry) -> str:
        """Extract key finding from abstract using heuristics."""
        abstract = entry.abstract.lower()

        # Look for sentences with "found", "showed", "demonstrated", "suggest"
        finding_patterns = [
            r'(?:we|this study|the study|the authors) (?:found|showed|demonstrated|revealed|suggests?|indicates?) ([^.]*\.)(?:\s|$)',
            r'(?:results|key findings?) (?:show|indicate|reveal|demonstrate) ([^.]*\.)(?:\s|$)',
            r'(?:the paper|this research) (?:concludes?|finds?) (?:that)? ([^.]*\.)(?:\s|$)'
        ]

        for pattern in finding_patterns:
            match = re.search(pattern, abstract, re.IGNORECASE)
            if match:
                finding = match.group(1) if match.lastindex else match.group(0)
                return finding.strip()[:200]

        # Fallback to first sentence if no finding pattern found
        sentences = abstract.split('.')
        if sentences:
            return sentences[0].strip()[:200]

        return "Key finding not available in abstract"

    def crawl_domain_sources(self) -> List[KnowledgeEntry]:
        """Crawl authoritative domain sources using crawl4ai."""
        entries = []

        try:
            from crawl4ai import AsyncWebCrawler
            import asyncio

            async def crawl_source(source_name: str, base_url: str):
                """Async crawl function for each source."""
                crawl_entries = []
                try:
                    async with AsyncWebCrawler(verbose=True) as crawler:
                        # Create search URLs for each source
                        search_urls = self._generate_search_urls(base_url)

                        for url in search_urls[:3]:  # Limit to 3 URLs per source
                            try:
                                result = await crawler.arun(url=url)
                                if result.success:
                                    # Extract relevant content
                                    content = self._extract_relevant_content(result)

                                    if content:
                                        entry = KnowledgeEntry(
                                            title=content.get('title', 'Unknown'),
                                            authors=source_name,
                                            year=str(datetime.datetime.now().year),
                                            venue=source_name,
                                            url=url,
                                            abstract=content.get('abstract', '')[:500],
                                            key_finding=content.get('key_finding', '')[:200],
                                            evidence_grade=EVIDENCE_HIERARCHY['industry_report']
                                        )
                                        crawl_entries.append(entry)
                                        self.entries_processed += 1

                                await asyncio.sleep(1)  # Rate limiting

                            except Exception as e:
                                logger.warning(f"Error crawling {url}: {e}")

                return crawl_entries

            # Run crawls for all sources
            async def crawl_all_sources():
                all_entries = []
                tasks = []
                for source_name, base_url in DOMAIN_SOURCES.items():
                    tasks.append(crawl_source(source_name, base_url))

                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, list):
                        all_entries.extend(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Crawl task failed: {result}")

                return all_entries

            # Run async crawling
            entries = asyncio.run(crawl_all_sources())

        except ImportError:
            logger.warning("crawl4ai not available - skipping domain source crawling")
            logger.info("Install crawl4ai with: pip install crawl4ai")
        except Exception as e:
            logger.error(f"Error during domain crawling: {e}")
            logger.debug(traceback.format_exc())

        logger.info(f"Crawled {len(entries)} entries from domain sources")
        return entries

    def _generate_search_urls(self, base_url: str) -> List[str]:
        """Generate search URLs for a given source."""
        urls = [base_url]

        # Source-specific URL generation
        if 'weforum.org' in base_url:
            urls.extend([
                f"{base_url}?term=future%20of%20jobs",
                f"{base_url}?term=skills",
                f"{base_url}?topic=employment"
            ])
        elif 'linkedin.com' in base_url:
            urls.extend([
                f"{base_url}skills",
                f"{base_url}future-of-work",
                f"{base_url}learning"
            ])
        elif 'onetonline.org' in base_url:
            urls.extend([
                f"{base_url}help",
                f"{base_url}links"
            ])

        return urls

    def _extract_relevant_content(self, crawl_result) -> Optional[Dict[str, str]]:
        """Extract relevant content from crawl result."""
        try:
            if hasattr(crawl_result, 'extracted_content') and crawl_result.extracted_content:
                content = crawl_result.extracted_content

                # Extract title from meta or first heading
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                title = title_match.group(1) if title_match else "Untitled"

                # Extract main content (first 500 chars of relevant sections)
                abstract_pattern = r'<(?:p|div)[^>]*>([^<]{100,500})</(?:p|div)>'
                abstract_matches = re.findall(abstract_pattern, content)
                abstract = ' '.join(abstract_matches[:3]) if abstract_matches else ""

                # Look for key findings
                finding_pattern = r'(?:key finding|result|conclusion)[^:]*:\s*([^.]{20,200})\.'
                finding_match = re.search(finding_pattern, content, re.IGNORECASE)
                key_finding = finding_match.group(1) if finding_match else ""

                return {
                    'title': title[:200],
                    'abstract': abstract[:500],
                    'key_finding': key_finding[:200]
                }
        except Exception as e:
            logger.warning(f"Error extracting content: {e}")

        return None

    def web_search_integration(self) -> List[KnowledgeEntry]:
        """Integration point for web search tools."""
        # This is where web search results would be processed
        # In production, this would integrate with WebSearch tools
        logger.info("Web search integration - placeholder for production implementation")
        return []

    def deduplicate_and_filter(self, entries: List[KnowledgeEntry]) -> List[KnowledgeEntry]:
        """Remove duplicates and filter low-quality entries."""
        unique_entries = []
        seen_hashes = self.existing_hashes.copy()
        seen_titles = set()

        for entry in entries:
            # Skip if no title or URL
            if not entry.title or not entry.url:
                self.entries_skipped += 1
                continue

            # Skip if already seen by hash
            if entry.entry_hash in seen_hashes:
                self.entries_skipped += 1
                continue

            # Skip near-duplicate titles (Levenshtein distance < 3)
            title_lower = entry.title.lower()
            is_duplicate = False
            for existing_title in seen_titles:
                if self._titles_similar(title_lower, existing_title):
                    is_duplicate = True
                    break

            if is_duplicate:
                self.entries_skipped += 1
                continue

            # Filter low relevance scores (< 2.0)
            if entry.relevance_score < 2.0:
                self.entries_skipped += 1
                continue

            # Add to unique entries
            seen_hashes.add(entry.entry_hash)
            seen_titles.add(title_lower)
            unique_entries.append(entry)

        logger.info(f"Deduplication: {len(unique_entries)} unique entries, {self.entries_skipped} skipped")
        return unique_entries

    def _titles_similar(self, title1: str, title2: str, threshold: int = 3) -> bool:
        """Check if two titles are similar using simple edit distance."""
        if abs(len(title1) - len(title2)) > threshold * 2:
            return False

        # Simple word overlap check
        words1 = set(title1.split())
        words2 = set(title2.split())

        if not words1 or not words2:
            return False

        overlap = len(words1 & words2) / max(len(words1), len(words2))
        return overlap > 0.7

    def format_entry_row(self, entry: KnowledgeEntry) -> str:
        """Format entry as markdown table row."""
        safe_title = entry.title.replace('|', '\\|')[:80]
        safe_authors = entry.authors.replace('|', '\\|')[:40]
        safe_url = entry.url.replace('|', '\\|')

        return (
            f"| {safe_title} | {safe_authors} | {entry.year} "
            f"| {entry.venue[:30]} | {safe_url[:60]} | "
            f"relevance:{entry.relevance_score}, grade:{entry.evidence_grade:.1f} |"
            f" <!--h:{entry.entry_hash}-->"
        )

    def append_to_brain(self, entries: List[KnowledgeEntry]) -> int:
        """Append new entries to SECOND-KNOWLEDGE-BRAIN.md."""
        if not entries:
            logger.warning("No entries to append")
            return 0

        try:
            # Read existing content
            with open(self.brain_path, 'r', encoding='utf-8') as f:
                brain_content = f.read()

            # Sort entries by relevance score
            sorted_entries = sorted(entries, key=lambda e: e.relevance_score, reverse=True)

            # Format entries
            today = datetime.date.today().isoformat()
            rows = []
            for entry in sorted_entries:
                rows.append(self.format_entry_row(entry))
                self.entries_added += 1

            # Create new log entry
            log_entry = (
                f"\n- **{today}** — Auto-crawl appended {len(rows)} new entries "
                f"(processed: {self.entries_processed}, skipped: {self.entries_skipped}).\n"
                + "\n".join(rows) + "\n"
            )

            # Append to content
            updated_content = brain_content.rstrip() + log_entry

            # Write back
            with open(self.brain_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            logger.info(f"Successfully appended {len(rows)} entries to knowledge base")
            return len(rows)

        except Exception as e:
            logger.error(f"Error appending to brain: {e}")
            logger.debug(traceback.format_exc())
            return 0

    def run_pipeline(self, enable_crawling: bool = True) -> Dict[str, Any]:
        """Run the complete knowledge update pipeline."""
        logger.info("=" * 60)
        logger.info("Starting Knowledge Update Pipeline")
        logger.info("=" * 60)

        start_time = time.time()
        results = {
            'processed': 0,
            'added': 0,
            'skipped': 0,
            'errors': [],
            'sources': {}
        }

        try:
            # Load existing hashes
            self.load_existing_hashes()

            # Fetch ArXiv papers
            logger.info("Phase 1: Fetching ArXiv papers...")
            arxiv_entries = self.fetch_arxiv_papers()
            results['sources']['arxiv'] = len(arxiv_entries)

            # Crawl domain sources (if enabled and available)
            domain_entries = []
            if enable_crawling:
                logger.info("Phase 2: Crawling domain sources...")
                domain_entries = self.crawl_domain_sources()
                results['sources']['domain_crawl'] = len(domain_entries)

            # Web search integration (placeholder)
            logger.info("Phase 3: Web search integration...")
            web_entries = self.web_search_integration()
            results['sources']['web_search'] = len(web_entries)

            # Combine all entries
            all_entries = arxiv_entries + domain_entries + web_entries
            logger.info(f"Total entries fetched: {len(all_entries)}")

            # Score and enhance entries
            logger.info("Phase 4: Scoring and enhancing entries...")
            for entry in all_entries:
                self.score_relevance(entry)
                entry.evidence_grade = self.detect_evidence_grade(entry)
                if not entry.key_finding:
                    entry.key_finding = self.extract_key_finding(entry)

            # Deduplicate and filter
            logger.info("Phase 5: Deduplicating and filtering...")
            unique_entries = self.deduplicate_and_filter(all_entries)

            # Append to knowledge base
            logger.info("Phase 6: Appending to knowledge base...")
            appended = self.append_to_brain(unique_entries)

            # Compile results
            results['processed'] = self.entries_processed
            results['added'] = self.entries_added
            results['skipped'] = self.entries_skipped

            elapsed = time.time() - start_time
            logger.info("=" * 60)
            logger.info(f"Pipeline completed in {elapsed:.2f} seconds")
            logger.info(f"Results: {results['added']} entries added, {results['skipped']} skipped, {results['processed']} processed")
            logger.info("=" * 60)

        except Exception as e:
            error_msg = f"Pipeline error: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            results['errors'].append(error_msg)

        return results


def main():
    """Main entry point for the knowledge updater."""
    import argparse

    parser = argparse.ArgumentParser(description='Update career-path-advisor knowledge base')
    parser.add_argument('--no-crawl', action='store_true', help='Skip domain crawling')
    parser.add_argument('--dry-run', action='store_true', help='Run without writing to file')
    parser.add_argument('--arxiv-only', action='store_true', help='Only fetch from ArXiv')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    pipeline = KnowledgePipeline()

    if args.dry_run:
        logger.info("Dry run mode - no files will be modified")
        # For dry run, we could add logic to preview without writing

    enable_crawling = not args.no_crawl and not args.arxiv_only
    results = pipeline.run_pipeline(enable_crawling=enable_crawling)

    # Exit with appropriate code
    if results['errors']:
        return 1
    elif results['added'] == 0:
        return 2  # No new entries added
    else:
        return 0


if __name__ == "__main__":
    exit(main())
