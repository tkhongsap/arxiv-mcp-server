"""ArXiv API integration for searching and downloading papers."""

import os
import re
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import arxiv
import aiofiles
import httpx
from .models import SearchQuery, PaperInfo, SearchResult, DownloadResult


class ArxivClient:
    """Client for interacting with arXiv API."""
    
    def __init__(self, download_dir: Optional[str] = None):
        """Initialize ArXiv client.
        
        Args:
            download_dir: Directory for downloading papers
        """
        self.download_dir = Path(download_dir or os.getenv("ARXIV_DOWNLOAD_DIR", "./downloads"))
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.client = arxiv.Client()
    
    def build_query_string(self, search_query: SearchQuery) -> str:
        """Build arXiv query string from structured query.
        
        Args:
            search_query: Structured search query
            
        Returns:
            ArXiv API query string
        """
        query_parts = []
        
        # Add keywords
        if search_query.keywords:
            keyword_query = " AND ".join(f'all:"{kw}"' for kw in search_query.keywords)
            query_parts.append(f"({keyword_query})")
        
        # Add title search
        if search_query.title:
            query_parts.append(f'ti:"{search_query.title}"')
        
        # Add author search
        if search_query.author:
            query_parts.append(f'au:"{search_query.author}"')
        
        # Add abstract search
        if search_query.abstract:
            query_parts.append(f'abs:"{search_query.abstract}"')
        
        # Add category filter
        if search_query.categories:
            cat_query = " OR ".join(f'cat:{cat}' for cat in search_query.categories)
            query_parts.append(f"({cat_query})")
        
        # Combine all parts
        if not query_parts:
            # Default to recent papers if no specific query
            query_parts.append("all:*")
        
        query_string = " AND ".join(query_parts)
        
        # Add date filtering if specified
        if search_query.date_from or search_query.date_to:
            # Note: arXiv API doesn't directly support date filtering in query
            # We'll filter results after fetching
            pass
        
        return query_string
    
    async def search(self, query: str, search_query: Optional[SearchQuery] = None, 
                    max_results: int = 10) -> SearchResult:
        """Search arXiv for papers.
        
        Args:
            query: Natural language query or arXiv query string
            search_query: Optional structured query object
            max_results: Maximum number of results
            
        Returns:
            SearchResult with papers
        """
        # If we have a structured query, build the query string
        if search_query:
            arxiv_query = self.build_query_string(search_query)
            max_results = search_query.max_results
        else:
            arxiv_query = query
        
        # Create search
        search = arxiv.Search(
            query=arxiv_query,
            max_results=max_results * 2,  # Fetch extra for date filtering
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        # Execute search
        papers = []
        try:
            results = list(self.client.results(search))
            
            for result in results:
                # Date filtering if needed
                if search_query and (search_query.date_from or search_query.date_to):
                    published = result.published.replace(tzinfo=None)
                    
                    if search_query.date_from:
                        date_from = datetime.strptime(search_query.date_from, "%Y-%m-%d")
                        if published < date_from:
                            continue
                    
                    if search_query.date_to:
                        date_to = datetime.strptime(search_query.date_to, "%Y-%m-%d")
                        if published > date_to:
                            continue
                
                # Create PaperInfo
                paper = PaperInfo(
                    arxiv_id=result.entry_id.split("/")[-1],
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    categories=result.categories,
                    published=result.published.replace(tzinfo=None),
                    updated=result.updated.replace(tzinfo=None),
                    pdf_url=result.pdf_url,
                    comment=result.comment,
                    journal_ref=result.journal_ref
                )
                papers.append(paper)
                
                if len(papers) >= max_results:
                    break
        
        except Exception as e:
            print(f"Search error: {e}")
        
        return SearchResult(
            query=query,
            total_results=len(papers),
            papers=papers
        )
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for saving.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    async def download_paper(self, paper: PaperInfo, custom_dir: Optional[str] = None) -> DownloadResult:
        """Download a paper PDF.
        
        Args:
            paper: Paper information
            custom_dir: Optional custom download directory
            
        Returns:
            DownloadResult with file path
        """
        try:
            # Determine download directory
            download_dir = Path(custom_dir) if custom_dir else self.download_dir
            
            # Create subdirectory based on date and category
            date_dir = paper.published.strftime("%Y-%m")
            category_dir = paper.categories[0].replace(".", "_") if paper.categories else "uncategorized"
            full_dir = download_dir / date_dir / category_dir
            full_dir.mkdir(parents=True, exist_ok=True)
            
            # Create filename
            title_safe = self._sanitize_filename(paper.title)
            filename = f"{paper.arxiv_id}_{title_safe}.pdf"
            file_path = full_dir / filename
            
            # Check if already downloaded
            if file_path.exists():
                return DownloadResult(
                    arxiv_id=paper.arxiv_id,
                    title=paper.title,
                    file_path=str(file_path),
                    success=True,
                    error=None
                )
            
            # Download PDF
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(paper.pdf_url)
                response.raise_for_status()
                
                # Save to file
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(response.content)
            
            return DownloadResult(
                arxiv_id=paper.arxiv_id,
                title=paper.title,
                file_path=str(file_path),
                success=True,
                error=None
            )
        
        except Exception as e:
            return DownloadResult(
                arxiv_id=paper.arxiv_id,
                title=paper.title,
                file_path="",
                success=False,
                error=str(e)
            )
    
    async def download_by_id(self, arxiv_id: str, custom_dir: Optional[str] = None) -> DownloadResult:
        """Download a paper by its arXiv ID.
        
        Args:
            arxiv_id: ArXiv identifier
            custom_dir: Optional custom download directory
            
        Returns:
            DownloadResult with file path
        """
        # Search for the specific paper
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(self.client.results(search))
        
        if not results:
            return DownloadResult(
                arxiv_id=arxiv_id,
                title="",
                file_path="",
                success=False,
                error=f"Paper {arxiv_id} not found"
            )
        
        result = results[0]
        paper = PaperInfo(
            arxiv_id=result.entry_id.split("/")[-1],
            title=result.title,
            authors=[author.name for author in result.authors],
            abstract=result.summary,
            categories=result.categories,
            published=result.published.replace(tzinfo=None),
            updated=result.updated.replace(tzinfo=None),
            pdf_url=result.pdf_url,
            comment=result.comment,
            journal_ref=result.journal_ref
        )
        
        return await self.download_paper(paper, custom_dir)
    
    async def batch_download(self, papers: List[PaperInfo], custom_dir: Optional[str] = None,
                           delay: float = 3.0) -> List[DownloadResult]:
        """Download multiple papers with rate limiting.
        
        Args:
            papers: List of papers to download
            custom_dir: Optional custom download directory
            delay: Delay between downloads in seconds
            
        Returns:
            List of DownloadResults
        """
        results = []
        
        for i, paper in enumerate(papers):
            if i > 0:
                # Rate limiting
                await asyncio.sleep(delay)
            
            result = await self.download_paper(paper, custom_dir)
            results.append(result)
        
        return results