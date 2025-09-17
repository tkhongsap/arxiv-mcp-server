---
allowed-tools: Bash, BashOutput, LS, Read
description: Start the ArXiv MCP server for searching and downloading papers from arXiv
---

Start the ArXiv MCP server to enable natural language search and download of papers from arXiv.

First, let me check if the server is already running:
!ps aux | grep -E "python.*src.server.*stdio" | grep -v grep | head -5

Now I'll start the server in the background:
!cd /home/tkhongsap/my-github/arxiv/arxiv-mcp-server && source venv/bin/activate && python -m src.server --stdio > /tmp/arxiv-mcp-server.log 2>&1 & echo "ArXiv MCP server starting with PID: $!"

Let me verify the server is running:
!sleep 2 && ps aux | grep -E "python.*src.server.*stdio" | grep -v grep | head -5

Check the server log for any startup issues:
!tail -n 10 /tmp/arxiv-mcp-server.log 2>/dev/null || echo "Log file not yet created"

The ArXiv MCP server is now available! You can use these natural language commands:

**Search Examples:**
- "Search arXiv for recent papers on quantum computing"
- "Find math papers about combinatorics published after December 2024"
- "Show me papers by Yann LeCun on deep learning"

**Download Examples:**
- "Download arXiv paper 2401.12345"
- "Download papers with IDs 2401.01234, 2401.05678"

**Combined Operations:**
- "Find 5 recent papers on transformers and download the first 3"
- "Search for machine learning papers and download all of them"

**Check Downloads:**
- "Show me download statistics"

The server will continue running in the background. Use `/stop-arxiv-search-mcp` to stop it when done.