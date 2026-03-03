#!/usr/bin/env python3
"""
Unified MCP Server - Google Services, GitHub, and Antigravity
Works with any MCP client via stdio
"""

import sys
import json
import asyncio
import os
import requests
import webbrowser
from pathlib import Path

# MCP Imports
from mcp.server import Server
from mcp.types import Tool, TextContent

# Add project root to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Local Service Imports (Ensure these files exist in your src/ folder)
import src.google_sheets as sheets
import src.google_gmail as gmail
import src.google_calendar as calendar

def load_config():
    try:
        config_path = Path(__file__).parent.parent / 'config.json'
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {'google': {}}

config = load_config()
server = Server("unified-mcp-server")

@server.list_tools()
async def list_tools():
    return [
        # --- GOOGLE SHEETS ---
        Tool(
            name="read_sheet",
            description="Read data from a Google Sheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheetId": {"type": "string"},
                    "range": {"type": "string", "description": "e.g. 'Sheet1!A1:B10'"}
                },
                "required": ["spreadsheetId", "range"]
            }
        ),
        # --- GMAIL ---
        Tool(
            name="list_emails",
            description="List recent emails from Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "maxResults": {"type": "integer", "default": 10},
                    "query": {"type": "string", "default": ""}
                }
            }
        ),
        # --- CALENDAR ---
        Tool(
            name="list_calendar_events",
            description="List upcoming calendar events",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendarId": {"type": "string", "default": "primary"},
                    "maxResults": {"type": "integer", "default": 10}
                }
            }
        ),
        # --- GITHUB ---
        Tool(
            name="list_github_repos",
            description="List repositories for the authenticated GitHub user",
            inputSchema={"type": "object", "properties": {}}
        ),
        # --- ANTIGRAVITY ---
        Tool(
            name="engage_antigravity",
            description="Enable Python's secret antigravity flight mode (opens XKCD comic)",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        result = None
        
        # 1. Google Sheets Logic
        if name == "read_sheet":
            sid = arguments.get("spreadsheetId") or config.get("google", {}).get("spreadsheetId")
            result = sheets.read_sheet_data(sid, arguments["range"])
        
        # 2. Gmail Logic
        elif name == "list_emails":
            result = gmail.list_emails(arguments.get("maxResults", 10), arguments.get("query", ""))
        
        # 3. Calendar Logic
        elif name == "list_calendar_events":
            cid = arguments.get("calendarId") or config.get("google", {}).get("calendarId", "primary")
            result = calendar.list_events(cid, arguments.get("maxResults", 10))
            
        # 4. GitHub Logic
        elif name == "list_github_repos":
            token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
            if not token:
                result = {"error": "GitHub token missing in environment variables"}
            else:
                headers = {"Authorization": f"token {token}"}
                resp = requests.get("https://api.github.com/user/repos", headers=headers)
                result = resp.json() if resp.status_code == 200 else {"error": resp.text}

        # 5. Antigravity Logic
        elif name == "engage_antigravity":
            # The classic Python joke
            url = "https://xkcd.com/353/"
            webbrowser.open(url)
            result = {"status": "Antigravity engaged. Opening flight manual (XKCD 353).", "url": url}

        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as error:
        return [TextContent(type="text", text=json.dumps({"success": False, "error": str(error)}, indent=2))]

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())