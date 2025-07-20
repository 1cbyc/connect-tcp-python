import unittest
import socket
import json
import threading
import time
from client import TCPClient

class TestTCPClient(unittest.TestCase):
    def setUp(self):
        self.client = TCPClient(host="127.0.0.1", port=8082, timeout=5)
        
    def test_client_creation(self):
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.host, "127.0.0.1")
        self.assertEqual(self.client.port, 8082)
        self.assertFalse(self.client.connected)
        
    def test_socket_creation(self):
        socket_obj = self.client.create_socket()
        self.assertIsNotNone(socket_obj)
        socket_obj.close()
        
    def test_connection_failure(self):
        result = self.client.connect()
        self.assertFalse(result)
        self.assertFalse(self.client.connected)
        
    def test_message_validation(self):
        valid_message = {"type": "ping"}
        invalid_message = "invalid json"
        
        self.assertIsNotNone(self.client.send_message(valid_message))
        self.assertIsNone(self.client.send_message(invalid_message))
        
    def test_authentication_failure(self):
        self.assertFalse(self.client.authenticated)
        result = self.client.authenticate("invalid", "invalid")
        self.assertFalse(result)
        self.assertFalse(self.client.authenticated)

if __name__ == '__main__':
    unittest.main() 