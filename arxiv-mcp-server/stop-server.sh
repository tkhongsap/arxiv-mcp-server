#!/bin/bash

# ArXiv MCP Server Stop Script
echo "Stopping ArXiv MCP Server..."

# Try to read PID file first
if [ -f /tmp/arxiv-mcp-server.pid ]; then
    PID=$(cat /tmp/arxiv-mcp-server.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "Stopped server with PID: $PID"
        rm /tmp/arxiv-mcp-server.pid
    else
        echo "Process with PID $PID not found, searching for process..."
        rm /tmp/arxiv-mcp-server.pid
    fi
fi

# Also try pkill in case PID file is missing or outdated
if pgrep -f "python.*src.server.*stdio" > /dev/null; then
    pkill -f "python.*src.server.*stdio"
    echo "ArXiv MCP server processes stopped"
else
    echo "No ArXiv MCP server process found running"
fi

# Clean up log files
if [ -f /tmp/arxiv-mcp-server.log ]; then
    echo "Cleaning up log file..."
    rm -f /tmp/arxiv-mcp-server.log
fi

echo "ArXiv MCP server stopped and cleaned up"