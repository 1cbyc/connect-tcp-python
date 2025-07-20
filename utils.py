import hashlib
import secrets
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime

def generate_token(length: int = 32) -> str:
    return secrets.token_hex(length)

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    
    hash_obj = hashlib.sha256()
    hash_obj.update((password + salt).encode('utf-8'))
    hashed = hash_obj.hexdigest()
    
    return hashed, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == hashed

def format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def validate_json_message(message: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return None

def create_response(success: bool, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = {
        "success": success,
        "message": message,
        "timestamp": time.time()
    }
    if data:
        response["data"] = data
    return response

def sanitize_input(input_str: str) -> str:
    return input_str.strip().replace('\n', ' ').replace('\r', '')

def validate_port(port: int) -> bool:
    return 1 <= port <= 65535

def validate_host(host: str) -> bool:
    if host == "localhost" or host == "127.0.0.1":
        return True
    
    parts = host.split('.')
    if len(parts) != 4:
        return False
    
    try:
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    except ValueError:
        return False

def format_bytes(bytes_value: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

def calculate_checksum(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()

def is_valid_username(username: str) -> bool:
    if not username or len(username) > 50:
        return False
    
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-')
    return all(c in allowed_chars for c in username)

def rate_limit_check(client_id: str, rate_limits: Dict[str, list], max_requests: int = 10, window_seconds: int = 60) -> bool:
    current_time = time.time()
    
    if client_id not in rate_limits:
        rate_limits[client_id] = []
    
    requests = rate_limits[client_id]
    
    requests = [req_time for req_time in requests if current_time - req_time < window_seconds]
    rate_limits[client_id] = requests
    
    if len(requests) >= max_requests:
        return False
    
    requests.append(current_time)
    return True 