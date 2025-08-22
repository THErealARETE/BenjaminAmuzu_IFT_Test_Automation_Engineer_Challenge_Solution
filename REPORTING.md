# Waku Node Test Automation - Reporting Guide

## Overview

This framework provides comprehensive reporting capabilities for Waku node testing, including HTML reports, coverage analysis, and detailed logging.

## Reporting Features

### 1. HTML Test Reports
Generate professional HTML reports with detailed test results, metadata, and execution information.

```bash
# Generate HTML report
python run_tests.py --html

# Or directly with pytest
venv/bin/pytest --html=reports/report.html --self-contained-html
```

**Features:**
- Test execution timeline
- Pass/fail statistics
- Test duration analysis
- Error details and stack traces
- Metadata (Project, Framework, Test Type)
- Self-contained HTML (no external dependencies)

### 2. Code Coverage Reports
Analyze code coverage to identify untested areas and improve test quality.

```bash
# Generate coverage report
python run_tests.py --coverage

# Or directly with pytest
venv/bin/pytest --cov=tests --cov=utils --cov-report=html:reports/coverage --cov-report=term-missing
```

**Coverage Reports:**
- **HTML Coverage**: Interactive coverage report in `reports/coverage/index.html`
- **Terminal Output**: Missing lines and coverage percentages
- **XML Report**: For CI/CD integration (`reports/coverage.xml`)

### 3. Enhanced Logging
Structured logging with timestamps and log levels for better debugging.

**Log Levels:**
- `INFO`: Node readiness, peer connections, test status
- `DEBUG`: Detailed API calls and retry attempts
- `WARNING`: API failures and retry attempts
- `ERROR`: Test failures and timeout errors

**Example Log Output:**
```
2025-08-22 14:12:12 [    INFO] utils.waku_api: Waiting for node on port 21161 to become ready...
2025-08-22 14:12:15 [    INFO] utils.waku_api: Node on port 21161 is ready
2025-08-22 14:12:17 [    INFO] utils.waku_api: Verifying peer connection for 172.18.0.2 on port 21261
2025-08-22 14:12:32 [    INFO] utils.waku_api: Peer connection established for 172.18.0.2 on port 21261
```

### 4. Custom Test Reporter
Detailed test execution tracking with timing and status information.

**Features:**
- Test-by-test execution tracking
- Duration analysis
- Success rate calculation
- Detailed failure reporting
- Session summary

### 5. Parallel Test Execution
Run tests in parallel for faster execution.

```bash
# Run tests in parallel
python run_tests.py --parallel

# Or directly with pytest
venv/bin/pytest -n auto --dist=loadfile
```

## Report Types and Locations

### Generated Reports

| Report Type | Location | Description |
|-------------|----------|-------------|
| HTML Test Report | `reports/waku_test_report_YYYYMMDD_HHMMSS.html` | Main test execution report |
| Coverage HTML | `reports/coverage/index.html` | Interactive coverage analysis |
| Coverage XML | `reports/coverage.xml` | Machine-readable coverage data |
| Coverage Terminal | Console output | Missing lines and percentages |

### Report Contents

#### HTML Test Report
- **Summary**: Pass/fail counts, total duration, success rate
- **Test Details**: Individual test results with timing
- **Metadata**: Project information and test environment
- **Error Details**: Full stack traces for failed tests

#### Coverage Report
- **File Coverage**: Line-by-line coverage analysis
- **Missing Lines**: Specific lines not covered by tests
- **Coverage Percentage**: Overall and per-file coverage
- **Interactive Navigation**: Click to view source code

## Usage Examples

### Basic Test Execution
```bash
# Run all tests with basic output
python run_tests.py

# Run specific test suite
python run_tests.py --suite 1
python run_tests.py --suite 2
```

### Comprehensive Reporting
```bash
# Full reporting with HTML and coverage
python run_tests.py --html --coverage --verbose

# Parallel execution with reporting
python run_tests.py --parallel --html --coverage
```

### Debug Mode
```bash
# Debug mode with detailed logging
python run_tests.py --debug

# Verbose output with stack traces
python run_tests.py --verbose --debug
```

### Direct Pytest Commands
```bash
# HTML report only
venv/bin/pytest --html=reports/report.html --self-contained-html

# Coverage only
venv/bin/pytest --cov=tests --cov=utils --cov-report=html:reports/coverage

# Combined reporting
venv/bin/pytest --html=reports/report.html --cov=tests --cov=utils --cov-report=html:reports/coverage --cov-report=term-missing
```

## Configuration

### Pytest Configuration (`pytest.ini`)
```ini
[pytest]
markers =
    slow: marks tests as slow to run
    integration: marks tests as integration tests
    unit: marks tests as unit tests

addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings

log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(name)s: %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S
```

### Report Configuration (`utils/test_report_config.py`)
- Timestamped report files
- Configurable report locations
- Metadata customization
- Coverage report options

## Current Coverage Status

**Overall Coverage: 68%**

| Module | Coverage | Status |
|--------|----------|--------|
| `tests/` | 100% | ✅ Fully covered |
| `utils/config.py` | 100% | ✅ Fully covered |
| `utils/models.py` | 91% | ✅ Well covered |
| `utils/validators.py` | 88% | ✅ Well covered |
| `utils/waku_api.py` | 79% | ✅ Good coverage |
| `utils/test_helpers.py` | 79% | ✅ Good coverage |
| `utils/docker_manager.py` | 62% | ⚠️ Needs improvement |
| `utils/reporter.py` | 17% | ❌ Low coverage |
| `utils/test_report_config.py` | 0% | ❌ No coverage |

## Best Practices

### 1. Regular Coverage Analysis
- Run coverage reports regularly to identify gaps
- Aim for >80% coverage in critical modules
- Focus on business logic coverage

### 2. Report Management
- Archive old reports for historical analysis
- Use timestamped reports for version tracking
- Share reports with stakeholders

### 3. Logging Strategy
- Use appropriate log levels
- Include relevant context in log messages
- Monitor for performance issues

### 4. CI/CD Integration
- Include coverage thresholds in CI
- Generate reports in build artifacts
- Use XML reports for automated analysis

## Troubleshooting

### Common Issues

1. **Reports not generated**
   - Check if `reports/` directory exists
   - Verify pytest plugins are installed
   - Check file permissions

2. **Coverage not accurate**
   - Ensure virtual environment is activated
   - Check if coverage includes all relevant modules
   - Verify test execution paths

3. **Logging not visible**
   - Check log level configuration
   - Ensure `--verbose` or `--debug` flags are used
   - Verify pytest.ini configuration

### Performance Optimization

1. **Parallel Execution**
   - Use `--parallel` for faster execution
   - Monitor resource usage
   - Balance speed vs. stability

2. **Report Generation**
   - Generate reports only when needed
   - Use `--self-contained-html` for portability
   - Consider report size for CI/CD

## Future Enhancements

1. **Custom Report Templates**
   - Waku-specific report formatting
   - Node status visualization
   - Performance metrics

2. **Integration with External Tools**
   - SonarQube integration
   - Slack/Teams notifications
   - JIRA integration

3. **Advanced Analytics**
   - Test execution trends
   - Performance regression detection
   - Coverage trend analysis
