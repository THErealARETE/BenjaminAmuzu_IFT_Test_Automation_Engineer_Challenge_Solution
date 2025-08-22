import os
from datetime import datetime
from pathlib import Path


class TestReportConfig:
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.html_report_path = self.reports_dir / f"waku_test_report_{timestamp}.html"
        self.json_report_path = self.reports_dir / f"waku_test_results_{timestamp}.json"
        self.coverage_report_path = self.reports_dir / "coverage"
    
    def get_html_report_args(self):
        return [
            "--html", str(self.html_report_path),
            "--self-contained-html",
            "--metadata", "Project", "Waku Node Test Automation",
            "--metadata", "Framework", "pytest",
            "--metadata", "Test Type", "Integration Tests"
        ]
    
    def get_coverage_args(self):
        return [
            "--cov=tests",
            "--cov=utils",
            "--cov-report=html:" + str(self.coverage_report_path),
            "--cov-report=term-missing",
            "--cov-report=xml:" + str(self.reports_dir / "coverage.xml")
        ]
    
    def get_parallel_args(self, workers="auto"):
        return [
            "-n", workers,
            "--dist=loadfile"
        ]
    
    def get_verbose_args(self):
        return [
            "-v",
            "-s",
            "--tb=short"
        ]
    
    def get_debug_args(self):
        return [
            "-vv",
            "-s",
            "--tb=long",
            "--log-cli-level=DEBUG"
        ]
    
    def get_summary_args(self):
        return [
            "--durations=10",
            "--durations-min=1.0"
        ]


def get_report_config():
    return TestReportConfig()
