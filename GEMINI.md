# Gemini Code Assistant Context

This document provides context for the Gemini Code Assistant to understand the `arxiv-mcp-server` project.

## Project Overview

The `arxiv-mcp-server` is a Python-based MCP (Model Context Protocol) server that enables a large language model to search and download papers from the arXiv repository using natural language queries.

The server exposes a set of tools to the language model, allowing it to perform the following actions:

*   **Search arXiv:** Search for papers using natural language queries, which are parsed into structured queries for the arXiv API.
*   **Download Papers:** Download papers by their arXiv ID.
*   **Batch Download:** Download multiple papers at once.
*   **Search and Download:** Search for papers and immediately download selected results.
*   **Get Download Statistics:** Retrieve statistics about downloaded papers.

The project uses the following main technologies:

*   **Python 3.9+**
*   **fastmcp:** For creating the MCP server.
*   **arxiv:** A Python library for accessing the arXiv API.
*   **openai:** For parsing natural language queries (optional).
*   **pydantic:** For data validation and settings management.
*   **aiofiles** and **httpx:** For asynchronous file and HTTP operations.

## Building and Running

### Prerequisites

*   Python 3.9 or higher
*   pip

### Installation

1.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r arxiv-mcp-server/requirements.txt
    ```

### Running the Server

The server can be run in two modes:

1.  **Standalone Mode (for testing):**

    ```bash
    python arxiv-mcp-server/src/server.py
    ```

2.  **STDIO Mode (for MCP):**

    ```bash
    python arxiv-mcp-server/src/server.py --stdio
    ```

### Testing

To run the tests, execute the following command:

```bash
python arxiv-mcp-server/test_server.py
```

## Development Conventions

*   **Code Style:** The code follows the PEP 8 style guide.
*   **Typing:** The code uses type hints for all functions and methods.
*   **Asynchronous Operations:** The server uses `asyncio` for all I/O-bound operations, such as making HTTP requests and writing files.
*   **Configuration:** The server is configured using environment variables, with an `.env.example` file provided for reference.
*   **Dependencies:** Project dependencies are managed in `pyproject.toml` and `requirements.txt`.
*   **Modular Design:** The code is organized into modules with specific responsibilities:
    *   `server.py`: Handles the MCP server and tool definitions.
    *   `arxiv_search.py`: Manages interactions with the arXiv API.
    *   `query_parser.py`: Parses natural language queries.
    *   `models.py`: Defines the data models used in the application.
