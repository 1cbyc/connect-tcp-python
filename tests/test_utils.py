import unittest
import time
from utils import (
    generate_token, hash_password, verify_password, format_timestamp,
    validate_json_message, create_response, sanitize_input, validate_port,
    validate_host, format_bytes, calculate_checksum, is_valid_username,
    rate_limit_check
)

class TestUtils(unittest.TestCase):
    def test_generate_token(self):
        token1 = generate_token()
        token2 = generate_token()
        
        self.assertEqual(len(token1), 64)
        self.assertEqual(len(token2), 64)
        self.assertNotEqual(token1, token2)
        
    def test_hash_password(self):
        password = "testpassword"
        hashed1, salt1 = hash_password(password)
        hashed2, salt2 = hash_password(password)
        
        self.assertNotEqual(hashed1, hashed2)
        self.assertNotEqual(salt1, salt2)
        self.assertTrue(verify_password(password, hashed1, salt1))
        self.assertTrue(verify_password(password, hashed2, salt2))
        
    def test_verify_password(self):
        password = "testpassword"
        wrong_password = "wrongpassword"
        hashed, salt = hash_password(password)
        
        self.assertTrue(verify_password(password, hashed, salt))
        self.assertFalse(verify_password(wrong_password, hashed, salt))
        
    def test_format_timestamp(self):
        timestamp = time.time()
        formatted = format_timestamp(timestamp)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("202", formatted)
        
    def test_validate_json_message(self):
        valid_json = '{"type": "ping"}'
        invalid_json = '{"type": "ping"'
        
        self.assertIsNotNone(validate_json_message(valid_json))
        self.assertIsNone(validate_json_message(invalid_json))
        
    def test_create_response(self):
        response = create_response(True, "Success", {"data": "test"})
        
        self.assertTrue(response["success"])
        self.assertEqual(response["message"], "Success")
        self.assertEqual(response["data"]["data"], "test")
        self.assertIn("timestamp", response)
        
    def test_sanitize_input(self):
        input_str = "test\n\rinput"
        sanitized = sanitize_input(input_str)
        
        self.assertEqual(sanitized, "test input")
        
    def test_validate_port(self):
        self.assertTrue(validate_port(8080))
        self.assertTrue(validate_port(1))
        self.assertTrue(validate_port(65535))
        self.assertFalse(validate_port(0))
        self.assertFalse(validate_port(65536))
        
    def test_validate_host(self):
        self.assertTrue(validate_host("127.0.0.1"))
        self.assertTrue(validate_host("localhost"))
        self.assertTrue(validate_host("192.168.1.1"))
        self.assertFalse(validate_host("256.256.256.256"))
        self.assertFalse(validate_host("invalid"))
        
    def test_format_bytes(self):
        self.assertEqual(format_bytes(1024), "1.0 KB")
        self.assertEqual(format_bytes(1048576), "1.0 MB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024), "1.0 GB")
        
    def test_calculate_checksum(self):
        data = b"test data"
        checksum = calculate_checksum(data)
        
        self.assertEqual(len(checksum), 32)
        self.assertIsInstance(checksum, str)
        
    def test_is_valid_username(self):
        self.assertTrue(is_valid_username("testuser"))
        self.assertTrue(is_valid_username("test_user"))
        self.assertTrue(is_valid_username("test123"))
        self.assertFalse(is_valid_username(""))
        self.assertFalse(is_valid_username("a" * 51))
        self.assertFalse(is_valid_username("test@user"))
        
    def test_rate_limit_check(self):
        rate_limits = {}
        client_id = "test_client"
        
        for i in range(10):
            self.assertTrue(rate_limit_check(client_id, rate_limits, 10, 60))
            
        self.assertFalse(rate_limit_check(client_id, rate_limits, 10, 60))

if __name__ == '__main__':
    unittest.main() 