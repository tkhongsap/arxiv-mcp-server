"""Data models for ArXiv MCP server."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Structured search query parsed from natural language."""
    
    keywords: Optional[List[str]] = Field(default=None, description="Search keywords")
    title: Optional[str] = Field(default=None, description="Search in title")
    author: Optional[str] = Field(default=None, description="Author name")
    abstract: Optional[str] = Field(default=None, description="Search in abstract")
    categories: Optional[List[str]] = Field(default=None, description="ArXiv categories (e.g., math.CO, cs.AI)")
    date_from: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD)")
    max_results: int = Field(default=10, description="Maximum number of results")


class PaperInfo(BaseModel):
    """Information about an arXiv paper."""
    
    arxiv_id: str = Field(description="ArXiv identifier")
    title: str = Field(description="Paper title")
    authors: List[str] = Field(description="List of authors")
    abstract: str = Field(description="Paper abstract")
    categories: List[str] = Field(description="ArXiv categories")
    published: datetime = Field(description="Publication date")
    updated: datetime = Field(description="Last update date")
    pdf_url: str = Field(description="URL to PDF")
    comment: Optional[str] = Field(default=None, description="Author comments")
    journal_ref: Optional[str] = Field(default=None, description="Journal reference")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract[:500] + "..." if len(self.abstract) > 500 else self.abstract,
            "categories": self.categories,
            "published": self.published.isoformat(),
            "updated": self.updated.isoformat(),
            "pdf_url": self.pdf_url,
            "comment": self.comment,
            "journal_ref": self.journal_ref
        }


class SearchResult(BaseModel):
    """Search results from arXiv."""
    
    query: str = Field(description="Original search query")
    total_results: int = Field(description="Total number of results found")
    papers: List[PaperInfo] = Field(description="List of papers")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "query": self.query,
            "total_results": self.total_results,
            "papers": [paper.to_dict() for paper in self.papers]
        }


class DownloadResult(BaseModel):
    """Result of downloading a paper."""
    
    arxiv_id: str = Field(description="ArXiv identifier")
    title: str = Field(description="Paper title")
    file_path: str = Field(description="Path to downloaded file")
    success: bool = Field(description="Whether download was successful")
    error: Optional[str] = Field(default=None, description="Error message if failed")