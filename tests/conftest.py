import pytest

from utils.docker_manager import DockerManager
from utils.waku_api import Node
from utils.config import CONTENT_TOPIC, NODE1_IP
from utils.reporter import WakuTestReporter


@pytest.fixture(scope="session")
def docker_manager():
    manager = DockerManager()
    manager.setup_network()
    
    yield manager
    
    manager.cleanup_all()


@pytest.fixture(scope="session")
def node1(docker_manager):
    container = docker_manager.create_node1()
    node = Node(container)
    node.wait_for_ready()
    
    yield node
    
    node.stop()


@pytest.fixture(scope="session")
def node2_with_bootstrap(docker_manager, node1):
    enr_uri = node1.get_enr_uri()
    
    container = docker_manager.create_node2_with_bootstrap(enr_uri)
    node = Node(container, docker_manager)
    node.wait_for_ready()
    
    node.verify_peer_connection(NODE1_IP)
    
    yield node
    
    node.stop()


@pytest.fixture(scope="function")
def subscription_factory():
    def _subscribe(node):
        node.subscribe_to_topic(CONTENT_TOPIC)
        return node

    return _subscribe


@pytest.fixture(scope="function")
def message_text():
    return "Testing confirmation on subscription and publishing"


@pytest.fixture(scope="session")
def connected_nodes(node1, node2_with_bootstrap):
    return (node1, node2_with_bootstrap)


@pytest.fixture(scope="function")
def connected_and_subscribed_nodes(connected_nodes, subscription_factory):
    node1, node2 = connected_nodes
    subscription_factory(node2)
    return (node1, node2)