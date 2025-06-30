import asyncio
from datetime import datetime
from typing import Dict, Any

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Store movie bookings to demonstrate state management
bookings: dict[str, dict[str, Any]] = {}

server = Server("movie-ticket-booking")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available movie booking resources.
    Each booking is exposed as a resource with a custom booking:// URI scheme.
    """
    return [
        types.Resource(
            uri=AnyUrl(f"booking://internal/{booking_id}"),
            name=f"Booking: {booking_id}",
            description=f"Movie ticket booking for {booking_data['group_type']} - {booking_data['movie_title']}",
            mimeType="application/json",
        )
        for booking_id, booking_data in bookings.items()
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific booking's details by its URI.
    The booking ID is extracted from the URI path component.
    """
    if uri.scheme != "booking":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    booking_id = uri.path
    if booking_id is not None:
        booking_id = booking_id.lstrip("/")
        if booking_id in bookings:
            import json
            return json.dumps(bookings[booking_id], indent=2)
    raise ValueError(f"Booking not found: {booking_id}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts for movie booking assistance.
    """
    return [
        types.Prompt(
            name="booking-summary",
            description="Creates a summary of all movie bookings",
            arguments=[
                types.PromptArgument(
                    name="group_type",
                    description="Filter by group type (friends/relatives/class/family)",
                    required=False,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt for movie booking summaries.
    """
    if name != "booking-summary":
        raise ValueError(f"Unknown prompt: {name}")

    group_filter = (arguments or {}).get("group_type", "all")
    
    filtered_bookings = bookings
    if group_filter != "all":
        filtered_bookings = {
            booking_id: booking_data 
            for booking_id, booking_data in bookings.items() 
            if booking_data.get('group_type') == group_filter
        }

    return types.GetPromptResult(
        description="Summarize the current movie bookings",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Here are the current movie bookings to summarize:\n\n"
                    + "\n".join(
                        f"- {booking_id}: {booking_data['movie_title']} for {booking_data['group_type']} ({booking_data['ticket_count']} tickets)"
                        for booking_id, booking_data in filtered_bookings.items()
                    ),
                ),
            )
        ],
    )

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available movie booking tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="book-for-friends",
            description="Book movie tickets for a group of 4 friends",
            inputSchema={
                "type": "object",
                "properties": {
                    "movie_title": {"type": "string", "description": "Title of the movie"},
                    "theater": {"type": "string", "description": "Theater name"},
                    "showtime": {"type": "string", "description": "Show time (e.g., '7:30 PM')"},
                    "date": {"type": "string", "description": "Date of the show (YYYY-MM-DD)"},
                    "seat_preference": {"type": "string", "description": "Seating preference (e.g., 'middle', 'back', 'front')"},
                },
                "required": ["movie_title", "theater", "showtime", "date"],
            },
        ),
        types.Tool(
            name="book-for-relatives",
            description="Book movie tickets for relatives",
            inputSchema={
                "type": "object",
                "properties": {
                    "movie_title": {"type": "string", "description": "Title of the movie"},
                    "theater": {"type": "string", "description": "Theater name"},
                    "showtime": {"type": "string", "description": "Show time (e.g., '7:30 PM')"},
                    "date": {"type": "string", "description": "Date of the show (YYYY-MM-DD)"},
                    "ticket_count": {"type": "integer", "description": "Number of tickets needed"},
                    "special_requirements": {"type": "string", "description": "Any special requirements (wheelchair access, etc.)"},
                },
                "required": ["movie_title", "theater", "showtime", "date", "ticket_count"],
            },
        ),
        types.Tool(
            name="book-for-class",
            description="Book movie tickets for the whole class",
            inputSchema={
                "type": "object",
                "properties": {
                    "movie_title": {"type": "string", "description": "Title of the movie"},
                    "theater": {"type": "string", "description": "Theater name"},
                    "showtime": {"type": "string", "description": "Show time (e.g., '7:30 PM')"},
                    "date": {"type": "string", "description": "Date of the show (YYYY-MM-DD)"},
                    "student_count": {"type": "integer", "description": "Number of students"},
                    "teacher_count": {"type": "integer", "description": "Number of teachers/chaperones"},
                    "group_discount": {"type": "boolean", "description": "Apply group discount if available"},
                },
                "required": ["movie_title", "theater", "showtime", "date", "student_count", "teacher_count"],
            },
        ),
        types.Tool(
            name="book-for-family",
            description="Book movie tickets for the family",
            inputSchema={
                "type": "object",
                "properties": {
                    "movie_title": {"type": "string", "description": "Title of the movie"},
                    "theater": {"type": "string", "description": "Theater name"},
                    "showtime": {"type": "string", "description": "Show time (e.g., '7:30 PM')"},
                    "date": {"type": "string", "description": "Date of the show (YYYY-MM-DD)"},
                    "adult_count": {"type": "integer", "description": "Number of adults"},
                    "child_count": {"type": "integer", "description": "Number of children"},
                    "senior_count": {"type": "integer", "description": "Number of seniors", "default": 0},
                },
                "required": ["movie_title", "theater", "showtime", "date", "adult_count", "child_count"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle movie ticket booking tool execution requests.
    Tools simulate the booking process and notify clients of changes.
    """
    if not arguments:
        raise ValueError("Missing arguments")

    # Generate a unique booking ID
    booking_id = f"booking_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if name == "book-for-friends":
        print("🎬 Starting booking process for friends group...")
        print("📡 Fetching movie showtimes API...")
        print("🎟️ Reserving 4 tickets for friends...")
        
        booking_data = {
            "booking_id": booking_id,
            "group_type": "friends",
            "ticket_count": 4,
            "movie_title": arguments.get("movie_title"),
            "theater": arguments.get("theater"),
            "showtime": arguments.get("showtime"),
            "date": arguments.get("date"),
            "seat_preference": arguments.get("seat_preference", "middle"),
            "total_cost": 60.00,  # Simulated cost
            "booking_time": datetime.now().isoformat()
        }
        
        print("💳 Processing payment for friends group...")
        print("📧 Sending tickets to all 4 friends via email...")
        print("📱 Sending confirmation SMS to group organizer...")
        
        result_text = f"✅ Successfully booked 4 tickets for '{arguments.get('movie_title')}' at {arguments.get('theater')}. Booking ID: {booking_id}. Tickets sent to all friends!"
        
    elif name == "book-for-relatives":
        ticket_count = arguments.get("ticket_count", 1)
        print(f"🎬 Starting booking process for {ticket_count} relatives...")
        print("📡 Fetching movie showtimes API...")
        print(f"🎟️ Reserving {ticket_count} tickets for relatives...")
        
        booking_data = {
            "booking_id": booking_id,
            "group_type": "relatives",
            "ticket_count": ticket_count,
            "movie_title": arguments.get("movie_title"),
            "theater": arguments.get("theater"),
            "showtime": arguments.get("showtime"),
            "date": arguments.get("date"),
            "special_requirements": arguments.get("special_requirements"),
            "total_cost": ticket_count * 15.00,  # Simulated cost
            "booking_time": datetime.now().isoformat()
        }
        
        print("🔍 Checking for special requirements...")
        if arguments.get("special_requirements"):
            print(f"♿ Arranging for: {arguments.get('special_requirements')}")
        
        print("💳 Processing payment for relatives...")
        print("📧 Sending tickets to family email list...")
        print("📞 Calling relatives to confirm attendance...")
        
        result_text = f"✅ Successfully booked {ticket_count} tickets for relatives for '{arguments.get('movie_title')}' at {arguments.get('theater')}. Booking ID: {booking_id}. Family notifications sent!"
        
    elif name == "book-for-class":
        student_count = arguments.get("student_count", 0)
        teacher_count = arguments.get("teacher_count", 0)
        total_count = student_count + teacher_count
        group_discount = arguments.get("group_discount", False)
        
        print(f"🎬 Starting booking process for class trip - {student_count} students + {teacher_count} teachers...")
        print("📡 Fetching movie showtimes API...")
        print("🏫 Checking group booking availability...")
        print(f"🎟️ Reserving {total_count} tickets for class...")
        
        base_cost = total_count * 12.00
        final_cost = base_cost * 0.8 if group_discount else base_cost  # 20% group discount
        
        booking_data = {
            "booking_id": booking_id,
            "group_type": "class",
            "ticket_count": total_count,
            "student_count": student_count,
            "teacher_count": teacher_count,
            "movie_title": arguments.get("movie_title"),
            "theater": arguments.get("theater"),
            "showtime": arguments.get("showtime"),
            "date": arguments.get("date"),
            "group_discount_applied": group_discount,
            "total_cost": final_cost,
            "booking_time": datetime.now().isoformat()
        }
        
        if group_discount:
            print("💰 Applying 20% group discount...")
        
        print("🏦 Processing school payment authorization...")
        print("📋 Generating permission slip summary...")
        print("🚌 Coordinating transportation arrangements...")
        print("📧 Sending booking confirmation to school administration...")
        print("📱 Notifying all teachers and parent coordinators...")
        
        result_text = f"✅ Successfully booked {total_count} tickets for class trip to '{arguments.get('movie_title')}' at {arguments.get('theater')}. Booking ID: {booking_id}. School notifications sent!"
        
    elif name == "book-for-family":
        adult_count = arguments.get("adult_count", 0)
        child_count = arguments.get("child_count", 0)
        senior_count = arguments.get("senior_count", 0)
        total_count = adult_count + child_count + senior_count
        
        print(f"🎬 Starting booking process for family - {adult_count} adults, {child_count} children, {senior_count} seniors...")
        print("📡 Fetching movie showtimes API...")
        print("👨‍👩‍👧‍👦 Checking family-friendly seating options...")
        print(f"🎟️ Reserving {total_count} tickets for family...")
        
        # Calculate cost with different pricing for adults, children, and seniors
        total_cost = (adult_count * 15.00) + (child_count * 10.00) + (senior_count * 12.00)
        
        booking_data = {
            "booking_id": booking_id,
            "group_type": "family",
            "ticket_count": total_count,
            "adult_count": adult_count,
            "child_count": child_count,
            "senior_count": senior_count,
            "movie_title": arguments.get("movie_title"),
            "theater": arguments.get("theater"),
            "showtime": arguments.get("showtime"),
            "date": arguments.get("date"),
            "total_cost": total_cost,
            "booking_time": datetime.now().isoformat()
        }
        
        print("🍿 Adding family concession package...")
        print("💳 Processing family payment...")
        print("📧 Sending tickets to family email...")
        print("📅 Adding event to family calendar...")
        print("🎈 Arranging special seating for children...")
        
        result_text = f"✅ Successfully booked {total_count} tickets for family movie night - '{arguments.get('movie_title')}' at {arguments.get('theater')}. Booking ID: {booking_id}. Family package confirmed!"
        
    else:
        raise ValueError(f"Unknown tool: {name}")

    # Store the booking
    bookings[booking_id] = booking_data

    # Notify clients that resources have changed
    await server.request_context.session.send_resource_list_changed()

    print("✨ Booking process completed successfully!")
    
    return [
        types.TextContent(
            type="text",
            text=result_text,
        )
    ]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="movie-ticket-booking",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )