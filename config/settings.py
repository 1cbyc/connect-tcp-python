import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8080
    max_clients: int = 100
    enable_ssl: bool = False
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    log_level: str = "INFO"
    log_file: str = "logs/server.log"
    timeout: int = 30
    buffer_size: int = 4096

@dataclass
class ClientConfig:
    host: str = "127.0.0.1"
    port: int = 8080
    enable_ssl: bool = False
    verify_ssl: bool = True
    timeout: int = 30
    log_level: str = "INFO"
    log_file: str = "logs/client.log"
    buffer_size: int = 4096

class ConfigManager:
    def __init__(self, config_file: str = "config/config.json"):
        self.config_file = config_file
        self.server_config = ServerConfig()
        self.client_config = ClientConfig()
        self.load_config()
        
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    
                if 'server' in data:
                    server_data = data['server']
                    for key, value in server_data.items():
                        if hasattr(self.server_config, key):
                            setattr(self.server_config, key, value)
                            
                if 'client' in data:
                    client_data = data['client']
                    for key, value in client_data.items():
                        if hasattr(self.client_config, key):
                            setattr(self.client_config, key, value)
                            
            except Exception as e:
                print(f"Failed to load config: {e}")
                
    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump({
                    'server': asdict(self.server_config),
                    'client': asdict(self.client_config)
                }, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
            
    def get_server_config(self) -> ServerConfig:
        return self.server_config
        
    def get_client_config(self) -> ClientConfig:
        return self.client_config
        
    def update_server_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.server_config, key):
                setattr(self.server_config, key, value)
        self.save_config()
        
    def update_client_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.client_config, key):
                setattr(self.client_config, key, value)
        self.save_config()

config_manager = ConfigManager() 