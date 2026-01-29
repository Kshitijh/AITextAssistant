"""
Online Search Module
Handles fallback to online sources when local data is insufficient.
"""

import pickle
from pathlib import Path
from typing import List, Dict, Optional
import time

import wikipedia
import requests
from bs4 import BeautifulSoup
from loguru import logger

from config.settings import config


class OnlineSearch:
    """
    Performs online searches as fallback when local data is insufficient.
    Caches results to minimize API calls and improve performance.
    """
    
    def __init__(self, cache_enabled: bool = True):
        """
        Initialize online search.
        
        Args:
            cache_enabled: Whether to cache search results
        """
        self.cache_enabled = cache_enabled
        self.cache_path = config.online_cache_path
        self.cache: Dict[str, List[Dict]] = {}
        self.max_results = config.online_max_results
        
        if self.cache_enabled:
            self._load_cache()
        
        logger.info("Online search initialized")
    
    def search(self, query: str) -> List[Dict]:
        """
        Search online sources for relevant content.
        
        Args:
            query: Search query
            
        Returns:
            List of result dictionaries from online sources
        """
        if not query or not query.strip():
            logger.warning("Empty query provided to online search")
            return []
        
        # Check cache first
        if self.cache_enabled and query in self.cache:
            logger.info(f"Returning cached online results for query: {query[:50]}...")
            return self.cache[query]
        
        results = []
        
        # Try Wikipedia first
        wiki_results = self._search_wikipedia(query)
        results.extend(wiki_results)
        
        # Could add more sources here (e.g., DuckDuckGo, specific docs sites)
        
        # Cache results
        if self.cache_enabled and results:
            self.cache[query] = results
            self._save_cache()
        
        logger.info(f"Online search returned {len(results)} results")
        return results
    
    def _search_wikipedia(self, query: str) -> List[Dict]:
        """
        Search Wikipedia for relevant articles.
        
        Args:
            query: Search query
            
        Returns:
            List of Wikipedia search results
        """
        try:
            logger.debug(f"Searching Wikipedia for: {query}")
            
            # Search for pages
            search_results = wikipedia.search(query, results=self.max_results)
            
            results = []
            for title in search_results[:self.max_results]:
                try:
                    # Get page summary
                    page = wikipedia.page(title, auto_suggest=False)
                    summary = page.summary
                    
                    result = {
                        'text': summary,
                        'source': 'wikipedia',
                        'similarity_score': 0.0,  # Not computed for online results
                        'metadata': {
                            'title': title,
                            'url': page.url,
                            'timestamp': time.time()
                        }
                    }
                    results.append(result)
                    
                    logger.debug(f"Retrieved Wikipedia article: {title}")
                    
                except wikipedia.exceptions.DisambiguationError as e:
                    # Try first option from disambiguation
                    if e.options:
                        try:
                            page = wikipedia.page(e.options[0], auto_suggest=False)
                            summary = page.summary
                            
                            result = {
                                'text': summary,
                                'source': 'wikipedia',
                                'similarity_score': 0.0,
                                'metadata': {
                                    'title': e.options[0],
                                    'url': page.url,
                                    'timestamp': time.time()
                                }
                            }
                            results.append(result)
                            
                        except Exception:
                            continue
                            
                except wikipedia.exceptions.PageError:
                    logger.debug(f"Wikipedia page not found: {title}")
                    continue
                    
                except Exception as e:
                    logger.warning(f"Error fetching Wikipedia page '{title}': {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error in Wikipedia search: {e}")
            return []
    
    def _load_cache(self) -> None:
        """Load cached search results from disk."""
        try:
            if self.cache_path.exists():
                with open(self.cache_path, 'rb') as f:
                    self.cache = pickle.load(f)
                logger.info(f"Loaded online search cache with {len(self.cache)} entries")
        except Exception as e:
            logger.warning(f"Error loading online search cache: {e}")
            self.cache = {}
    
    def _save_cache(self) -> None:
        """Save cached search results to disk."""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, 'wb') as f:
                pickle.dump(self.cache, f)
            logger.debug("Online search cache saved")
        except Exception as e:
            logger.error(f"Error saving online search cache: {e}")
    
    def clear_cache(self) -> None:
        """Clear the online search cache."""
        self.cache = {}
        if self.cache_path.exists():
            self.cache_path.unlink()
        logger.info("Online search cache cleared")
