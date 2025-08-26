#!/usr/bin/env python3
"""Test script for ArXiv MCP server functionality."""

import asyncio
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.arxiv_search import ArxivClient
from src.query_parser import QueryParser
from src.models import SearchQuery


async def test_search():
    """Test basic search functionality."""
    print("Testing ArXiv search...")
    print("-" * 50)
    
    client = ArxivClient()
    
    # Test 1: Simple keyword search
    print("\n1. Testing keyword search for 'quantum computing'...")
    result = await client.search("quantum computing", max_results=3)
    print(f"   Found {result.total_results} papers")
    if result.papers:
        print(f"   First paper: {result.papers[0].title}")
    
    # Test 2: Search with structured query
    print("\n2. Testing structured search...")
    query = SearchQuery(
        keywords=["transformer", "attention"],
        categories=["cs.LG"],
        max_results=3
    )
    arxiv_query = client.build_query_string(query)
    print(f"   Query string: {arxiv_query}")
    result = await client.search(arxiv_query, search_query=query)
    print(f"   Found {result.total_results} papers")
    
    return result


async def test_query_parser():
    """Test natural language query parsing."""
    print("\nTesting query parser...")
    print("-" * 50)
    
    parser = QueryParser()
    
    test_queries = [
        "Find math papers about combinatorics published after December 2024",
        "Papers by Yann LeCun on deep learning",
        "Recent quantum physics papers",
        "10 papers on natural language processing"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        try:
            # Test simple parser (always available)
            parsed = parser.parse_simple(query)
            print(f"   Parsed (simple): {json.dumps(parsed.model_dump(), indent=2)}")
        except Exception as e:
            print(f"   Error: {e}")


async def test_download():
    """Test paper download functionality."""
    print("\nTesting download functionality...")
    print("-" * 50)
    
    client = ArxivClient()
    
    # Search for a paper first
    print("\n1. Searching for a test paper...")
    result = await client.search("quantum", max_results=1)
    
    if result.papers:
        paper = result.papers[0]
        print(f"   Found: {paper.title}")
        print(f"   ArXiv ID: {paper.arxiv_id}")
        
        # Test download
        print("\n2. Testing download...")
        download_result = await client.download_paper(paper)
        
        if download_result.success:
            print(f"   Success! Downloaded to: {download_result.file_path}")
        else:
            print(f"   Failed: {download_result.error}")
    else:
        print("   No papers found to test download")


async def main():
    """Run all tests."""
    print("=" * 50)
    print("ArXiv MCP Server Test Suite")
    print("=" * 50)
    
    try:
        # Test search
        search_result = await test_search()
        
        # Test query parser
        await test_query_parser()
        
        # Test download (optional - comment out if you don't want to download)
        # await test_download()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())