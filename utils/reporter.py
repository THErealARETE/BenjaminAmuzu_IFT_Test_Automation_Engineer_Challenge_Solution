import pytest
import time
from typing import Dict, List, Optional
from datetime import datetime


class WakuTestReporter:
    def __init__(self):
        self.test_results = []
        self.node_status = {}
        self.start_time = None
        self.end_time = None
    
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item):
        test_name = item.name
        test_class = item.cls.__name__ if item.cls else "Unknown"
        
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_class}.{test_name}")
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            yield
            duration = time.time() - start_time
            status = "PASSED"
            error_msg = None
        except Exception as e:
            duration = time.time() - start_time
            status = "FAILED"
            error_msg = str(e)
        
        self.test_results.append({
            'test_name': test_name,
            'test_class': test_class,
            'status': status,
            'duration': duration,
            'error': error_msg,
            'timestamp': datetime.now()
        })
        
        print(f"\n📊 Test Result: {status}")
        print(f"⏱️  Duration: {duration:.2f}s")
        if error_msg:
            print(f"❌ Error: {error_msg}")
        print(f"{'='*60}")
    
    def pytest_sessionstart(self, session):
        self.start_time = time.time()
        print(f"\n🚀 Starting Waku Node Test Session")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Total Tests: {len(session.items)}")
    
    def pytest_sessionfinish(self, session, exitstatus):
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time
        
        print(f"\n{'='*80}")
        print(f"📋 WAKU NODE TEST SESSION SUMMARY")
        print(f"{'='*80}")
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASSED')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAILED')
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {len(self.test_results)}")
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        print(f"📈 Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAILED':
                    print(f"   • {result['test_class']}.{result['test_name']}")
                    print(f"     Error: {result['error']}")
        
        print(f"\n📊 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            print(f"   {status_icon} {result['test_class']}.{result['test_name']} ({result['duration']:.2f}s)")
        
        print(f"{'='*80}")
    
    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        if report.when == 'call' and report.failed:
            print(f"\n🔍 FAILURE DETAILS for {report.nodeid}:")
            if report.longrepr:
                print(report.longrepr)
