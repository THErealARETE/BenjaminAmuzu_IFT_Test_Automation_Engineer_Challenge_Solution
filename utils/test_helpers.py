import time
from typing import Callable, Any, Optional
from functools import wraps
from utils.config import MESSAGE_TIMEOUT, POLL_INTERVAL


def extract_peer_id(multiaddr: str) -> Optional[str]:
    try:
        if "/p2p/" in multiaddr:
            return multiaddr.split("/p2p/")[-1]
    except Exception:
        pass
    return None


def wait_for(
    condition_func: Callable[[], Any],
    timeout: float = MESSAGE_TIMEOUT,
    poll_interval: float = POLL_INTERVAL,
    error_message: Optional[str] = None
) -> Any:
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        result = condition_func()
        if result:
            return result
        
        time.sleep(poll_interval)
    
    if error_message is None:
        error_message = f"Condition not met within {timeout} seconds"
    
    raise TimeoutError(error_message)


def wait_for_messages(
    get_messages_func: Callable[[], list],
    expected_count: int = 1,
    timeout: float = MESSAGE_TIMEOUT,
    poll_interval: float = POLL_INTERVAL
) -> list:
    def check_messages():
        messages = get_messages_func()
        return messages if len(messages) >= expected_count else None
    
    return wait_for(
        check_messages,
        timeout=timeout,
        poll_interval=poll_interval,
        error_message=f"Expected at least {expected_count} message(s) within {timeout} seconds"
    )


def wait_for_specific_message(
    get_messages_func: Callable[[], list],
    message_filter: Callable[[dict], bool],
    timeout: float = MESSAGE_TIMEOUT,
    poll_interval: float = POLL_INTERVAL
) -> dict:
    def check_for_message():
        messages = get_messages_func()
        for message in messages:
            if message_filter(message):
                return message
        return None
    
    return wait_for(
        check_for_message,
        timeout=timeout,
        poll_interval=poll_interval,
        error_message=f"Expected message not found within {timeout} seconds"
    ) 