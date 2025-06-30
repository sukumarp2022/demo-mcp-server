# Movie Ticket Booking MCP Server

An MCP (Model Context Protocol) server for booking movie tickets for different groups including friends, relatives, whole class, and family.

## Features

This MCP server provides tools to simulate movie ticket booking for various group types:

- **Friends Group**: Book tickets for a group of 4 friends
- **Relatives**: Book tickets for family relatives with special requirements
- **Class Trip**: Book tickets for the whole class with group discounts
- **Family**: Book tickets for family with different pricing for adults, children, and seniors

## Components

### Resources

The server implements a movie booking resource system with:
- Custom booking:// URI scheme for accessing individual bookings
- Each booking resource contains detailed booking information in JSON format
- Booking data includes group type, ticket counts, costs, and booking details

### Prompts

The server provides booking-related prompts:
- **booking-summary**: Creates summaries of all movie bookings
  - Optional "group_type" filter to show bookings for specific groups (friends/relatives/class/family)
  - Generates detailed summaries of current bookings

### Tools

The server implements four main booking tools:

1. **book-for-friends**: Book movie tickets for 4 friends
   - Required: movie_title, theater, showtime, date
   - Optional: seat_preference
   - Automatically books 4 tickets and sends notifications to all friends

2. **book-for-relatives**: Book movie tickets for relatives
   - Required: movie_title, theater, showtime, date, ticket_count
   - Optional: special_requirements (wheelchair access, etc.)
   - Flexible ticket count with accommodation for special needs

3. **book-for-class**: Book movie tickets for class trips
   - Required: movie_title, theater, showtime, date, student_count, teacher_count
   - Optional: group_discount
   - Handles large groups with educational pricing and coordination

4. **book-for-family**: Book movie tickets for family outings
   - Required: movie_title, theater, showtime, date, adult_count, child_count
   - Optional: senior_count
   - Different pricing tiers for adults, children, and seniors

## Configuration

### Claude Desktop Integration

Add this configuration to your Claude Desktop config file:

**Development/Local Server:**
```json
"mcpServers": {
  "movie-ticket-booking": {
    "command": "uv",
    "args": [
      "--directory",
      "/Users/sukumarp/VSCode-Projects/AgentMode/demo-mcp-server",
      "run",
      "movie-ticket-booking"
    ]
  }
}
```

**Docker Server:**
```json
"mcpServers": {
  "movie-ticket-booking": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "movie-ticket-booking-mcp:latest"
    ]
  }
}
```

**Published Server (when available):**
```json
"mcpServers": {
  "movie-ticket-booking": {
    "command": "uvx",
    "args": ["movie-ticket-booking"]
  }
}
```

### VS Code Integration

This project includes a `.vscode/mcp.json` file for VS Code MCP debugging support.

## Deployment Options

### Local Development
```bash
uv run movie-ticket-booking
```

### Docker Deployment
```bash
# Build and run with Docker
./run-docker.sh

# Or manually:
docker build -t movie-ticket-booking-mcp:latest .
docker run -it --rm movie-ticket-booking-mcp:latest

# Using Docker Compose
docker-compose up -d
```

For detailed Docker setup instructions, see [DOCKER.md](DOCKER.md).

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "movie-ticket-booking": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/sukumarp/VSCode-Projects/AgentMode/demo-mcp-server",
        "run",
        "movie-ticket-booking"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Docker Servers Configuration</summary>
  ```
  "mcpServers": {
    "movie-ticket-booking": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "movie-ticket-booking-mcp:latest"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "movie-ticket-booking": {
      "command": "uvx",
      "args": [
        "movie-ticket-booking"
      ]
    }
  }
  ```
</details>

## Testing & Validation

To validate that the server is working correctly:

```bash
# Run the validation script
uv run python validate_server.py

# Test server startup (will wait for stdin, press Ctrl+C to exit)
uv run movie-ticket-booking
```

## Example Usage

Once configured with Claude Desktop, you can use natural language to book movie tickets:

- "Book movie tickets for my 4 friends to see 'Dune' tomorrow at 7 PM"
- "Reserve seats for my family (2 adults, 3 children) for the latest Marvel movie"
- "Book a class trip to see an educational film for 25 students and 3 teachers"
- "Get tickets for my relatives gathering (8 people) with wheelchair accessibility"

The server will simulate the entire booking process including:
- API calls to fetch showtimes
- Seat reservations
- Payment processing
- Ticket delivery notifications
- Special accommodation arrangements

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/sukumarp/VSCode-Projects/AgentMode/demo-mcp-server run movie-ticket-booking
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.