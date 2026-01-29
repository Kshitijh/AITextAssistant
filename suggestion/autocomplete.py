"""
Autocomplete Module
Provides real-time text suggestions based on context.
"""

from typing import List, Optional
from loguru import logger

from retrieval.local_search import LocalSearch
from retrieval.online_search import OnlineSearch
from retrieval.ranker import Ranker
from config.settings import config


class Autocomplete:
    """
    Generates intelligent text suggestions based on user input.
    Prioritizes local documents, falls back to online search when needed.
    """
    
    def __init__(
        self,
        local_search: LocalSearch,
        online_search: Optional[OnlineSearch] = None,
        ranker: Optional[Ranker] = None
    ):
        """
        Initialize autocomplete engine.
        
        Args:
            local_search: LocalSearch instance for querying local documents
            online_search: Optional OnlineSearch instance for fallback
            ranker: Optional Ranker for prioritizing results
        """
        self.local_search = local_search
        self.online_search = online_search
        self.ranker = ranker or Ranker()
        self.context_window = config.context_window_size
        
        logger.info("Autocomplete engine initialized")
    
    def get_suggestions(self, context: str, num_suggestions: int = 3) -> List[str]:
        """
        Generate text suggestions based on current context.
        
        Args:
            context: Current text context (last N characters typed)
            num_suggestions: Number of suggestions to generate
            
        Returns:
            List of suggested text completions
        """
        if not context or not context.strip():
            logger.debug("Empty context provided")
            return []
        
        try:
            # Extract query from context (last sentence or meaningful chunk)
            query = self._extract_query(context)
            logger.debug(f"Extracted query: {query[:100]}...")
            
            # Search local documents first
            local_results = self.local_search.search(query, top_k=num_suggestions * 2)
            
            suggestions = []
            
            if local_results:
                # Generate suggestions from local results
                logger.info(f"Generating suggestions from {len(local_results)} local results")
                
                for result in local_results[:num_suggestions]:
                    suggestion = self._generate_suggestion_from_result(result, context)
                    if suggestion:
                        suggestions.append(suggestion)
            
            # Fallback to online if insufficient local results
            if len(suggestions) < num_suggestions and self.online_search:
                logger.info("Insufficient local results, using online fallback")
                
                online_results = self.online_search.search(query)
                
                if online_results:
                    for result in online_results[:num_suggestions - len(suggestions)]:
                        suggestion = self._generate_suggestion_from_result(result, context)
                        if suggestion:
                            suggestions.append(suggestion)
            
            logger.info(f"Generated {len(suggestions)} suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
    
    def _extract_query(self, context: str) -> str:
        """
        Extract meaningful query from context.
        
        Args:
            context: Full context text
            
        Returns:
            Extracted query string
        """
        # Take last N characters as query context
        query = context[-self.context_window:].strip()
        
        # Try to find last complete sentence
        for delimiter in ['. ', '! ', '? ', '\n']:
            if delimiter in query:
                parts = query.split(delimiter)
                if parts[-1].strip():
                    query = parts[-1].strip()
                    break
        
        return query
    
    def _generate_suggestion_from_result(self, result: dict, context: str) -> Optional[str]:
        """
        Generate a suggestion from a search result.
        
        Args:
            result: Search result dictionary
            context: Current context
            
        Returns:
            Suggested text or None
        """
        try:
            text = result.get('text', '')
            if not text:
                return None
            
            # Extract relevant portion from result
            # Simple approach: take first sentence or first N characters
            sentences = text.split('. ')
            
            if sentences:
                # Take first complete sentence
                suggestion = sentences[0].strip()
                
                # Ensure it's not too long
                max_length = 150
                if len(suggestion) > max_length:
                    suggestion = suggestion[:max_length].rsplit(' ', 1)[0] + '...'
                
                # Don't suggest if it's too similar to existing context
                if suggestion.lower() not in context.lower():
                    return suggestion
            
            return None
            
        except Exception as e:
            logger.warning(f"Error generating suggestion from result: {e}")
            return None
    
    def get_completion(self, context: str) -> Optional[str]:
        """
        Get single best completion for current context.
        
        Args:
            context: Current text context
            
        Returns:
            Best completion suggestion or None
        """
        suggestions = self.get_suggestions(context, num_suggestions=1)
        return suggestions[0] if suggestions else None
