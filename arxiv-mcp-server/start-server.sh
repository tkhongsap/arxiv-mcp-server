#!/bin/bash

# ArXiv MCP Server Start Script
echo "Starting ArXiv MCP Server..."

# Navigate to the server directory
cd /home/tkhongsap/my-github/arxiv/arxiv-mcp-server || exit 1

# Activate virtual environment
source venv/bin/activate || {
    echo "Error: Could not activate virtual environment"
    echo "Make sure venv exists and dependencies are installed"
    exit 1
}

# Check if already running
if pgrep -f "python.*src.server.*stdio" > /dev/null; then
    echo "ArXiv MCP server is already running"
    echo "Use stop-server.sh or /stop-arxiv-search-mcp to stop it first"
    exit 0
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your OPENAI_API_KEY for better natural language parsing"
fi

# Start the server in background
nohup python -m src.server --stdio > /tmp/arxiv-mcp-server.log 2>&1 &
SERVER_PID=$!

# Save PID for later
echo $SERVER_PID > /tmp/arxiv-mcp-server.pid

echo "ArXiv MCP server started with PID: $SERVER_PID"
echo "Log file: /tmp/arxiv-mcp-server.log"
echo ""
echo "Server is ready for:"
echo "  - Natural language paper searches"
echo "  - PDF downloads to organized folders"
echo "  - Batch operations"
echo ""
echo "Use /stop-arxiv-search-mcp to stop the server"