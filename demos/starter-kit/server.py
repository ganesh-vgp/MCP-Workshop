#!/usr/bin/env python3
"""
MCP Server Demo - Starter Kit for Local LLM Integration
Cool Club 007 - August 2025

TODO: Complete this MCP server by following along with the session!

This server will provide tools that a local LLM can use:
1. Calculator tools (add, subtract, multiply, divide)
2. File operations (read, write, list)
3. Resources for direct file access

IMPORTANT: This version is designed to work with local LLMs via our chat interface!
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path

# MCP imports - these provide the core functionality
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.server.sse import SseServerTransport
    from mcp.types import Tool, Resource, TextContent
    import mcp.types as types
except ImportError:
    print("MCP library not found. Install with: pip install mcp")
    print("For this demo, we'll use a mock implementation")
    
    # Mock classes for demo purposes
    class Server:
        def __init__(self, name): self.name = name
        def list_tools(self): return lambda f: f
        def call_tool(self): return lambda f: f
        def list_resources(self): return lambda f: f
        def read_resource(self): return lambda f: f
    
    class Tool:
        def __init__(self, name, description, inputSchema):
            self.name = name
            self.description = description
            self.inputSchema = inputSchema
    
    class Resource:
        def __init__(self, uri, name, description):
            self.uri = uri
            self.name = name
            self.description = description
    
    class TextContent:
        def __init__(self, type="text", text=""):
            self.type = type
            self.text = text
    
    # Mock types module
    class types:
        TextContent = TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-demo-server")

# TODO: Create the MCP server instance
# HINT: Use Server("demo-server") to create a server named "demo-server"
server = Server("demo-server")  # This line creates the server

# TODO: Part 1 - Initialize server with tools and resources
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    Return the list of tools this server provides.
    
    TODO: Return a list of Tool objects for:
    - calculator operations (add, subtract, multiply, divide)
    - file operations (read_file, write_file, list_files)
    
    HINT: Tool objects need name, description, and input schema
    """
    return [
        # TODO: Add calculator tools here
        
        # TODO: Add file operation tools here
    ]

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """
    Return the list of resources this server provides.
    
    TODO: Return a list of resources for files in the demo_files directory
    HINT: Each file should be a Resource with uri, name, and description
    """
    resources = []
    
    # TODO: Scan demo_files directory and create Resource objects
    # HINT: Use pathlib.Path("demo_files").glob("*") to find files
    
    return resources

# TODO: Part 2 - Implement calculator tools
@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handle tool calls from the AI model.
    
    TODO: Implement handlers for each tool:
    - add, subtract, multiply, divide
    - read_file, write_file, list_files
    """
    
    # Calculator tools
    if name == "add":
        # TODO: Get 'a' and 'b' from arguments, add them, return result
        pass
    
    elif name == "subtract":
        # TODO: Implement subtraction
        pass
        
    elif name == "multiply":
        # TODO: Implement multiplication
        pass
        
    elif name == "divide":
        # TODO: Implement division (handle division by zero!)
        pass
    
    # File operation tools
    elif name == "read_file":
        # TODO: Read file from arguments['filename'] and return contents
        pass
        
    elif name == "write_file":
        # TODO: Write arguments['content'] to arguments['filename']
        pass
        
    elif name == "list_files":
        # TODO: List files in demo_files directory
        pass
    
    else:
        raise ValueError(f"Unknown tool: {name}")

# TODO: Part 3 - Implement resource access
@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """
    Read and return the contents of a resource.
    
    TODO: Parse the URI to get the filename and return file contents
    HINT: URI will be like "file://demo_files/example.txt"
    """
    # TODO: Extract filename from URI
    # TODO: Read file contents
    # TODO: Return contents as string
    pass

async def main():
    """Main function to run the MCP server."""
    # TODO: Get command line arguments for transport
    if len(sys.argv) != 2:
        print("Usage: python server.py <transport>")
        print("Transport options: stdio, sse")
        sys.exit(1)
    
    transport = sys.argv[1]
    
    # TODO: Run the server with the specified transport
    if transport == "stdio":
        # TODO: Import and use stdio transport
        pass
    elif transport == "sse":
        # TODO: Import and use SSE transport
        pass
    else:
        raise ValueError(f"Unknown transport: {transport}")

if __name__ == "__main__":
    # TODO: Run the main function
    pass


# HELPFUL HINTS:
#
# 1. MCP Server Structure:
#    - Use @server.list_tools() to register tool list handler
#    - Use @server.call_tool() to register tool execution handler
#    - Use @server.list_resources() to register resource list handler
#    - Use @server.read_resource() to register resource read handler
#
# 2. Tool Schema Example:
#    {
#        "type": "object",
#        "properties": {
#            "param_name": {"type": "string", "description": "Parameter description"}
#        },
#        "required": ["param_name"]
#    }
#
# 3. Return Types:
#    - Tools should return List[types.TextContent]
#    - Use types.TextContent(type="text", text="your result") to return text
#
# 4. Error Handling:
#    - Always handle errors gracefully
#    - Return meaningful error messages to the AI model
#
# 5. File Operations:
#    - Use pathlib.Path for file operations
#    - Create demo_files directory if it doesn't exist
#    - Handle file not found errors
