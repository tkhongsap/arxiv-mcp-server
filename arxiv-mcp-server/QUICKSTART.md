# Quick Start Guide

## 1. Installation (5 minutes)

```bash
# Clone and enter directory
cd /home/tkhongsap/my-github/arxiv/arxiv-mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Set OpenAI API key for better natural language parsing
export OPENAI_API_KEY="your-api-key-here"
```

## 2. Test the Server

```bash
# Run test script
python test_server.py

# Or test manually
python -m src.server
```

## 3. Configure Claude Code

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "arxiv-search": {
      "command": "/home/tkhongsap/my-github/arxiv/arxiv-mcp-server/venv/bin/python",
      "args": ["-m", "src.server", "--stdio"],
      "cwd": "/home/tkhongsap/my-github/arxiv/arxiv-mcp-server",
      "env": {
        "ARXIV_DOWNLOAD_DIR": "/home/tkhongsap/my-github/arxiv/arxiv-mcp-server/downloads",
        "PYTHONPATH": "/home/tkhongsap/my-github/arxiv/arxiv-mcp-server"
      }
    }
  }
}
```

## 4. Use in Claude Code

After restarting Claude Code, you can use commands like:

### Example 1: Search for Papers
"Search arXiv for math papers about combinatorics published after December 2024"

Claude will use the `search_arxiv` tool and show you results.

### Example 2: Download Specific Papers
"Download arXiv paper 2312.01234"

### Example 3: Search and Download
"Find 5 recent papers on quantum computing and download the first 3"

## Common Usage Patterns

### Research Workflow
1. "Search for recent papers on [your topic]"
2. Review the results
3. "Download papers 1, 3, and 5" (or specify by arXiv ID)

### Bulk Download
"Find all papers by [author name] from 2024 and download them all"

### Category-Specific Search
"Show me the latest 10 papers in machine learning (cs.LG)"

## Tips

- Papers are saved to `downloads/YYYY-MM/category/` automatically
- Use specific date ranges for focused searches
- Combine author names with topics for precise results
- The server handles rate limiting automatically

## Need Help?

- Check `README.md` for detailed documentation
- Run `python test_server.py` to verify setup
- Review `test_server.py` for usage examples