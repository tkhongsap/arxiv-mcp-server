---
allowed-tools: Bash, KillBash
description: Stop the running ArXiv MCP server
---

Stop the ArXiv MCP server that's running in the background.

First, let me find the running server process:
!ps aux | grep -E "python.*src.server.*stdio" | grep -v grep | head -5

Now I'll stop the server:
!pkill -f "python.*src.server.*stdio" 2>/dev/null && echo "ArXiv MCP server stopped successfully" || echo "No ArXiv MCP server process found running"

Let me verify it's stopped:
!sleep 1 && ps aux | grep -E "python.*src.server.*stdio" | grep -v grep | head -5 || echo "Confirmed: ArXiv MCP server is not running"

Clean up the log file:
!rm -f /tmp/arxiv-mcp-server.log 2>/dev/null && echo "Log file cleaned up" || echo "No log file to clean"

The ArXiv MCP server has been stopped. Use `/start-arxiv-search-mcp` to start it again when needed.