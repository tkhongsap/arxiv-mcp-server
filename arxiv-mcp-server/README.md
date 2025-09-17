# ArXiv MCP Server

An MCP (Model Context Protocol) server that enables Claude Code to search and download papers from arXiv using natural language queries.

## Features

- **Natural Language Search**: Search arXiv using queries like "math papers about combinatorics published after Dec 2024"
- **Smart Query Parsing**: Automatically converts natural language to structured arXiv API queries
- **PDF Downloads**: Download papers directly to organized folders
- **Batch Operations**: Download multiple papers at once
- **Category Support**: Search within specific arXiv categories (math, cs, physics, etc.)
- **Date Filtering**: Find papers published within specific date ranges
- **Rate Limiting**: Built-in compliance with arXiv API rate limits
- **Download Statistics**: Track and retrieve download history

## Installation

### Prerequisites

- Python 3.9 or higher
- Claude Code with MCP support
- OpenAI API key (optional, for enhanced natural language parsing)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd arxiv-mcp-server
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key (optional)
```

## Configuration

### Adding to Claude Code

Add the following to your Claude Code MCP configuration file:

```json
{
  "mcpServers": {
    "arxiv-search": {
      "command": "/path/to/arxiv-mcp-server/venv/bin/python",
      "args": ["-m", "src.server", "--stdio"],
      "cwd": "/path/to/arxiv-mcp-server",
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key",
        "ARXIV_DOWNLOAD_DIR": "/path/to/downloads",
        "PYTHONPATH": "/path/to/arxiv-mcp-server"
      }
    }
  }
}
```

### Environment Variables

- `OPENAI_API_KEY`: (Optional) OpenAI API key for enhanced natural language parsing
- `ARXIV_DOWNLOAD_DIR`: Directory for downloading papers (default: `./downloads`)
- `MAX_SEARCH_RESULTS`: Default maximum results per search (default: 10)

## Usage

Once configured, the MCP server provides the following tools in Claude Code:

### 1. Search ArXiv

Search for papers using natural language:

```
search_arxiv(query="quantum computing papers published after 2024", max_results=10)
```

Examples:
- "Find recent papers about transformer architectures in computer vision"
- "Mathematics papers on combinatorics published after December 2024"
- "Papers by Yann LeCun on deep learning"
- "10 most recent papers on natural language processing"

### 2. Download Paper

Download a single paper by its arXiv ID:

```
download_paper(arxiv_id="2312.01234")
```

### 3. Batch Download

Download multiple papers at once:

```
batch_download(arxiv_ids=["2312.01234", "2401.05678", "2402.09876"])
```

### 4. Search and Download

Search and immediately download selected papers:

```
search_and_download(
    query="quantum computing 2024",
    indices=[1, 2, 3],  # Download papers 1, 2, and 3 from results
    max_results=10
)
```

Or download all results:

```
search_and_download(
    query="machine learning transformers",
    download_all=True,
    max_results=5
)
```

### 5. Get Download Statistics

View statistics about downloaded papers:

```
get_download_stats()
```

## Natural Language Query Examples

The server understands various natural language patterns:

### Subject/Category Queries
- "mathematics papers" → searches in math categories
- "computer science AI papers" → searches in cs.AI
- "quantum physics research" → searches in quant-ph

### Date Filtering
- "papers published after December 2024"
- "articles since January 2024"
- "research before 2023"
- "papers in 2024"

### Author Searches
- "papers by Geoffrey Hinton"
- "research by LeCun and Bengio"

### Keyword Searches
- "papers about transformer architecture"
- "research on graph neural networks"
- "articles about quantum entanglement"

### Combined Queries
- "10 machine learning papers by Yoshua Bengio published after 2023"
- "Recent computer vision papers about object detection"

## File Organization

Downloaded papers are automatically organized:

```
downloads/
├── 2024-12/
│   ├── cs_AI/
│   │   ├── 2412.01234_Paper_Title.pdf
│   │   └── 2412.05678_Another_Paper.pdf
│   └── math_CO/
│       └── 2412.09876_Math_Paper.pdf
└── 2025-01/
    └── physics/
        └── 2501.01234_Physics_Paper.pdf
```

Papers are organized by:
- Year-Month of publication
- Primary arXiv category
- Named with arXiv ID and sanitized title

## Testing

Run the test script to verify functionality:

```bash
source venv/bin/activate
python test_server.py
```

## Limitations

- Rate limiting: 3-second delay between batch downloads (arXiv API requirement)
- Maximum 50 results per search (configurable)
- OpenAI API key required for optimal natural language parsing (falls back to simple parser)

## Troubleshooting

### Server not appearing in Claude Code
1. Check that the MCP configuration path is correct
2. Ensure Python path in configuration points to the virtual environment
3. Restart Claude Code after configuration changes

### Natural language parsing not working
1. Verify OpenAI API key is set correctly
2. Check API key has sufficient credits
3. Server falls back to simple parsing if LLM parsing fails

### Downloads failing
1. Check write permissions for download directory
2. Ensure internet connection is stable
3. Verify arXiv IDs are valid

## License

MIT License

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.