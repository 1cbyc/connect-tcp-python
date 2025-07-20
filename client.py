import socket
import json
import time
import threading
import logging
import signal
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import ssl
import getpass

class TCPClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080, enable_ssl: bool = False, 
                 verify_ssl: bool = True, timeout: int = 30):
        self.host = host
        self.port = port
        self.enable_ssl = enable_ssl
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.authenticated = False
        self.username: Optional[str] = None
        self.client_id: Optional[str] = None
        
        self.setup_logging()
        self.setup_signal_handlers()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/client.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}, disconnecting...")
        self.disconnect()
        
    def create_socket(self) -> socket.socket:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(self.timeout)
        
        if self.enable_ssl:
            context = ssl.create_default_context()
            if not self.verify_ssl:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            client_socket = context.wrap_socket(client_socket)
            
        return client_socket
        
    def connect(self) -> bool:
        try:
            self.socket = self.create_socket()
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.logger.info(f"Connected to server {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to server: {e}")
            return False
            
    def disconnect(self):
        self.connected = False
        self.authenticated = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.logger.info("Disconnected from server")
        
    def send_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.connected or not self.socket:
            self.logger.error("Not connected to server")
            return None
            
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
            response_data = self.socket.recv(4096)
            if response_data:
                return json.loads(response_data.decode('utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to send/receive message: {e}")
            self.disconnect()
        return None
        
    def authenticate(self, username: str, password: str) -> bool:
        message = {
            "type": "auth",
            "credentials": {
                "username": username,
                "password": password
            }
        }
        
        response = self.send_message(message)
        if response and response.get('type') == 'auth_response':
            success = response.get('success', False)
            if success:
                self.authenticated = True
                self.username = username
                self.logger.info("Authentication successful")
            else:
                self.logger.error(f"Authentication failed: {response.get('message', 'Unknown error')}")
            return success
        return False
        
    def send_broadcast_message(self, content: str) -> bool:
        if not self.authenticated:
            self.logger.error("Authentication required")
            return False
            
        message = {
            "type": "message",
            "target": "broadcast",
            "content": content
        }
        
        response = self.send_message(message)
        if response and response.get('type') == 'message_response':
            success = response.get('success', False)
            if success:
                self.logger.info(f"Broadcast sent: {response.get('message', '')}")
            else:
                self.logger.error(f"Failed to send broadcast: {response.get('message', '')}")
            return success
        return False
        
    def send_private_message(self, target_username: str, content: str) -> bool:
        if not self.authenticated:
            self.logger.error("Authentication required")
            return False
            
        message = {
            "type": "message",
            "target": target_username,
            "content": content
        }
        
        response = self.send_message(message)
        if response and response.get('type') == 'message_response':
            success = response.get('success', False)
            if success:
                self.logger.info(f"Private message sent to {target_username}")
            else:
                self.logger.error(f"Failed to send private message: {response.get('message', '')}")
            return success
        return False
        
    def execute_command(self, command: str) -> Optional[Dict[str, Any]]:
        if not self.authenticated:
            self.logger.error("Authentication required")
            return None
            
        message = {
            "type": "command",
            "command": command
        }
        
        response = self.send_message(message)
        if response and response.get('type') == 'command_response':
            return response.get('data')
        elif response and response.get('type') == 'error':
            self.logger.error(f"Command error: {response.get('message', '')}")
        return None
        
    def ping_server(self) -> bool:
        message = {"type": "ping"}
        response = self.send_message(message)
        if response and response.get('type') == 'pong':
            self.logger.info("Server ping successful")
            return True
        return False
        
    def start_interactive_mode(self):
        if not self.connect():
            return
            
        print("TCP Client Interactive Mode")
        print("Commands:")
        print("  auth <username> <password> - Authenticate with server")
        print("  broadcast <message> - Send broadcast message")
        print("  private <username> <message> - Send private message")
        print("  list - List connected clients")
        print("  info - Get server information")
        print("  ping - Ping server")
        print("  quit - Disconnect and exit")
        print()
        
        while self.connected:
            try:
                command = input("> ").strip()
                if not command:
                    continue
                    
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == 'quit':
                    break
                elif cmd == 'auth' and len(parts) >= 3:
                    username = parts[1]
                    password = parts[2]
                    self.authenticate(username, password)
                elif cmd == 'broadcast' and len(parts) >= 2:
                    content = ' '.join(parts[1:])
                    self.send_broadcast_message(content)
                elif cmd == 'private' and len(parts) >= 3:
                    target = parts[1]
                    content = ' '.join(parts[2:])
                    self.send_private_message(target, content)
                elif cmd == 'list':
                    data = self.execute_command('list_clients')
                    if data:
                        print(f"Connected clients ({len(data)}):")
                        for client in data:
                            print(f"  {client['username']} ({client['address']}) - {client['connected_at']}")
                    else:
                        print("Failed to get client list")
                elif cmd == 'info':
                    data = self.execute_command('server_info')
                    if data:
                        print(f"Server Information:")
                        print(f"  Host: {data['host']}:{data['port']}")
                        print(f"  Connected clients: {data['connected_clients']}/{data['max_clients']}")
                        print(f"  Uptime: {data['uptime']:.2f} seconds")
                    else:
                        print("Failed to get server information")
                elif cmd == 'ping':
                    self.ping_server()
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error in interactive mode: {e}")
                break
                
        self.disconnect()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='TCP Client')
    parser.add_argument('--host', default='127.0.0.1', help='Server host')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    parser.add_argument('--ssl', action='store_true', help='Enable SSL')
    parser.add_argument('--no-verify', action='store_true', help='Disable SSL verification')
    parser.add_argument('--timeout', type=int, default=30, help='Connection timeout')
    
    args = parser.parse_args()
    
    client = TCPClient(
        host=args.host,
        port=args.port,
        enable_ssl=args.ssl,
        verify_ssl=not args.no_verify,
        timeout=args.timeout
    )
    
    try:
        client.start_interactive_mode()
    except KeyboardInterrupt:
        client.disconnect()

if __name__ == "__main__":
    main()
