# utils/test_helpers.py
from pydantic import ValidationError
import base64
from utils.models import WakuMessage

def validate_waku_message(message_data, expected_payload=None, expected_topic=None, expected_content=None):
    """
    Validate a Waku message using Pydantic schema and optional content checks.
    
    Args:
        message_data: Raw message data (dict)
        expected_payload: Expected base64 payload (optional)
        expected_topic: Expected content topic (optional)
        expected_content: Expected decoded message content (optional)
    
    Returns:
        WakuMessage: The validated Pydantic model instance
    
    Raises:
        AssertionError: If any validation fails
        ValidationError: If schema validation fails
    """
    # Schema validation with Pydantic
    try:
        waku_message = WakuMessage(**message_data)
    except ValidationError as e:
        raise AssertionError(f"Schema validation failed for the message: {e}") from e
    
    # Optional field validations
    if expected_payload is not None:
        assert waku_message.payload == expected_payload, \
            f"Payload mismatch. Expected: {expected_payload}, Got: {waku_message.payload}"
    
    if expected_topic is not None:
        assert waku_message.contentTopic == expected_topic, \
            f"Content topic mismatch. Expected: {expected_topic}, Got: {waku_message.contentTopic}"
    
    if expected_content is not None:
        decoded_message = base64.b64decode(waku_message.payload).decode('utf-8')
        assert decoded_message == expected_content, \
            f"Message content mismatch. Expected: '{expected_content}', Got: '{decoded_message}'"
    
    return waku_message