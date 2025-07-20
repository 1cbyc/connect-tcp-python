import socket
import threading
import json
import time
import logging
import signal
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import ssl
import hashlib
import secrets

@dataclass
class ClientInfo:
    id: str
    socket: socket.socket
    address: Tuple[str, int]
    connected_at: datetime
    last_activity: datetime
    username: Optional[str] = None
    authenticated: bool = False

class TCPServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080, max_clients: int = 100, 
                 enable_ssl: bool = False, cert_file: str = None, key_file: str = None):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.enable_ssl = enable_ssl
        self.cert_file = cert_file
        self.key_file = key_file
        
        self.clients: Dict[str, ClientInfo] = {}
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.client_counter = 0
        
        self.setup_logging()
        self.setup_signal_handlers()
        
    def setup_logging(self):
        import os
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/server.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        
    def generate_client_id(self) -> str:
        self.client_counter += 1
        return f"client_{self.client_counter}_{int(time.time())}"
        
    def create_server_socket(self) -> socket.socket:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass
        
        if self.enable_ssl and self.cert_file and self.key_file:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)
            server_socket = context.wrap_socket(server_socket, server_side=True)
            
        return server_socket
        
    def authenticate_client(self, client_id: str, credentials: dict) -> bool:
        if not credentials or 'username' not in credentials or 'password' not in credentials:
            return False
            
        username = credentials['username']
        password = credentials['password']
        
        if username == "admin" and password == "admin123":
            self.clients[client_id].username = username
            self.clients[client_id].authenticated = True
            return True
        return False
        
    def handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        client_id = self.generate_client_id()
        client_info = ClientInfo(
            id=client_id,
            socket=client_socket,
            address=client_address,
            connected_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.clients[client_id] = client_info
        self.logger.info(f"Client {client_id} connected from {client_address[0]}:{client_address[1]}")
        
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                client_info.last_activity = datetime.now()
                message = data.decode('utf-8').strip()
                
                try:
                    parsed_message = json.loads(message)
                    response = self.process_message(client_id, parsed_message)
                except json.JSONDecodeError:
                    response = {"type": "error", "message": "Invalid JSON format"}
                    
                client_socket.send(json.dumps(response).encode('utf-8'))
                
        except Exception as e:
            self.logger.error(f"Error handling client {client_id}: {e}")
        finally:
            self.disconnect_client(client_id)
            
    def process_message(self, client_id: str, message: dict) -> dict:
        msg_type = message.get('type', 'unknown')
        
        if msg_type == 'auth':
            success = self.authenticate_client(client_id, message.get('credentials', {}))
            return {
                "type": "auth_response",
                "success": success,
                "message": "Authentication successful" if success else "Authentication failed"
            }
            
        elif msg_type == 'message':
            if not self.clients[client_id].authenticated:
                return {"type": "error", "message": "Authentication required"}
                
            content = message.get('content', '')
            target = message.get('target', 'broadcast')
            
            if target == 'broadcast':
                return self.broadcast_message(client_id, content)
            else:
                return self.send_private_message(client_id, target, content)
                
        elif msg_type == 'command':
            if not self.clients[client_id].authenticated:
                return {"type": "error", "message": "Authentication required"}
                
            return self.handle_command(client_id, message.get('command', ''))
            
        elif msg_type == 'ping':
            return {"type": "pong", "timestamp": time.time()}
            
        else:
            return {"type": "error", "message": f"Unknown message type: {msg_type}"}
            
    def handle_command(self, client_id: str, command: str) -> dict:
        if command == 'list_clients':
            client_list = []
            for cid, client in self.clients.items():
                if client.authenticated:
                    client_list.append({
                        "id": cid,
                        "username": client.username,
                        "address": f"{client.address[0]}:{client.address[1]}",
                        "connected_at": client.connected_at.isoformat()
                    })
            return {"type": "command_response", "command": command, "data": client_list}
            
        elif command == 'server_info':
            return {
                "type": "command_response",
                "command": command,
                "data": {
                    "host": self.host,
                    "port": self.port,
                    "connected_clients": len(self.clients),
                    "max_clients": self.max_clients,
                    "uptime": time.time()
                }
            }
            
        else:
            return {"type": "error", "message": f"Unknown command: {command}"}
            
    def broadcast_message(self, sender_id: str, content: str) -> dict:
        sender_username = self.clients[sender_id].username or sender_id
        message = {
            "type": "broadcast",
            "sender": sender_username,
            "content": content,
            "timestamp": time.time()
        }
        
        sent_count = 0
        for client_id, client in self.clients.items():
            if client_id != sender_id and client.authenticated:
                try:
                    client.socket.send(json.dumps(message).encode('utf-8'))
                    sent_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to send broadcast to {client_id}: {e}")
                    
        return {
            "type": "message_response",
            "success": True,
            "message": f"Broadcast sent to {sent_count} clients"
        }
        
    def send_private_message(self, sender_id: str, target_username: str, content: str) -> dict:
        sender_username = self.clients[sender_id].username or sender_id
        
        target_client = None
        for client in self.clients.values():
            if client.username == target_username and client.authenticated:
                target_client = client
                break
                
        if not target_client:
            return {
                "type": "message_response",
                "success": False,
                "message": f"User {target_username} not found or not authenticated"
            }
            
        message = {
            "type": "private_message",
            "sender": sender_username,
            "content": content,
            "timestamp": time.time()
        }
        
        try:
            target_client.socket.send(json.dumps(message).encode('utf-8'))
            return {
                "type": "message_response",
                "success": True,
                "message": f"Private message sent to {target_username}"
            }
        except Exception as e:
            self.logger.error(f"Failed to send private message: {e}")
            return {
                "type": "message_response",
                "success": False,
                "message": "Failed to send private message"
            }
            
    def disconnect_client(self, client_id: str):
        if client_id in self.clients:
            client = self.clients[client_id]
            try:
                client.socket.close()
            except:
                pass
            del self.clients[client_id]
            self.logger.info(f"Client {client_id} disconnected")
            
    def start(self):
        try:
            self.server_socket = self.create_server_socket()
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_clients)
            self.running = True
            
            self.logger.info(f"TCP Server started on {self.host}:{self.port}")
            self.logger.info(f"SSL enabled: {self.enable_ssl}")
            self.logger.info(f"Max clients: {self.max_clients}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    
                    if len(self.clients) >= self.max_clients:
                        client_socket.send(json.dumps({
                            "type": "error",
                            "message": "Server is at maximum capacity"
                        }).encode('utf-8'))
                        client_socket.close()
                        continue
                        
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        self.logger.error("Socket error occurred")
                    break
                    
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            self.stop()
            
    def stop(self):
        self.running = False
        
        for client_id in list(self.clients.keys()):
            self.disconnect_client(client_id)
            
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
                
        self.logger.info("Server stopped")

def main():
    server = TCPServer(
        host="127.0.0.1",
        port=8080,
        max_clients=100,
        enable_ssl=False
    )
    
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

if __name__ == "__main__":
    main()