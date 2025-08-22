"""
Docker management utilities for IFT-Automation tests.
This module handles all Docker operations including containers, networks, and commands.
"""

import subprocess
import time
from typing import Optional, List, Dict, Any
from utils.config import NODE1_PORT, NODE2_PORT, NODE1_IP, NODE2_IP, NETWORK_NAME


class DockerContainerManager:
    """Manages Docker container lifecycle and operations"""
    
    def __init__(self, name: str, port: int, network_ip: str = None):
        self.name = name
        self.port = port
        self.network_ip = network_ip
        self.container_id = None
    
    def start(self, network_name: str = None) -> str:
        """Start the Waku node container"""
        try:
            cmd = [
                "docker", "run", "--name", self.name, "-d",
                "-p", f"{self.port}:21161"
            ]
            
            # Add network configuration if specified
            if network_name:
                cmd.extend(["--network", network_name])
                if self.network_ip:
                    cmd.extend(["--ip", self.network_ip])
            
            # Add all the standard ports
            cmd.extend([
                "-p", f"{self.port + 1}:21162",  # TCP port
                "-p", f"{self.port + 2}:21163",  # WebSocket port
                "-p", f"{self.port + 3}:21164",  # Discv5 UDP port
                "-p", f"{self.port + 4}:21165",  # Additional port
            ])
            
            # Add Waku image and configuration
            cmd.extend([
                "wakuorg/nwaku:v0.24.0",
                "--listen-address=0.0.0.0",
                "--rest=true",
                "--rest-admin=true",
                "--websocket-support=true",
                "--log-level=TRACE",
                "--rest-relay-cache-capacity=100",
                "--websocket-port=21163",
                "--rest-port=21161",
                "--tcp-port=21162",
                "--discv5-udp-port=21164",
                "--rest-address=0.0.0.0",
                "--peer-exchange=true",
                "--discv5-discovery=true",
                "--relay=true"
            ])
            
            # Add NAT configuration if network IP is specified
            if self.network_ip:
                cmd.append(f"--nat=extip:{self.network_ip}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.container_id = result.stdout.strip()
            
            print(f"Started {self.name} with container ID: {self.container_id}")
            return self.container_id
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to start {self.name}: {e.stderr}")
    
    def start_with_bootstrap(self, bootstrap_enr: str, network_name: str = "waku") -> str:
        """Start the Waku node container with bootstrap configuration from the start"""
        try:
            cmd = [
                "docker", "run", "--name", self.name, "-d",
                "--network", network_name,
                "--ip", self.network_ip,
                "-p", f"{self.port}:21161",
                "-p", f"{self.port + 1}:21162",
                "-p", f"{self.port + 2}:21163",
                "-p", f"{self.port + 3}:21164",
                "-p", f"{self.port + 4}:21165",
                "wakuorg/nwaku:v0.24.0",
                "--listen-address=0.0.0.0",
                "--rest=true",
                "--rest-admin=true",
                "--websocket-support=true",
                "--log-level=TRACE",
                "--rest-relay-cache-capacity=100",
                "--websocket-port=21163",
                "--rest-port=21161",
                "--tcp-port=21162",
                "--discv5-udp-port=21164",
                "--rest-address=0.0.0.0",
                f"--nat=extip:{self.network_ip}",
                "--peer-exchange=true",
                "--discv5-discovery=true",
                "--relay=true",
                f"--discv5-bootstrap-node={bootstrap_enr}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.container_id = result.stdout.strip()
            
            print(f"Started {self.name} with bootstrap configuration. Container ID: {self.container_id}")
            return self.container_id
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to start {self.name} with bootstrap: {e.stderr}")
    
    def stop(self):
        """Stop and remove the container"""
        try:
            subprocess.run(["docker", "stop", self.name], capture_output=True, check=True)
            subprocess.run(["docker", "rm", self.name], capture_output=True, check=True)
            print(f"Stopped and removed {self.name}")
        except subprocess.CalledProcessError:
            # Container might not exist, which is fine
            pass
    
    def restart_with_bootstrap(self, bootstrap_enr: str, network_name: str = "waku") -> str:
        """Restart container with bootstrap configuration (used for node2)"""
        # Stop current container
        self.stop()
        
        # Start with bootstrap configuration
        cmd = [
            "docker", "run", "--name", self.name, "-d",
            "--network", network_name,
            "--ip", self.network_ip,
            "-p", f"{self.port}:21161",
            "-p", f"{self.port + 1}:21162",
            "-p", f"{self.port + 2}:21163",
            "-p", f"{self.port + 3}:21164",
            "-p", f"{self.port + 4}:21165",
            "wakuorg/nwaku:v0.24.0",
            "--listen-address=0.0.0.0",
            "--rest=true",
            "--rest-admin=true",
            "--websocket-support=true",
            "--log-level=TRACE",
            "--rest-relay-cache-capacity=100",
            "--websocket-port=21163",
            "--rest-port=21161",
            "--tcp-port=21162",
            "--discv5-udp-port=21164",
            "--rest-address=0.0.0.0",
            "--nat=extip:172.18.0.3",
            "--peer-exchange=true",
            "--discv5-discovery=true",
            "--relay=true",
            f"--discv5-bootstrap-node={bootstrap_enr}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        container_id = result.stdout.strip()
        self.container_id = container_id
        
        print(f"{self.name} restarted with bootstrap configuration. Container ID: {container_id}")
        return container_id
    
    def get_logs(self, tail: int = 50) -> str:
        """Get container logs"""
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(tail), self.name],
                capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return "No logs available"
    
    def is_running(self) -> bool:
        """Check if container is running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.name}", "--format", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            return self.name in result.stdout
        except subprocess.CalledProcessError:
            return False


class DockerNetworkManager:
    """Manages Docker network for inter-node communication"""
    
    def __init__(self, name: str = "waku", subnet: str = "172.18.0.0/16", gateway: str = "172.18.0.1"):
        self.name = name
        self.subnet = subnet
        self.gateway = gateway
    
    def create(self):
        """Create the Docker network"""
        try:
            subprocess.run([
                "docker", "network", "create",
                "--driver", "bridge",
                "--subnet", self.subnet,
                "--gateway", self.gateway,
                self.name
            ], capture_output=True, check=True)
            print(f"Created Docker network: {self.name}")
        except subprocess.CalledProcessError as e:
            if "already exists" in e.stderr.decode:
                print(f"Network {self.name} already exists")
            else:
                raise RuntimeError(f"Failed to create Docker network: {e.stderr}")
    
    def remove(self):
        """Remove the Docker network"""
        try:
            subprocess.run(["docker", "network", "rm", self.name], capture_output=True, check=True)
            print(f"Removed Docker network: {self.name}")
        except subprocess.CalledProcessError:
            # Network might not exist, which is fine
            pass
    
    def connect_container(self, container_name: str, ip: str):
        """Connect a container to the network with a specific IP"""
        try:
            result = subprocess.run([
                "docker", "network", "connect", 
                "--ip", ip, 
                self.name, 
                container_name
            ], capture_output=True, text=True, check=True)
            
            print(f"{container_name} connected to network {self.name} with IP {ip}")
            return True
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to connect {container_name} to network: {e.stderr}")
    
    def list_containers(self) -> List[str]:
        """List containers connected to this network"""
        try:
            result = subprocess.run([
                "docker", "network", "inspect", self.name, "--format", "{{range .Containers}}{{.Name}} {{end}}"
            ], capture_output=True, text=True, check=True)
            return result.stdout.strip().split() if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            return []
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get detailed network information"""
        try:
            result = subprocess.run([
                "docker", "network", "inspect", self.name
            ], capture_output=True, text=True, check=True)
            
            import json
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return {}


class DockerManager:
    """High-level Docker manager that coordinates containers and networks"""
    
    def __init__(self):
        self.network_manager = DockerNetworkManager(NETWORK_NAME)
        self.containers = {}
    
    def setup_network(self):
        """Set up the Docker network"""
        self.network_manager.create()
    
    def cleanup_network(self):
        """Clean up the Docker network"""
        self.network_manager.remove()
    
    def create_node1(self) -> DockerContainerManager:
        """Create and start node1"""
        node1 = DockerContainerManager("node1", NODE1_PORT, NODE1_IP)
        node1.start(NETWORK_NAME)
        self.containers["node1"] = node1
        return node1
    
    def create_node2(self) -> DockerContainerManager:
        """Create and start node2"""
        node2 = DockerContainerManager("node2", NODE2_PORT, NODE2_IP)
        node2.start(NETWORK_NAME)
        self.containers["node2"] = node2
        return node2
    
    def create_node2_with_bootstrap(self, bootstrap_enr: str) -> DockerContainerManager:
        """Create and start node2 with bootstrap configuration from the start"""
        node2 = DockerContainerManager("node2", NODE2_PORT, NODE2_IP)
        node2.start_with_bootstrap(bootstrap_enr, NETWORK_NAME)
        self.containers["node2"] = node2
        return node2
    
    def restart_node2_with_bootstrap(self, bootstrap_enr: str) -> str:
        """Restart node2 with bootstrap configuration"""
        if "node2" not in self.containers:
            raise RuntimeError("Node2 not created yet")
        
        return self.containers["node2"].restart_with_bootstrap(bootstrap_enr, NETWORK_NAME)
    
    def cleanup_all(self):
        """Clean up all containers and network"""
        for container in self.containers.values():
            container.stop()
        
        self.cleanup_network()
        self.containers.clear()
    
    def get_container_status(self) -> Dict[str, bool]:
        """Get status of all containers"""
        return {name: container.is_running() for name, container in self.containers.items()} 