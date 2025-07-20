import threading
import time
import json
from server import TCPServer
from client import TCPClient

def run_server():
    server = TCPServer(host="127.0.0.1", port=8083, max_clients=5)
    server.start()

def run_client():
    time.sleep(2)
    client = TCPClient(host="127.0.0.1", port=8083, timeout=10)
    
    if client.connect():
        print("Client connected successfully")
        
        auth_result = client.authenticate("admin", "admin123")
        if auth_result:
            print("Authentication successful")
            
            ping_result = client.ping_server()
            if ping_result:
                print("Server ping successful")
                
            broadcast_result = client.send_broadcast_message("Hello from example client!")
            if broadcast_result:
                print("Broadcast message sent")
                
            info_data = client.execute_command('server_info')
            if info_data:
                print(f"Server info: {info_data}")
                
        else:
            print("Authentication failed")
            
        client.disconnect()
    else:
        print("Failed to connect to server")

def main():
    print("Starting TCP Server and Client Example")
    print("=" * 40)
    
    server_thread = threading.Thread(target=run_server)
    client_thread = threading.Thread(target=run_client)
    
    server_thread.daemon = True
    client_thread.daemon = True
    
    server_thread.start()
    client_thread.start()
    
    try:
        time.sleep(10)
        print("Example completed")
    except KeyboardInterrupt:
        print("Example interrupted")

if __name__ == "__main__":
    main() 