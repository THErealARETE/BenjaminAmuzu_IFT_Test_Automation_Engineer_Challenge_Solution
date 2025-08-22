# IFT-Automation

A test automation framework for testing Waku node operations and inter-node communication.

## Overview

This project contains automated tests for Waku nodes, including:
- **Test Suite 1**: Basic single-node operations (publish/subscribe)
- **Test Suite 2**: Inter-node communication and message relay

## Project Structure

```
IFT-Automation/
├── tests/
│   ├── __init__.py          # Makes tests a Python package
│   ├── conftest.py          # Pytest fixtures (session-scoped resources)
│   ├── test_suite_1.py      # Basic node operations
│   └── test_suite_2.py      # Inter-node communication
├── utils/
│   ├── __init__.py          # Makes utils a Python package
│   ├── config.py            # Shared configuration constants
│   ├── docker_manager.py    # Docker container and network management
│   └── waku_api.py          # Waku API client and node manager
├── pytest.ini               # Pytest configuration
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Features

- **Clean Pytest Fixtures**: `conftest.py` focuses purely on pytest fixtures following best practices
- **Docker Management**: `utils/docker_manager.py` handles all Docker operations (containers, networks)
- **Clean API Interface**: `utils/waku_api.py` provides a clean interface for all Waku operations
- **Session-scoped Resources**: Nodes and networks are created once per test session for efficiency
- **Automatic Cleanup**: Resources are automatically cleaned up after tests complete
- **Separation of Concerns**: Clear separation between test infrastructure, Docker management, and API operations

## Prerequisites

- Python 3.9+
- Docker
- Waku node image (`wakuorg/nwaku:v0.24.0`)

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

### Run All Tests
```bash
pytest
```

### Run Specific Test Suite
```bash
# Run only basic node operations
pytest tests/test_suite_1.py

# Run only inter-node communication tests
pytest tests/test_suite_2.py
```

### Run with Markers
```bash
# Run only Docker-related tests
pytest -m docker

# Run only Waku-specific tests
pytest -m waku
```

### Run with Verbose Output
```bash
pytest -v
```

## Docker Management

The `utils/docker_manager.py` module handles all Docker operations:

### `DockerContainerManager`
Manages individual Docker container lifecycle:
- `start()` - Start container with proper configuration
- `stop()` - Stop and remove container
- `restart_with_bootstrap()` - Restart with bootstrap configuration (for node2)
- `get_logs()` - Retrieve container logs
- `is_running()` - Check container status

### `DockerNetworkManager`
Manages Docker network operations:
- `create()` - Create network with specified subnet and gateway
- `remove()` - Clean up network
- `connect_container()` - Connect container to network with specific IP
- `list_containers()` - List containers in network
- `get_network_info()` - Get detailed network information

### `DockerManager`
High-level coordinator for Docker operations:
- `setup_network()` - Set up the Docker network
- `create_node1()` / `create_node2()` - Create and start nodes
- `restart_node2_with_bootstrap()` - Restart node2 with bootstrap
- `cleanup_all()` - Clean up all resources

## API Client

The `utils/waku_api.py` module provides a clean interface for all Waku node operations:

### `WakuAPIClient`
Low-level client for direct REST API interactions:
- `get_node_info()` - Get node information and ENR URI
- `check_health()` - Check if node is healthy
- `subscribe_to_topic()` - Subscribe to content topics
- `publish_message()` - Publish messages
- `get_messages()` - Retrieve messages
- `get_peers()` - Get connected peers

### `WakuNodeManager`
High-level manager for common operations:
- `wait_for_ready()` - Wait for node to be ready
- `verify_message_received()` - Verify message delivery
- `verify_peer_connection()` - Verify peer connections

## Test Fixtures

The `conftest.py` file provides several key fixtures:

### `docker_network`
- **Scope**: Session
- **Purpose**: Creates and manages the Docker network for inter-node communication
- **Network**: `waku` with subnet `172.18.0.0/16`

### `node1`
- **Scope**: Session
- **Purpose**: Manages the first Waku node (port 21161)
- **IP**: `172.18.0.2`
- **Used by**: Both test suites

### `node2`
- **Scope**: Session
- **Purpose**: Manages the second Waku node (port 21261)
- **IP**: `172.18.0.3`
- **Used by**: Test suite 2 (inter-node communication)

### `shared_data`
- **Scope**: Session
- **Purpose**: Provides a dictionary for sharing data between tests
- **Usage**: Store ENR URIs, message payloads, etc.

## Test Suites

### Test Suite 1: Basic Node Operations
Tests basic publish/subscribe functionality on a single node:
1. Get node information and ENR URI (using /health endpoint)
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
- **Gateway**: `172.18.0.1`
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

## Contributing

When adding new test suites:
1. Use the existing fixtures from `conftest.py`
2. Follow the naming convention: `test_suite_N.py`
3. Add appropriate test markers
4. Ensure proper cleanup in fixtures

## License

This project is part of the IFT-Automation framework.