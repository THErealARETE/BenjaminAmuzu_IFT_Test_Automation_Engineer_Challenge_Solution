#!/usr/bin/env python3
"""
Test Runner Script for IFT-Automation
Provides convenient access to common test execution patterns.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from utils.test_report_config import get_report_config


def run_command(cmd, description):
    """Run a command and handle errors gracefully"""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error: {e.stderr.strip()}")
        if e.stdout:
            print(f"Output: {e.stdout.strip()}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="IFT-Automation Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --suite 1          # Run test suite 1 only
  python run_tests.py --suite 2          # Run test suite 2 only
  python run_tests.py --markers waku     # Run only Waku tests
  python run_tests.py --parallel         # Run tests in parallel
  python run_tests.py --html             # Generate HTML report
  python run_tests.py --coverage         # Run with coverage
        """
    )
    
    parser.add_argument(
        "--suite", 
        type=int, 
        choices=[1, 2], 
        help="Run specific test suite (1 or 2)"
    )
    
    parser.add_argument(
        "--markers", 
        type=str, 
        help="Run tests with specific markers (e.g., 'waku', 'integration')"
    )
    
    parser.add_argument(
        "--parallel", 
        action="store_true", 
        help="Run tests in parallel using pytest-xdist"
    )
    
    parser.add_argument(
        "--html", 
        action="store_true", 
        help="Generate HTML test report"
    )
    
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run tests with coverage reporting"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Run with verbose output"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Run with debug output (shows print statements)"
    )
    
    parser.add_argument(
        "--cleanup", 
        action="store_true", 
        help="Clean up Docker resources before running tests"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("❌ Error: 'tests' directory not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("❌ Error: 'tests' directory not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Use virtual environment pytest
    venv_pytest = Path("venv/bin/pytest")
    if not venv_pytest.exists():
        print("❌ Error: Virtual environment not found. Please create it first:")
        print("   python -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Build pytest command
    cmd = [str(venv_pytest)]
    
    # Add test selection
    if args.suite:
        cmd.append(f"tests/test_suite_{args.suite}.py")
    elif args.markers:
        cmd.extend(["-m", args.markers])
    else:
        cmd.append("tests/")
    
    # Add options
    if args.verbose:
        cmd.append("-v")
    
    if args.debug:
        cmd.extend(["-s", "--tb=long"])
    
    if args.parallel:
        cmd.extend(["-n", "auto"])
    
    if args.html:
        report_config = get_report_config()
        cmd.extend(report_config.get_html_report_args())
    
    if args.coverage:
        report_config = get_report_config()
        cmd.extend(report_config.get_coverage_args())
    
    # Cleanup Docker resources if requested
    if args.cleanup:
        print("\n🧹 Cleaning up Docker resources...")
        cleanup_commands = [
            (["docker", "stop", "node1", "node2"], "Stopping containers"),
            (["docker", "rm", "node1", "node2"], "Removing containers"),
            (["docker", "network", "rm", "waku"], "Removing network")
        ]
        
        for cmd, desc in cleanup_commands:
            try:
                subprocess.run(cmd, capture_output=True)
                print(f"✅ {desc} completed")
            except:
                pass  # Ignore errors during cleanup
    
    # Run the tests
    print(f"\n🚀 Running tests with command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n❌ Some tests failed (exit code: {result.returncode})")
        
        # Show summary
        print("\n📊 Test Summary:")
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Exit Code: {result.returncode}")
        
        if args.html:
            print("   HTML Report: reports/report.html")
        
        if args.coverage:
            print("   Coverage Report: htmlcov/index.html")
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 