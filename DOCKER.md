# Docker Setup for Movie Ticket Booking MCP Server

This document provides instructions for running the Movie Ticket Booking MCP Server in Docker containers.

## Quick Start

### Option 1: Using the provided script
```bash
./run-docker.sh
```

### Option 2: Manual Docker commands
```bash
# Build the image
docker build -t movie-ticket-booking-mcp:latest .

# Run the container
docker run -it --rm movie-ticket-booking-mcp:latest
```

### Option 3: Using Docker Compose
```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Configuration

### Environment Variables
- `PYTHONUNBUFFERED=1`: Ensures Python output is sent straight to terminal
- `PYTHONPATH=/app/src`: Sets the Python path for module imports

### Volumes
The Docker setup includes a persistent volume for booking data:
- `booking_data:/app/data` - Stores booking information between container restarts

## Usage with MCP Clients

### Claude Desktop Configuration
Add this to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "movie-ticket-booking": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "movie-ticket-booking-mcp:latest"],
      "env": {}
    }
  }
}
```

### Custom MCP Client
For custom MCP clients, you can connect to the Dockerized server using:

```python
import subprocess
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def connect_to_docker_mcp():
    # Start the Docker container
    process = subprocess.Popen([
        "docker", "run", "-i", "--rm", 
        "movie-ticket-booking-mcp:latest"
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    
    # Connect using stdio
    async with stdio_client(process.stdout, process.stdin) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize and use the session
            await session.initialize()
            # Your MCP client code here
```

## Development

### Building for Development
```bash
# Build development image
docker build -t movie-ticket-booking-mcp:dev .

# Run with code mounted for development
docker run -it --rm \
    -v $(pwd)/src:/app/src \
    movie-ticket-booking-mcp:dev
```

### Debugging
```bash
# Run with bash shell for debugging
docker run -it --rm movie-ticket-booking-mcp:latest bash

# Check container logs
docker logs movie-ticket-booking-mcp-server
```

## Available Tools

The containerized MCP server provides these tools:
- `book-for-friends` - Book tickets for 4 friends
- `book-for-relatives` - Book tickets for relatives
- `book-for-class` - Book tickets for a school class
- `book-for-family` - Book tickets for family members

## Health Monitoring

The Docker Compose setup includes health checks:
```bash
# Check service health
docker-compose ps

# View health check logs
docker inspect movie-ticket-booking-mcp-server | grep -A 10 "Health"
```

## Troubleshooting

### Common Issues

1. **Container exits immediately**
   ```bash
   # Check logs for errors
   docker logs movie-ticket-booking-mcp-server
   ```

2. **Permission issues**
   ```bash
   # Ensure scripts are executable
   chmod +x run-docker.sh
   ```

3. **Module import errors**
   ```bash
   # Verify PYTHONPATH is set correctly
   docker run -it --rm movie-ticket-booking-mcp:latest python -c "import sys; print(sys.path)"
   ```

4. **Connection issues**
   - Ensure your MCP client is configured to use stdio mode
   - Verify Docker is running and accessible
   - Check that the container starts without errors

### Cleanup
```bash
# Remove container
docker rm movie-ticket-booking-mcp-server

# Remove image
docker rmi movie-ticket-booking-mcp:latest

# Remove volume
docker volume rm movie_booking_data
```

## Production Deployment

For production deployment, consider:

1. **Security**: Run containers with non-root user
2. **Monitoring**: Add logging and monitoring solutions
3. **Scaling**: Use container orchestration (Kubernetes, Docker Swarm)
4. **Persistence**: Configure external volume storage
5. **Networking**: Set up proper network isolation

Example production Dockerfile modifications:
```dockerfile
# Add non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Add health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import movie_ticket_booking; print('healthy')" || exit 1
```
