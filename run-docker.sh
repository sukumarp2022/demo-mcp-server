#!/bin/bash

# Build and run the Movie Ticket Booking MCP Server in Docker

set -e

echo "🎬 Building Movie Ticket Booking MCP Server Docker image..."

# Build the Docker image
docker build -t movie-ticket-booking-mcp:latest .

echo "✅ Docker image built successfully!"

echo "🚀 Starting the MCP server container..."

# Run the container in stdio mode (default for MCP servers)
docker run -it --rm \
    --name movie-ticket-booking-mcp-server \
    -v movie_booking_data:/app/data \
    movie-ticket-booking-mcp:latest

echo "🎭 Movie Ticket Booking MCP Server is now running in Docker!"
echo "💡 To run in detached mode, use: docker run -d movie-ticket-booking-mcp:latest"
echo "💡 To connect to the server, configure your MCP client to use this Docker container"
