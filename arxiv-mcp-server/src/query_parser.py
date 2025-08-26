"""Natural language query parser for arXiv searches."""

import os
import json
import re
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from openai import OpenAI
from pydantic import ValidationError
from .models import SearchQuery


class QueryParser:
    """Parse natural language queries into structured search parameters."""
    
    # Common category mappings
    CATEGORY_MAPPINGS = {
        "mathematics": ["math"],
        "combinatorics": ["math.CO"],
        "algebra": ["math.AG", "math.RA"],
        "geometry": ["math.DG", "math.AG"],
        "analysis": ["math.CA", "math.FA"],
        "probability": ["math.PR"],
        "statistics": ["stat", "math.ST"],
        "physics": ["physics"],
        "quantum": ["quant-ph"],
        "computer science": ["cs"],
        "artificial intelligence": ["cs.AI"],
        "machine learning": ["cs.LG", "stat.ML"],
        "computer vision": ["cs.CV"],
        "nlp": ["cs.CL"],
        "natural language": ["cs.CL"],
        "cryptography": ["cs.CR"],
        "biology": ["q-bio"],
        "finance": ["q-fin"],
        "economics": ["econ"],
    }
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the query parser.
        
        Args:
            openai_api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)
    
    def parse_with_llm(self, query: str) -> SearchQuery:
        """Parse query using OpenAI's structured output.
        
        Args:
            query: Natural language query
            
        Returns:
            Structured SearchQuery object
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        system_prompt = """You are an arXiv search query parser. Convert natural language queries into structured search parameters.

Extract the following information:
- keywords: General search terms
- title: If searching specifically in titles
- author: Author names
- abstract: If searching in abstracts
- categories: ArXiv category codes (e.g., math.CO for combinatorics, cs.AI for AI)
- date_from: Start date in YYYY-MM-DD format
- date_to: End date in YYYY-MM-DD format

Common category codes:
- Mathematics: math, math.CO (combinatorics), math.AG (algebraic geometry), math.PR (probability)
- Computer Science: cs, cs.AI (AI), cs.LG (machine learning), cs.CV (computer vision), cs.CL (NLP)
- Physics: physics, quant-ph (quantum physics), hep-th (high energy theory)
- Statistics: stat, stat.ML (machine learning)
- Biology: q-bio
- Finance: q-fin
- Economics: econ

For relative dates like "last month" or "after December 2024", calculate the actual dates."""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "search_query",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "keywords": {"type": "array", "items": {"type": "string"}},
                            "title": {"type": "string"},
                            "author": {"type": "string"},
                            "abstract": {"type": "string"},
                            "categories": {"type": "array", "items": {"type": "string"}},
                            "date_from": {"type": "string"},
                            "date_to": {"type": "string"},
                            "max_results": {"type": "integer", "default": 10}
                        },
                        "additionalProperties": False
                    }
                }
            }
        )
        
        try:
            parsed_data = json.loads(response.choices[0].message.content)
            # Remove None values
            parsed_data = {k: v for k, v in parsed_data.items() if v}
            return SearchQuery(**parsed_data)
        except (json.JSONDecodeError, ValidationError) as e:
            # Fallback to simple parsing
            return self.parse_simple(query)
    
    def parse_simple(self, query: str) -> SearchQuery:
        """Simple rule-based parser as fallback.
        
        Args:
            query: Natural language query
            
        Returns:
            Structured SearchQuery object
        """
        query_lower = query.lower()
        
        # Initialize result
        result = {
            "keywords": [],
            "categories": [],
            "max_results": 10
        }
        
        # Extract dates
        date_patterns = [
            (r"after (\w+ \d{4})", "date_from"),
            (r"since (\w+ \d{4})", "date_from"),
            (r"before (\w+ \d{4})", "date_to"),
            (r"until (\w+ \d{4})", "date_to"),
            (r"in (\d{4})", "year"),
            (r"published after (\w+ \d{4})", "date_from"),
            (r"published before (\w+ \d{4})", "date_to"),
        ]
        
        for pattern, date_type in date_patterns:
            match = re.search(pattern, query_lower)
            if match:
                date_str = match.group(1)
                try:
                    # Parse various date formats
                    if date_type == "year":
                        result["date_from"] = f"{date_str}-01-01"
                        result["date_to"] = f"{date_str}-12-31"
                    else:
                        # Try to parse month year format
                        date_obj = datetime.strptime(date_str.title(), "%B %Y")
                        if date_type == "date_from":
                            result["date_from"] = date_obj.strftime("%Y-%m-%d")
                        else:
                            result["date_to"] = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    pass
        
        # Extract categories
        for keyword, categories in self.CATEGORY_MAPPINGS.items():
            if keyword in query_lower:
                result["categories"].extend(categories)
        
        # Extract author if mentioned
        author_match = re.search(r"by (\w+ \w+)", query_lower)
        if author_match:
            result["author"] = author_match.group(1)
        
        # Extract limit
        limit_match = re.search(r"(\d+) (?:papers?|results?|articles?)", query_lower)
        if limit_match:
            result["max_results"] = min(int(limit_match.group(1)), 100)
        
        # Use remaining words as keywords
        # Remove common words and already extracted info
        stopwords = {"find", "search", "papers", "articles", "about", "on", "the", "a", 
                    "an", "in", "by", "after", "before", "since", "until", "published",
                    "recent", "latest", "new"}
        
        words = query_lower.split()
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        if keywords:
            result["keywords"] = keywords[:5]  # Limit to 5 keywords
        
        # Remove empty values
        result = {k: v for k, v in result.items() if v}
        
        return SearchQuery(**result)
    
    def parse(self, query: str) -> SearchQuery:
        """Parse a natural language query.
        
        Args:
            query: Natural language query
            
        Returns:
            Structured SearchQuery object
        """
        # Try LLM parsing first if available
        if self.client:
            try:
                return self.parse_with_llm(query)
            except Exception as e:
                print(f"LLM parsing failed: {e}, falling back to simple parser")
        
        # Fallback to simple parsing
        return self.parse_simple(query)