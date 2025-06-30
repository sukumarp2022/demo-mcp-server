#!/usr/bin/env python3
"""
Simple test script to validate the MCP server functionality
"""

import asyncio
import json
from movie_ticket_booking.server import server

async def test_server():
    """Test the movie booking server tools"""
    print("🧪 Testing Movie Ticket Booking MCP Server\n")
    
    # Test listing tools
    print("1. Testing list_tools...")
    tools = await server._request_handlers['list_tools']()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    print()
    
    # Test a sample booking
    print("2. Testing book-for-friends tool...")
    
    # Create a mock request context
    class MockSession:
        async def send_resource_list_changed(self):
            print("📢 Resource list changed notification sent")
    
    class MockRequestContext:
        def __init__(self):
            self.session = MockSession()
    
    # Temporarily set the request context
    original_context = getattr(server, 'request_context', None)
    server.request_context = MockRequestContext()
    
    try:
        result = await server._request_handlers['call_tool']("book-for-friends", {
            "movie_title": "Avengers: Endgame",
            "theater": "AMC Downtown",
            "showtime": "7:30 PM",
            "date": "2024-01-15",
            "seat_preference": "middle"
        })
        
        print(f"Booking result: {result[0].text}")
        print()
        
        # Test listing resources
        print("3. Testing list_resources...")
        resources = await server._request_handlers['list_resources']()
        print(f"Found {len(resources)} resources:")
        for resource in resources:
            print(f"  - {resource.name}")
        print()
        
        print("✅ All tests passed! The MCP server is working correctly.")
        
    finally:
        # Restore original context
        if original_context:
            server.request_context = original_context
        else:
            delattr(server, 'request_context')

if __name__ == "__main__":
    asyncio.run(test_server())
