# Deployment Guide — Career Path Advisor

## Quick Start Deployment

### Prerequisites
- Python 3.8+ installed
- Claude Code environment configured
- Git for version control
- Internet connection (for initial setup)

### Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Knowledge Base Initialization

```bash
# Run initial knowledge crawl
python tools/knowledge_updater.py

# Verify knowledge base populated
head -n 20 SECOND-KNOWLEDGE-BRAIN.md
```

### Step 3: Testing Validation

```bash
# Run scenario tests
python tests/test_validator.py

# Run pipeline tests
python tools/pipeline_tester.py

# Verify all tests pass
# Expected: All scenarios PASS, 100% success rate
```

### Step 4: Skill Registration

1. Copy skill files to Claude Code skills directory
2. Restart Claude Code
3. Test skill invocation

## Production Deployment

### File Structure

Ensure the following structure is maintained:

```
career-path-advisor/
├── skills/
│   ├── main.md
│   ├── sub-profile-intake.md
│   ├── sub-framework-selector.md
│   ├── sub-scoring-engine.md
│   └── sub-improvement-roadmap.md
├── tools/
│   ├── knowledge_updater.py
│   └── pipeline_tester.py
├── tests/
│   ├── test-scenarios.md
│   └── test_validator.py
├── docs/
│   ├── calibration_notes.md
│   ├── cluster_integration.md
│   └── production_readiness.md
├── SECOND-KNOWLEDGE-BRAIN.md
├── PROJECT-detail.md
├── CLAUDE.md
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md
├── README.md
├── LICENSE
├── requirements.txt
└── DEPLOYMENT.md
```

### Configuration

#### Environment Variables (Optional)

```bash
# Optional: Set knowledge update schedule
export KNOWLEDGE_UPDATE_SCHEDULE="weekly"
export KNOWLEDGE_UPDATE_DAY="monday"
export KNOWLEDGE_UPDATE_TIME="02:00"

# Optional: Set logging level
export LOG_LEVEL="INFO"
export LOG_FILE="knowledge_updater.log"
```

#### Cron Configuration

```bash
# Add to crontab (crontab -e)
0 2 * * 1 cd /path/to/career-path-advisor && python tools/knowledge_updater.py >> logs/weekly_update.log 2>&1
```

### Performance Optimization

#### Database Optimization (if using persistent storage)

```python
# In knowledge_updater.py
# Adjust batch sizes and timeouts
ARXIV_BATCH_SIZE = 25  # Optimize based on network
REQUEST_TIMEOUT = 30   # Seconds
```

#### Memory Management

```python
# For large knowledge bases
# Process entries in batches
BATCH_SIZE = 100
MAX_MEMORY_USAGE = "2GB"
```

## Monitoring Setup

### Health Checks

Create `monitoring/health_check.py`:

```python
#!/usr/bin/env python3
"""Health check for career-path-advisor deployment"""

import os
import sys
from datetime import datetime, timedelta

def check_knowledge_base():
    """Check if knowledge base is recent enough"""
    kb_path = "SECOND-KNOWLEDGE-BRAIN.md"
    if not os.path.exists(kb_path):
        return False, "Knowledge base missing"

    # Check last modified time
    mtime = os.path.getmtime(kb_path)
    last_update = datetime.fromtimestamp(mtime)
    age = datetime.now() - last_update

    if age > timedelta(days=14):  # 2 weeks
        return False, f"Knowledge base stale ({age.days} days old)"

    return True, "Knowledge base fresh"

def check_skill_files():
    """Check if all skill files present"""
    required_files = [
        "skills/main.md",
        "skills/sub-profile-intake.md",
        "skills/sub-framework-selector.md",
        "skills/sub-scoring-engine.md",
        "skills/sub-improvement-roadmap.md"
    ]

    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        return False, f"Missing skill files: {missing}"

    return True, "All skill files present"

def main():
    """Run health checks"""
    checks = [
        check_knowledge_base(),
        check_skill_files()
    ]

    all_passed = all(result for result, _ in checks)

    for result, message in checks:
        status = "✓" if result else "✗"
        print(f"{status} {message}")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
```

### Logging Configuration

Ensure proper logging is configured in `knowledge_updater.py`:

```python
# Add to production deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/career-path-advisor/knowledge.log'),
        logging.StreamHandler()
    ]
)
```

## Rollback Procedures

### Quick Rollback

```bash
# Restore previous knowledge base
cp SECOND-KNOWLEDGE-BRAIN.md.backup SECOND-KNOWLEDGE-BRAIN.md

# Restart skill service
# (implementation depends on deployment)
```

### Full Rollback

```bash
# Restore entire previous version
git checkout [previous-tag]

# Reinitialize if needed
python tools/knowledge_updater.py --restore-backup
```

## Troubleshooting

### Common Issues

#### Issue: Knowledge Base Not Updating

**Symptoms**: Old data in SECOND-KNOWLEDGE-BRAIN.md

**Solutions**:
```bash
# Check network connectivity
curl -I https://export.arxiv.org/api/query

# Run manual update with verbose logging
python tools/knowledge_updater.py --verbose

# Check for errors in logs
tail -f knowledge_updater.log
```

#### Issue: Tests Failing

**Symptoms**: test_validator.py or pipeline_tester.py failures

**Solutions**:
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Run tests with verbose output
python tests/test_validator.py --verbose
```

#### Issue: Skill Not Invoking

**Symptoms**: Claude Code doesn't recognize the skill

**Solutions**:
```bash
# Verify skill files in correct location
ls -la skills/*.md

# Check file permissions
chmod 644 skills/*.md

# Restart Claude Code
# (implementation dependent)
```

## Security Considerations

### Input Validation

The skill includes comprehensive input validation:

- URL sanitization in knowledge pipeline
- File path validation
- Content length limits
- Character encoding checks

### Dependency Security

```bash
# Check for vulnerabilities
pip safety check

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Access Control

For production deployments, consider:

- API rate limiting
- User authentication
- Audit logging
- Input sanitization

## Scaling Considerations

### Horizontal Scaling

The skill is designed for horizontal scaling:

- Stateless operations
- No session dependencies
- Shared knowledge base
- Distributed crawling capability

### Performance Tuning

```python
# In knowledge_updater.py
# Adjust based on deployment constraints

MAX_CONCURRENT_REQUESTS = 5
CACHE_TTL = 3600  # seconds
BATCH_PROCESSING_SIZE = 50
```

## Backup Strategy

### Knowledge Base Backups

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
cp SECOND-KNOWLEDGE-BRAIN.md "backups/SECOND-KNOWLEDGE-BRAIN.md.$DATE"

# Keep last 30 days
find backups/ -name "SECOND-KNOWLEDGE-BRAIN.md.*" -mtime +30 -delete
```

### Configuration Backups

```bash
# Backup all configuration
tar czf config-backup-$(date +%Y%m%d).tar.gz \
    CLAUDE.md \
    PROJECT-detail.md \
    requirements.txt
```

## Upgrade Path

### Version Upgrades

```bash
# Backup current version
git stash
git tag backup-$(date +%Y%m%d)

# Pull new version
git fetch origin
git checkout [new-version-tag]

# Run upgrade tests
python tests/test_validator.py
python tools/pipeline_tester.py

# Restore if tests fail
git checkout backup-$(date +%Y%m%d)
```

### Migration Between Versions

See specific release notes for migration instructions. Generally:

1. Backup current deployment
2. Update codebase
3. Run migration scripts
4. Validate with test suite
5. Deploy to production

## Support and Maintenance

### Monitoring Dashboards

Key metrics to monitor:

- Knowledge base freshness
- Test pass rates
- Error rates
- Response times
- User satisfaction

### Maintenance Schedule

**Weekly**:
- Automated knowledge updates
- Error log review
- Performance metrics check

**Monthly**:
- Framework relevance review
- User feedback analysis
- Security updates

**Quarterly**:
- Comprehensive testing
- Performance optimization
- Documentation updates
- Dependency updates

### Contact and Support

For deployment issues:
- GitHub Issues: [repository-url]/issues
- Documentation: See docs/ folder
- Cluster Standards: docs/cluster_integration.md

---

**Deployment Version**: 1.0.0
**Last Updated**: 2026-06-22
**Status**: Production Ready
