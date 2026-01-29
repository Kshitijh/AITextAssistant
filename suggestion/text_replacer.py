"""
Text Replacer Module
Handles text refinement and replacement operations.
"""

from typing import Optional, List
from loguru import logger

from retrieval.local_search import LocalSearch
from retrieval.online_search import OnlineSearch
from retrieval.ranker import Ranker
from config.settings import config


class TextReplacer:
    """
    Generates improved or alternative versions of selected text.
    Prioritizes local document style and content.
    """
    
    def __init__(
        self,
        local_search: LocalSearch,
        online_search: Optional[OnlineSearch] = None,
        ranker: Optional[Ranker] = None
    ):
        """
        Initialize text replacer.
        
        Args:
            local_search: LocalSearch instance
            online_search: Optional OnlineSearch instance
            ranker: Optional Ranker instance
        """
        self.local_search = local_search
        self.online_search = online_search
        self.ranker = ranker or Ranker()
        
        logger.info("Text replacer initialized")
    
    def refine_text(self, selected_text: str, context: str = "") -> Optional[str]:
        """
        Refine selected text to improve quality.
        
        Args:
            selected_text: The text to refine
            context: Surrounding context for better refinement
            
        Returns:
            Refined version of the text or None
        """
        if not selected_text or not selected_text.strip():
            logger.warning("Empty text provided for refinement")
            return None
        
        try:
            logger.info(f"Refining text: {selected_text[:50]}...")
            
            # Search for similar content in local documents
            query = selected_text if len(selected_text) < 200 else selected_text[:200]
            local_results = self.local_search.search(query, top_k=3)
            
            if local_results:
                # Use most similar result as refinement base
                best_result = local_results[0]
                refined = self._create_refinement(selected_text, best_result, context)
                
                if refined:
                    logger.info("Text refined using local documents")
                    return refined
            
            # Fallback to online if needed
            if self.online_search and not local_results:
                logger.info("No local results, attempting online refinement")
                online_results = self.online_search.search(query)
                
                if online_results:
                    refined = self._create_refinement(selected_text, online_results[0], context)
                    if refined:
                        logger.info("Text refined using online sources")
                        return refined
            
            # If no good refinement found, return slightly cleaned version
            return self._basic_cleanup(selected_text)
            
        except Exception as e:
            logger.error(f"Error refining text: {e}")
            return None
    
    def expand_text(self, selected_text: str, context: str = "") -> Optional[str]:
        """
        Expand selected text with additional relevant content.
        
        Args:
            selected_text: The text to expand
            context: Surrounding context
            
        Returns:
            Expanded version of the text or None
        """
        if not selected_text or not selected_text.strip():
            logger.warning("Empty text provided for expansion")
            return None
        
        try:
            logger.info(f"Expanding text: {selected_text[:50]}...")
            
            # Search for related content
            local_results = self.local_search.search(selected_text, top_k=5)
            
            if local_results:
                # Combine selected text with relevant context
                expansion = self._create_expansion(selected_text, local_results)
                
                if expansion:
                    logger.info("Text expanded using local documents")
                    return expansion
            
            # Fallback to online
            if self.online_search and len(local_results) < 2:
                online_results = self.online_search.search(selected_text)
                
                if online_results:
                    expansion = self._create_expansion(selected_text, online_results)
                    if expansion:
                        logger.info("Text expanded using online sources")
                        return expansion
            
            return selected_text  # Return original if no expansion possible
            
        except Exception as e:
            logger.error(f"Error expanding text: {e}")
            return None
    
    def get_alternatives(self, selected_text: str, num_alternatives: int = 3) -> List[str]:
        """
        Get alternative phrasings from similar content.
        
        Args:
            selected_text: The text to find alternatives for
            num_alternatives: Number of alternatives to generate
            
        Returns:
            List of alternative text versions
        """
        try:
            logger.info(f"Finding alternatives for: {selected_text[:50]}...")
            
            # Search for similar content
            local_results = self.local_search.search(selected_text, top_k=num_alternatives * 2)
            
            alternatives = []
            
            for result in local_results[:num_alternatives]:
                text = result.get('text', '')
                if text and text != selected_text:
                    # Extract relevant portion
                    alt = self._extract_alternative(text, selected_text)
                    if alt and alt not in alternatives:
                        alternatives.append(alt)
            
            logger.info(f"Found {len(alternatives)} alternatives")
            return alternatives
            
        except Exception as e:
            logger.error(f"Error finding alternatives: {e}")
            return []
    
    def _create_refinement(self, original: str, result: dict, context: str) -> Optional[str]:
        """
        Create refined version based on search result.
        
        Args:
            original: Original text
            result: Search result to base refinement on
            context: Surrounding context
            
        Returns:
            Refined text or None
        """
        # Simple refinement: use the most similar sentence from result
        result_text = result.get('text', '')
        
        if not result_text:
            return None
        
        # Extract most relevant sentence
        sentences = [s.strip() for s in result_text.split('. ') if s.strip()]
        
        if sentences:
            # Return first sentence as refinement (could be more sophisticated)
            refined = sentences[0]
            if not refined.endswith('.'):
                refined += '.'
            return refined
        
        return None
    
    def _create_expansion(self, original: str, results: List[dict]) -> Optional[str]:
        """
        Create expanded version using search results.
        
        Args:
            original: Original text
            results: List of search results
            
        Returns:
            Expanded text or None
        """
        # Combine original with relevant snippets from results
        expansion_parts = [original]
        
        for result in results[:2]:  # Use top 2 results
            text = result.get('text', '')
            if text:
                # Extract first sentence
                sentences = [s.strip() for s in text.split('. ') if s.strip()]
                if sentences and sentences[0] not in expansion_parts:
                    expansion_parts.append(sentences[0])
        
        if len(expansion_parts) > 1:
            expanded = '. '.join(expansion_parts)
            if not expanded.endswith('.'):
                expanded += '.'
            return expanded
        
        return None
    
    def _extract_alternative(self, text: str, original: str) -> Optional[str]:
        """Extract alternative phrasing from text."""
        # Simple approach: return first sentence if different from original
        sentences = [s.strip() for s in text.split('. ') if s.strip()]
        
        for sentence in sentences:
            if sentence.lower() != original.lower() and len(sentence) > 10:
                if not sentence.endswith('.'):
                    sentence += '.'
                return sentence
        
        return None
    
    def _basic_cleanup(self, text: str) -> str:
        """
        Perform basic text cleanup.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        cleaned = ' '.join(text.split())
        
        # Ensure proper ending punctuation
        if cleaned and cleaned[-1] not in '.!?':
            cleaned += '.'
        
        return cleaned
