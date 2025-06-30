#!/usr/bin/env python3
"""
Simple validation script to check if the MCP server can start without errors
"""

import sys
import importlib.util

def validate_server():
    """Validate that the server module loads correctly"""
    print("🧪 Validating Movie Ticket Booking MCP Server\n")
    
    try:
        # Try to import the server module
        from movie_ticket_booking import server
        print("✅ Server module imported successfully")
        
        # Check if the server object exists
        if hasattr(server, 'server'):
            print("✅ Server object found")
        else:
            print("❌ Server object not found")
            return False
            
        # Check if main function exists
        if hasattr(server, 'main'):
            print("✅ Main function found")
        else:
            print("❌ Main function not found")
            return False
            
        # Validate bookings dictionary exists
        if hasattr(server, 'bookings'):
            print("✅ Bookings storage found")
        else:
            print("❌ Bookings storage not found")
            return False
        
        print("\n🎬 Server validation completed successfully!")
        print("\n📋 Available tools that will be exposed:")
        print("  - book-for-friends: Book tickets for 4 friends")
        print("  - book-for-relatives: Book tickets for relatives")
        print("  - book-for-class: Book tickets for whole class")
        print("  - book-for-family: Book tickets for family")
        
        print("\n📝 Available prompts:")
        print("  - booking-summary: Summarize all bookings")
        
        print("\n📚 Available resources:")
        print("  - booking:// URIs for accessing booking details")
        
        print("\n🚀 To run the server:")
        print("  uv run movie-ticket-booking")
        
        print("\n🔍 To debug with MCP Inspector:")
        print("  npx @modelcontextprotocol/inspector uv --directory . run movie-ticket-booking")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import server module: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = validate_server()
    sys.exit(0 if success else 1)
