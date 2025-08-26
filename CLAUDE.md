# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains an MCP (Model Context Protocol) server implementation for searching and downloading academic papers from arXiv. The main production code is in `/arxiv-mcp-server/`, with structured development workflows in `/prd-driven-workflow/`.

## Common Development Commands

### Running the MCP Server
```bash
cd arxiv-mcp-server
python -m src.server --stdio
```

### Running Tests
```bash
cd arxiv-mcp-server
python test_server.py
```

### Installing Dependencies
```bash
cd arxiv-mcp-server
pip install -r requirements.txt
# or for development
pip install -e .
```

## Architecture and Project Structure

### Core Components
- **MCP Server** (`src/server.py`): Exposes 5 tools to Claude for arXiv operations
- **Query Parser** (`src/query_parser.py`): Converts natural language to structured arXiv queries using OpenAI (optional) or rule-based parsing
- **Search Engine** (`src/arxiv_search.py`): Handles arXiv API interactions with rate limiting (3-second delays)
- **Data Models** (`src/models.py`): Pydantic models for type safety and validation

### MCP Tools Exposed
1. `search_arxiv`: Natural language search for papers
2. `download_paper`: Download single paper by ID
3. `batch_download`: Download multiple papers
4. `search_and_download`: Combined search and download
5. `get_download_stats`: Retrieve download statistics

### Key Design Patterns
- **Async/await throughout**: All I/O operations are non-blocking
- **Rate limiting**: Built-in 3-second delays for arXiv API compliance
- **File organization**: Downloads stored in `downloads/YYYY-MM/category/` structure
- **Error handling**: Comprehensive exception handling with informative messages

## Development Workflows

The repository follows a PRD-driven development approach with structured workflows in `.cursor/rules/`:
- **PRD-driven workflow**: Start with product requirements document
- **Architecture design**: Technical planning before implementation
- **Test generation**: Automated test creation
- **Review-driven**: Code review and validation
- **Refactoring**: Technical debt management

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Optional, enables AI-powered query parsing
- `ARXIV_DOWNLOAD_DIR`: Custom download directory (default: `./downloads`)
- `PYTHONPATH`: Should include arxiv-mcp-server directory

### MCP Server Configuration
Use `arxiv-mcp-server/claude-config-example.json` as template for Claude Code integration.

## Important Notes

1. **Rate Limiting**: Always respect arXiv's 3-second delay between API calls
2. **Query Parser**: Has two modes - OpenAI-powered (if API key provided) or rule-based fallback
3. **File Naming**: Papers saved as `{arxiv_id}_{sanitized_title}.pdf`
4. **Category Mapping**: Automatic conversion of common terms to arXiv categories (e.g., "machine learning" → "cs.LG")
5. **Date Filtering**: Supports natural language dates like "after December 2024"