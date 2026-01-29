"""
Ranker Module
Ranks and prioritizes search results from multiple sources.
"""

from typing import List, Dict
from loguru import logger

from config.settings import config


class Ranker:
    """
    Ranks and merges results from local and online sources.
    Ensures local results are always prioritized over online results.
    """
    
    def __init__(self):
        """Initialize the ranker."""
        self.similarity_threshold = config.similarity_threshold
        logger.info("Ranker initialized")
    
    def rank_results(self, local_results: List[Dict], online_results: List[Dict]) -> List[Dict]:
        """
        Rank and merge local and online results.
        Local results ALWAYS take priority.
        
        Args:
            local_results: Results from local search
            online_results: Results from online search
            
        Returns:
            Merged and ranked list of results
        """
        ranked = []
        
        # Add all local results first (they're already filtered and scored)
        if local_results:
            ranked.extend(local_results)
            logger.info(f"Added {len(local_results)} local results to ranking")
        
        # Only add online results if local results are insufficient
        if online_results:
            # Mark online results as secondary
            for result in online_results:
                result['is_fallback'] = True
            
            ranked.extend(online_results)
            logger.info(f"Added {len(online_results)} online results as fallback")
        
        return ranked
    
    def get_best_context(self, results: List[Dict], max_length: int = None) -> str:
        """
        Extract the best context from ranked results.
        
        Args:
            results: Ranked list of results
            max_length: Maximum context length (uses config default if None)
            
        Returns:
            Concatenated context string
        """
        max_length = max_length or config.max_context_length
        
        context_parts = []
        current_length = 0
        local_count = 0
        online_count = 0
        
        for result in results:
            text = result.get('text', '')
            source = result.get('source', 'unknown')
            
            if current_length + len(text) <= max_length:
                context_parts.append(text)
                current_length += len(text)
                
                if source == 'local':
                    local_count += 1
                else:
                    online_count += 1
            else:
                # Add partial text if meaningful space remains
                remaining = max_length - current_length
                if remaining > 100:
                    context_parts.append(text[:remaining])
                    if source == 'local':
                        local_count += 1
                    else:
                        online_count += 1
                break
        
        context = "\n\n---\n\n".join(context_parts)
        
        logger.debug(
            f"Generated context: {len(context)} chars "
            f"({local_count} local, {online_count} online)"
        )
        
        return context
    
    def log_ranking_info(self, results: List[Dict]) -> None:
        """
        Log detailed ranking information for debugging.
        
        Args:
            results: Ranked results
        """
        logger.info("=== Ranking Summary ===")
        
        for i, result in enumerate(results, 1):
            source = result.get('source', 'unknown')
            score = result.get('similarity_score', 0.0)
            metadata = result.get('metadata', {})
            
            if source == 'local':
                file_name = metadata.get('file_name', 'unknown')
                chunk_idx = metadata.get('chunk_index', 0)
                logger.info(
                    f"{i}. [LOCAL] {file_name} (chunk {chunk_idx}) - "
                    f"Score: {score:.3f}"
                )
            else:
                title = metadata.get('title', 'unknown')
                logger.info(
                    f"{i}. [ONLINE-{source.upper()}] {title} - "
                    f"Fallback source"
                )
