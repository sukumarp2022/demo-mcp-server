# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package installer)
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Install project dependencies using uv
RUN uv sync --frozen

# Expose port for MCP server (though MCP typically uses stdio)
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Create entrypoint script
RUN echo '#!/bin/bash\n\
if [ "$1" = "stdio" ]; then\n\
    exec uv run movie-ticket-booking\n\
elif [ "$1" = "server" ]; then\n\
    # For HTTP/WebSocket mode if needed in future\n\
    exec uv run movie-ticket-booking\n\
else\n\
    exec "$@"\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Default command runs the MCP server in stdio mode
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["stdio"]
