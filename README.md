# IFT-Automation

A test automation framework for testing Waku node operations and inter-node communication.

## Overview

This project contains automated tests for Waku nodes:
- **Test Suite 1**: Basic single-node operations (publish/subscribe)
- **Test Suite 2**: Inter-node communication and message relay

## Project Structure

```
IFT-Automation/
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_suite_1.py      # Basic node operations
│   └── test_suite_2.py      # Inter-node communication
├── utils/
│   ├── config.py            # Configuration constants
│   ├── docker_manager.py    # Docker container management
│   ├── waku_api.py          # Waku API client
│   └── ...                  # Other utility modules
├── pytest.ini               # Pytest configuration
├── requirements.txt          # Python dependencies
├── run_tests.py             # Test execution script
└── README.md                # This file
```

## Prerequisites

- Python 3.9+
- Docker (ensure the daemon is running, e.g by starting the Docker Desktop)
- Waku node image (`wakuorg/nwaku:v0.24.0`) (This will download at first connection)

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

### Basic Test Execution

#### Run All Tests
```bash
pytest
```

#### Run Specific Test Suite
```bash
# Run only basic node operations
pytest tests/test_suite_1.py

# Run only inter-node communication tests
pytest tests/test_suite_2.py
```

#### Run with Verbose Output
```bash
pytest -v
```

### Using the Test Runner Script

The `run_tests.py` script provides additional options:

```bash
# Run all tests
python run_tests.py

# Run specific test suite
python run_tests.py --suite 1
python run_tests.py --suite 2

# Generate HTML report
python run_tests.py --html

# Generate coverage report
python run_tests.py --coverage

# Full reporting with HTML and coverage
python run_tests.py --html --coverage --verbose
```

## Test Suites

### Test Suite 1: Basic Node Operations
Tests basic publish/subscribe functionality on a single node:
1. Get node information and ENR URI
2. Subscribe to a content topic
3. Publish a message
4. Confirm message publication

### Test Suite 2: Inter-Node Communication
Tests communication between two nodes:
1. Create Docker network
2. Start and configure both nodes
3. Establish peer connection
4. Subscribe node2 to topic
5. Publish message on node1
6. Confirm message relay to node2

## Configuration

### Port Configuration
- **Node1**: 21161 (REST), 21162 (TCP), 21163 (WebSocket), 21164 (Discv5), 21165
- **Node2**: 21261 (REST), 21262 (TCP), 21263 (WebSocket), 21264 (Discv5), 21265

### Network Configuration
- **Network Name**: `waku`
- **Subnet**: `172.18.0.0/16`
- **Node1 IP**: `172.18.0.2`
- **Node2 IP**: `172.18.0.3`

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Ensure no other services are using the required ports
   - Check for existing Docker containers

2. **Docker Network Issues**
   - Run `docker network prune` to clean up unused networks
   - Ensure Docker daemon is running

3. **Node Startup Failures**
   - Check Docker logs: `docker logs <container_name>`
   - Verify Waku image is available: `docker images | grep waku`

### Debug Mode
Run tests with increased verbosity:
```bash
pytest -v -s --tb=long
```