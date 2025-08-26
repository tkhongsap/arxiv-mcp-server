"""MCP server for arXiv search and download."""

import os
import sys
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from src.models import SearchQuery, PaperInfo, SearchResult, DownloadResult
from src.query_parser import QueryParser
from src.arxiv_search import ArxivClient

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("ArXiv Search Assistant")

# Initialize components
query_parser = QueryParser()
arxiv_client = ArxivClient()


@mcp.tool()
async def search_arxiv(
    query: str,
    max_results: int = 10,
    use_natural_language: bool = True
) -> Dict[str, Any]:
    """
    Search arXiv papers using natural language or structured queries.
    
    Args:
        query: Natural language query (e.g., "quantum computing papers after 2024") 
               or arXiv query string (e.g., "cat:quant-ph AND ti:quantum")
        max_results: Maximum number of results to return (default: 10, max: 50)
        use_natural_language: Whether to parse as natural language (default: True)
    
    Returns:
        Dictionary containing search results with paper metadata
    
    Examples:
        - "Find recent papers about transformer architectures in computer vision"
        - "Mathematics papers on combinatorics published after December 2024"
        - "Papers by Yann LeCun on deep learning"
    """
    # Limit max results
    max_results = min(max_results, 50)
    
    try:
        # Parse query if using natural language
        search_query = None
        if use_natural_language:
            try:
                search_query = query_parser.parse(query)
                search_query.max_results = max_results
            except Exception as e:
                print(f"Failed to parse query: {e}, using raw query")
        
        # Search arXiv
        result = await arxiv_client.search(
            query=query,
            search_query=search_query,
            max_results=max_results
        )
        
        # Format response
        papers_info = []
        for i, paper in enumerate(result.papers, 1):
            paper_dict = paper.to_dict()
            paper_dict["index"] = i  # Add index for easy selection
            papers_info.append(paper_dict)
        
        return {
            "success": True,
            "query": query,
            "parsed_query": search_query.model_dump() if search_query else None,
            "total_results": result.total_results,
            "papers": papers_info
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


@mcp.tool()
async def download_paper(
    arxiv_id: str,
    custom_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Download a paper PDF by its arXiv ID.
    
    Args:
        arxiv_id: ArXiv identifier (e.g., "2312.01234" or "math.CO/0601001")
        custom_dir: Optional custom download directory (default: ./downloads)
    
    Returns:
        Dictionary with download status and file path
    
    Example:
        download_paper("2312.01234")
    """
    try:
        # Clean arxiv_id (remove version if present)
        if "v" in arxiv_id:
            arxiv_id = arxiv_id.split("v")[0]
        
        result = await arxiv_client.download_by_id(arxiv_id, custom_dir)
        
        return {
            "success": result.success,
            "arxiv_id": result.arxiv_id,
            "title": result.title,
            "file_path": result.file_path,
            "error": result.error
        }
    
    except Exception as e:
        return {
            "success": False,
            "arxiv_id": arxiv_id,
            "error": str(e)
        }


@mcp.tool()
async def batch_download(
    arxiv_ids: List[str],
    custom_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Download multiple papers at once.
    
    Args:
        arxiv_ids: List of arXiv identifiers
        custom_dir: Optional custom download directory (default: ./downloads)
    
    Returns:
        Dictionary with download results for each paper
    
    Example:
        batch_download(["2312.01234", "2401.05678", "2402.09876"])
    """
    try:
        # Get paper info for each ID
        papers = []
        for arxiv_id in arxiv_ids:
            # Clean arxiv_id
            if "v" in arxiv_id:
                arxiv_id = arxiv_id.split("v")[0]
            
            # Search for the paper
            search_result = await arxiv_client.search(
                query=f"id:{arxiv_id}",
                max_results=1
            )
            
            if search_result.papers:
                papers.append(search_result.papers[0])
        
        if not papers:
            return {
                "success": False,
                "error": "No valid papers found",
                "requested_ids": arxiv_ids
            }
        
        # Download papers with rate limiting
        results = await arxiv_client.batch_download(papers, custom_dir)
        
        # Format response
        download_results = []
        for result in results:
            download_results.append({
                "arxiv_id": result.arxiv_id,
                "title": result.title,
                "success": result.success,
                "file_path": result.file_path if result.success else None,
                "error": result.error
            })
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        return {
            "success": True,
            "total_requested": len(arxiv_ids),
            "successful_downloads": successful,
            "failed_downloads": failed,
            "results": download_results
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "requested_ids": arxiv_ids
        }


@mcp.tool()
async def search_and_download(
    query: str,
    indices: Optional[List[int]] = None,
    download_all: bool = False,
    max_results: int = 10,
    custom_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search arXiv and immediately download selected papers.
    
    Args:
        query: Natural language search query
        indices: List of paper indices to download (1-based, e.g., [1, 3, 5])
        download_all: Download all search results (default: False)
        max_results: Maximum number of search results (default: 10)
        custom_dir: Optional custom download directory
    
    Returns:
        Dictionary with search results and download status
    
    Examples:
        - search_and_download("quantum computing 2024", indices=[1, 2, 3])
        - search_and_download("machine learning transformers", download_all=True, max_results=5)
    """
    try:
        # First, search for papers
        search_result = await search_arxiv(query, max_results, use_natural_language=True)
        
        if not search_result["success"]:
            return search_result
        
        papers = search_result["papers"]
        
        if not papers:
            return {
                "success": True,
                "message": "No papers found",
                "search_result": search_result
            }
        
        # Determine which papers to download
        if download_all:
            indices_to_download = list(range(1, len(papers) + 1))
        elif indices:
            # Validate indices
            indices_to_download = [i for i in indices if 1 <= i <= len(papers)]
        else:
            return {
                "success": True,
                "message": "Search completed. Specify indices or use download_all=True to download papers.",
                "search_result": search_result
            }
        
        # Get arXiv IDs for selected papers
        arxiv_ids = [papers[i-1]["arxiv_id"] for i in indices_to_download]
        
        # Download selected papers
        download_result = await batch_download(arxiv_ids, custom_dir)
        
        return {
            "success": True,
            "search_result": search_result,
            "download_result": download_result,
            "message": f"Found {len(papers)} papers, downloaded {download_result.get('successful_downloads', 0)} papers"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


@mcp.tool()
async def get_download_stats() -> Dict[str, Any]:
    """
    Get statistics about downloaded papers.
    
    Returns:
        Dictionary with download directory information and statistics
    """
    try:
        download_dir = arxiv_client.download_dir
        
        # Count PDF files
        pdf_files = list(download_dir.rglob("*.pdf"))
        
        # Get directory structure
        categories = {}
        for pdf in pdf_files:
            # Get category from path
            parts = pdf.relative_to(download_dir).parts
            if len(parts) >= 2:
                date_dir = parts[0]
                category_dir = parts[1]
                
                if date_dir not in categories:
                    categories[date_dir] = {}
                
                if category_dir not in categories[date_dir]:
                    categories[date_dir][category_dir] = 0
                
                categories[date_dir][category_dir] += 1
        
        # Calculate total size
        total_size = sum(pdf.stat().st_size for pdf in pdf_files)
        total_size_mb = total_size / (1024 * 1024)
        
        return {
            "success": True,
            "download_directory": str(download_dir),
            "total_papers": len(pdf_files),
            "total_size_mb": round(total_size_mb, 2),
            "organization": categories,
            "recent_downloads": [str(pdf.name) for pdf in sorted(pdf_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]]
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Run the MCP server."""
    import sys
    
    # Check if running in stdio mode
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        # Run in stdio mode for MCP
        mcp.run(transport="stdio")
    else:
        # Run standalone for testing
        print("ArXiv MCP Server")
        print("================")
        print("This server provides tools for searching and downloading arXiv papers.")
        print("\nAvailable tools:")
        print("- search_arxiv: Search papers using natural language")
        print("- download_paper: Download a single paper by ID")
        print("- batch_download: Download multiple papers")
        print("- search_and_download: Search and download in one step")
        print("- get_download_stats: Get download statistics")
        print("\nTo use with Claude Code, add to your MCP configuration.")
        print("To test, run with --stdio flag.")


if __name__ == "__main__":
    main()