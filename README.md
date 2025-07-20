# Connect TCP Python

A TCP server and client implementation in Python with authentication, SSL support, logging, and interactive command interface.

## Features

- **Advanced TCP Server**: Multi-threaded server with client management
- **Interactive TCP Client**: Command-line interface with authentication
- **SSL/TLS Support**: Secure communication with certificate support
- **Authentication System**: Username/password authentication
- **Message Broadcasting**: Send messages to all connected clients
- **Private Messaging**: Direct messaging between authenticated users
- **Server Commands**: List clients, get server information, ping
- **Comprehensive Logging**: File and console logging with configurable levels
- **Configuration Management**: JSON-based configuration system
- **Error Handling**: Robust error handling and graceful shutdown
- **Rate Limiting**: Built-in rate limiting for client requests
- **Signal Handling**: Graceful shutdown on SIGINT/SIGTERM

<!-- ## Project Structure

```
connect-tcp-python/
├── server.py              # Main server implementation
├── client.py              # Main client implementation
├── utils.py               # Utility functions
├── config/
│   └── settings.py        # Configuration management
├── logs/                  # Log files directory
├── tests/                 # Test files directory
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
├── .gitignore            # Git ignore file
└── README.md             # This file
``` -->

## Installation

1. Clone the repository:
```bash
git clone https://github.com/1cbyc/connect-tcp-python.git
cd connect-tcp-python
```

2. Create necessary directories:
```bash
mkdir logs
```

3. No external dependencies required - uses only Python standard library.

## Usage

### Starting the Server

```bash
python server.py
```

The server will start on `127.0.0.1:8080` by default.

### Connecting with Client

```bash
python client.py
```

Or with custom parameters:
```bash
python client.py --host 127.0.0.1 --port 8080
```

### Client Commands

Once connected, use these commands in the interactive client:

- `auth <username> <password>` - Authenticate with server
- `broadcast <message>` - Send broadcast message to all clients
- `private <username> <message>` - Send private message to specific user
- `list` - List all connected clients
- `info` - Get server information
- `ping` - Ping server
- `quit` - Disconnect and exit

### Default Credentials

- Username: `admin`
- Password: `admin123`

## Configuration

The application uses a JSON configuration file at `config/config.json`. You can modify server and client settings:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8080,
    "max_clients": 100,
    "enable_ssl": false,
    "log_level": "INFO"
  },
  "client": {
    "host": "127.0.0.1",
    "port": 8080,
    "enable_ssl": false,
    "timeout": 30
  }
}
```

## SSL/TLS Support

To enable SSL/TLS:

1. Generate SSL certificates:
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

2. Update configuration:
```json
{
  "server": {
    "enable_ssl": true,
    "cert_file": "cert.pem",
    "key_file": "key.pem"
  },
  "client": {
    "enable_ssl": true
  }
}
```

3. Start server and client with SSL enabled.

## Logging

Logs are stored in the `logs/` directory:
- `logs/server.log` - Server logs
- `logs/client.log` - Client logs

Log levels can be configured in the settings.

## Testing

Run tests (if pytest is installed):
```bash
pytest tests/
```

## Security Features

- Password hashing with salt
- Rate limiting
- Input sanitization
- SSL/TLS encryption
- Authentication required for sensitive operations

## Error Handling

The application includes comprehensive error handling:
- Connection errors
- Authentication failures
- Invalid message formats
- Network timeouts
- Graceful shutdown

## Performance

- Multi-threaded server architecture
- Configurable buffer sizes
- Connection pooling
- Efficient message processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on GitHub and I would respond promptly. 