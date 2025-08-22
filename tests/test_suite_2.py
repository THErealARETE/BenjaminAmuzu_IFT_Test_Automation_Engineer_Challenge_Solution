import pytest
import json
import base64

from utils.config import CONTENT_TOPIC, MESSAGE_TIMEOUT, POLL_INTERVAL
from utils.test_helpers import wait_for_messages
from utils.validators import validate_waku_message

class TestInterNodeConnection:
    
    @pytest.mark.dependency(name="peer_connection")
    def test_01_verify_peer_connection(self, connected_nodes):
        node1_api, node2_api = connected_nodes
        
        peers = node2_api.get_peers()
        assert len(peers) > 0, "No peers found on node2"
        
        assert node2_api.has_peer(node1_api.node_id), "Node1 not found in node2's peers"
        
 

    @pytest.mark.dependency(depends=["peer_connection"])
    @pytest.mark.parametrize("message_text",["Test Message sending one one node and been received on another"])
    def test_02_verify_message_transmission_and_reception(self, connected_and_subscribed_nodes, message_text):
        node1_api, node2_api = connected_and_subscribed_nodes
        
        response = node1_api.publish_message(CONTENT_TOPIC, message_text)
        
        published_payload = base64.b64encode(message_text.encode('utf-8')).decode('utf-8')
        
        messages = wait_for_messages(
            lambda: node2_api.get_messages(CONTENT_TOPIC),
            expected_count=1,
            timeout=MESSAGE_TIMEOUT,
            poll_interval=POLL_INTERVAL
        )
        
        waku_message = validate_waku_message(
            messages[0],
            expected_payload=published_payload,
            expected_topic=CONTENT_TOPIC,
            expected_content=message_text
        )
        
        assert waku_message.version == 0
        
     