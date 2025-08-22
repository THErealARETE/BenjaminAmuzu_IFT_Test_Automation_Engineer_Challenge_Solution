import pytest
import base64
from utils.config import CONTENT_TOPIC, MESSAGE_TIMEOUT, POLL_INTERVAL
from utils.test_helpers import wait_for_specific_message
from utils.models import NodeInfo
from utils.validators import validate_waku_message

class TestBasicNodeOperation:
    
    def test_01_get_node_info(self, node1):
        node_info = node1.get_node_info()
        
        assert isinstance(node_info, NodeInfo), "Node info should be a validated NodeInfo instance"
        assert node_info.enrUri, "ENR URI should not be empty"
        assert node_info.enrUri.startswith("enr:"), "ENR URI should start with 'enr:'"
        assert node_info.listenAddresses, "Listen addresses should not be empty"
        assert len(node_info.enrUri) > 10, "ENR URI seems too short"
        assert len(node_info.listenAddresses) > 0, "At least one listen address should be present"

    def test_02_subscribe_to_topic(self, node1):
        response = node1.subscribe_to_topic(CONTENT_TOPIC)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.text == "OK", f"Expected 'OK' in body, got '{response.text}'"

    
    @pytest.mark.parametrize("message_text",["Test Message Publishing"])
    def test_03_publish_message(self, subscription_factory, node1, message_text):
        subscribed_node = subscription_factory(node1)
        
        response = subscribed_node.publish_message(CONTENT_TOPIC, message_text)

        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        assert response.text == "OK", f"Expected response text 'OK', got '{response.text}'"


    def test_04_confirm_message_publication(self, subscription_factory, node1, message_text):
        subscribed_node = subscription_factory(node1)
        
        response = subscribed_node.publish_message(CONTENT_TOPIC, message_text)
        
        published_payload = base64.b64encode(message_text.encode('utf-8')).decode('utf-8')
        
        found_message_data = wait_for_specific_message(
            lambda: subscribed_node.get_messages(CONTENT_TOPIC),
            lambda msg: msg.get("payload") == published_payload,
            timeout=MESSAGE_TIMEOUT, 
            poll_interval=POLL_INTERVAL  
        )

        waku_message = validate_waku_message(
            found_message_data,
            expected_payload=published_payload,
            expected_topic=CONTENT_TOPIC,
            expected_content=message_text
        )
        
        assert waku_message.version == 0
