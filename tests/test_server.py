import unittest
import socket
import json
import threading
import time
from server import TCPServer

class TestTCPServer(unittest.TestCase):
    def setUp(self):
        self.server = TCPServer(host="127.0.0.1", port=8081, max_clients=10)
        self.server_thread = threading.Thread(target=self.server.start)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(1)
        
    def tearDown(self):
        self.server.stop()
        time.sleep(1)
        
    def test_server_creation(self):
        self.assertIsNotNone(self.server)
        self.assertEqual(self.server.host, "127.0.0.1")
        self.assertEqual(self.server.port, 8081)
        
    def test_client_connection(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(("127.0.0.1", 8081))
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to connect: {e}")
        finally:
            client_socket.close()
            
    def test_authentication(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(("127.0.0.1", 8081))
            
            auth_message = {
                "type": "auth",
                "credentials": {
                    "username": "admin",
                    "password": "admin123"
                }
            }
            
            client_socket.send(json.dumps(auth_message).encode('utf-8'))
            response = client_socket.recv(4096)
            response_data = json.loads(response.decode('utf-8'))
            
            self.assertEqual(response_data.get('type'), 'auth_response')
            self.assertTrue(response_data.get('success'))
            
        except Exception as e:
            self.fail(f"Authentication test failed: {e}")
        finally:
            client_socket.close()
            
    def test_ping(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(("127.0.0.1", 8081))
            
            ping_message = {"type": "ping"}
            client_socket.send(json.dumps(ping_message).encode('utf-8'))
            response = client_socket.recv(4096)
            response_data = json.loads(response.decode('utf-8'))
            
            self.assertEqual(response_data.get('type'), 'pong')
            self.assertIn('timestamp', response_data)
            
        except Exception as e:
            self.fail(f"Ping test failed: {e}")
        finally:
            client_socket.close()

if __name__ == '__main__':
    unittest.main() 