"""
Autocomplete Module
Provides real-time text suggestions based on context with AI generation.
"""

from typing import List, Optional
from loguru import logger

from retrieval.local_search import LocalSearch
from retrieval.online_search import OnlineSearch
from retrieval.ranker import Ranker
from suggestion.ai_generator import AITextGenerator
from config.settings import config


class Autocomplete:
    """
    Generates intelligent text suggestions based on user input.
    Combines document retrieval with AI text generation for smart completions.
    """
    
    def __init__(
        self,
        local_search: LocalSearch,
        online_search: Optional[OnlineSearch] = None,
        ranker: Optional[Ranker] = None,
        ai_generator: Optional[AITextGenerator] = None
    ):
        """
        Initialize autocomplete engine.
        
        Args:
            local_search: LocalSearch instance for querying local documents
            online_search: Optional OnlineSearch instance for fallback
            ranker: Optional Ranker for prioritizing results
            ai_generator: Optional AI text generator for intelligent completions
        """
        self.local_search = local_search
        self.online_search = online_search
        self.ranker = ranker or Ranker()
        self.ai_generator = ai_generator
        self.context_window = config.context_window_size
        
        # Try to initialize AI generator if not provided
        if self.ai_generator is None:
            try:
                from suggestion.ai_generator import get_generator
                self.ai_generator = get_generator()
            except Exception as e:
                logger.warning(f"AI generator not available: {e}")
        
        logger.info("Autocomplete engine initialized with AI generation")
    
    def get_suggestions(self, context: str, num_suggestions: int = 3) -> List[str]:
        """
        Generate text suggestions based on current context.
        Uses AI generation when available, falls back to template matching.
        
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
            
            # Search local documents for relevant context (RAG)
            local_results = self.local_search.search(query, top_k=5)
            
            suggestions = []
            
            # Try AI generation first if available
            if self.ai_generator and self.ai_generator.is_available():
                logger.info("Using AI generation for suggestions")
                
                try:
                    # Generate AI-powered suggestions with retrieved context
                    ai_suggestions = self.ai_generator.generate_multiple(
                        prompt=context,
                        context=local_results,
                        count=num_suggestions
                    )
                    
                    suggestions.extend(ai_suggestions)
                    logger.info(f"AI generated {len(ai_suggestions)} suggestions")
                    
                except Exception as e:
                    logger.warning(f"AI generation failed: {e}, falling back to templates")
            
            # Fall back to template-based suggestions if needed
            if len(suggestions) < num_suggestions and local_results:
                logger.info("Using template-based suggestions from local results")
                
                for result in local_results[:num_suggestions * 2]:
                    if len(suggestions) >= num_suggestions:
                        break
                    
                    suggestion = self._generate_suggestion_from_result(result, context)
                    if suggestion and suggestion not in suggestions:
                        suggestions.append(suggestion)
            
            # Online fallback if still insufficient
            if len(suggestions) < num_suggestions and self.online_search:
                logger.info("Using online fallback for additional suggestions")
                
                online_results = self.online_search.search(query)
                
                if online_results:
                    for result in online_results[:num_suggestions - len(suggestions)]:
                        suggestion = self._generate_suggestion_from_result(result, context)
                        if suggestion and suggestion not in suggestions:
                            suggestions.append(suggestion)
            
            logger.info(f"Generated total of {len(suggestions)} suggestions")
            return suggestions[:num_suggestions]
            
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
        for delimiter in ['. ', '! ', '? ', '\\n']:
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
            
            # Extract more content - show multiple sentences or full paragraph
            sentences = text.split('. ')
            
            if sentences:
                # Take first 2-3 sentences for richer context
                num_sentences = min(3, len(sentences))
                suggestion_parts = []
                
                for i in range(num_sentences):
                    sentence = sentences[i].strip()
                    if sentence:
                        suggestion_parts.append(sentence)
                
                suggestion = '. '.join(suggestion_parts)
                if not suggestion.endswith('.'):
                    suggestion += '.'
                
                # Allow longer suggestions for more content
                max_length = 400
                if len(suggestion) > max_length:
                    suggestion = suggestion[:max_length].rsplit('. ', 1)[0] + '.'
                
                # Don't suggest if it's too similar to existing context
                if suggestion.lower() not in context.lower():
                    # Add metadata for context
                    metadata = result.get('metadata', {})
                    source_file = metadata.get('file_name', '')
                    if source_file:
                        suggestion = f"[From: {source_file}]\\n{suggestion}"
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
