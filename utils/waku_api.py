import requests
import base64
import time
import logging
from typing import Dict, List, Optional
from urllib.parse import quote

from utils.config import BASE_URL
from utils.models import NodeInfo
from utils.test_helpers import extract_peer_id, wait_for

logger = logging.getLogger(__name__)


class WakuNodeManager:
    
    def __init__(self, port: int):
        self.port = port
        self.base_url = f"http://{BASE_URL}:{port}".rstrip('/')
    
    def wait_for_ready(self, timeout: int = 30) -> bool:
        logger.info(f"Waiting for node on port {self.port} to become ready...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_health():
                logger.info(f"Node on port {self.port} is ready")
                return True
            time.sleep(2)
        
        logger.error(f"Node on port {self.port} failed to become ready within {timeout}s")
        raise TimeoutError(f"Node failed to become ready within {timeout}s")
    
    def get_node_info(self) -> NodeInfo:
        response = requests.get(f"{self.base_url}/debug/v1/info", timeout=10)
        response.raise_for_status()
        
        node_info_data = response.json()
        node_info = NodeInfo(**node_info_data)
        return node_info
    
    def get_enr_uri(self) -> str:
        node_info = self.get_node_info()
        return node_info.enrUri
    
    def check_health(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def subscribe_to_topic(self, content_topic: str):
        headers = {"accept": "text/plain", "content-type": "application/json"}
        payload = [content_topic]
        
        response = requests.post(
            f"{self.base_url}/relay/v1/auto/subscriptions",
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response
    
    def publish_message(self, content_topic: str, message_text: str):
        headers = {"content-type": "application/json"}
        payload_b64 = base64.b64encode(message_text.encode('utf-8')).decode('utf-8')
        
        payload = {
            "payload": payload_b64,
            "contentTopic": content_topic
        }
        
        response = requests.post(
            f"{self.base_url}/relay/v1/auto/messages",
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response
    
    def get_messages(self, content_topic: str) -> List[Dict]:
        encoded_content_topic = quote(content_topic, safe='')
        
        response = requests.get(
            f"{self.base_url}/relay/v1/auto/messages/{encoded_content_topic}",
            headers={"accept": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_peers(self) -> List[Dict]:
        response = requests.get(
            f"{self.base_url}/admin/v1/peers",
            headers={"accept": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_peer_ids(self) -> List[str]:
        peer_ids: List[str] = []
        for peer in self.get_peers():
            peer_id = extract_peer_id(peer.get("multiaddr", ""))
            if peer_id:
                peer_ids.append(peer_id)
        return peer_ids
    
    def has_peer(self, identifier: str) -> bool:
        peers = self.get_peers()
        for peer in peers:
            multiaddr = peer.get("multiaddr", "")
            if identifier in multiaddr:
                return True
            peer_id = extract_peer_id(multiaddr)
            if peer_id and peer_id == identifier:
                return True
        return False
    
    def verify_message_received(self, content_topic: str, expected_payload: str) -> bool:
        messages = self.get_messages(content_topic)
        
        if not messages:
            return False
        
        for message in messages:
            if message.get("payload") == expected_payload:
                return True
        
        return False
    
    def verify_peer_connection(self, expected_peer_ip: str, timeout: float = 100.0, poll_interval: float = 5.0) -> bool:
        logger.info(f"Verifying peer connection for {expected_peer_ip} on port {self.port}")
        
        def check_peer_connection():
            try:
                peers = self.get_peers()
                logger.debug(f"Found {len(peers)} peers")
                
                for peer in peers:
                    if expected_peer_ip in peer.get("multiaddr", ""):
                        for protocol in peer.get("protocols", []):
                            if (protocol.get("protocol") == "/vac/waku/relay/2.0.0" and 
                                protocol.get("connected") == True):
                                logger.info(f"Peer connection established for {expected_peer_ip} on port {self.port}")
                                return True
                
                logger.debug(f"Peer {expected_peer_ip} not found, retrying...")
                return False
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"API call failed: {e}")
                return False
        
        try:
            return wait_for(
                check_peer_connection,
                timeout=timeout,
                poll_interval=poll_interval,
                error_message=f"Failed to establish peer connection for {expected_peer_ip} on port {self.port} within {timeout}s"
            )
        except TimeoutError as e:
            logger.error(str(e))
            raise


class Node(WakuNodeManager):
    
    def __init__(self, container, docker_manager=None):
        self.container = container
        self.docker_manager = docker_manager
        
        super().__init__(container.port)
        
        self.port = container.port
        self.network_ip = container.network_ip
        self.name = container.name
        
        self._node_id: Optional[str] = None
    
    @property
    def node_id(self) -> Optional[str]:
        if self._node_id is not None:
            return self._node_id
        try:
            node_info = self.get_node_info()
            for addr in getattr(node_info, "listenAddresses", []):
                peer_id = extract_peer_id(addr)
                if peer_id:
                    self._node_id = peer_id
                    break
        except Exception:
            self._node_id = None
        return self._node_id
    
    def stop(self):
        self.container.stop() 