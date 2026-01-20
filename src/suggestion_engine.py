"""
Suggestion Engine Module
Handles text suggestions using template-based generation (lightweight alternative to LLM).
"""

from typing import List, Dict, Optional
import re
from loguru import logger

from src.config import config
from src.embedder import Embedder
from src.vector_store import VectorStore


class SuggestionEngine:
    """
    Generates text suggestions using template-based approach with retrieved context.
    Lightweight alternative to LLM - no GPT4All required!
    """
    
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        """
        Initialize the suggestion engine.
        
        Args:
            embedder: Embedder instance for query encoding
            vector_store: Vector store for context retrieval
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self._is_loaded = True  # Always ready with template-based approach
        
    def load_model(self) -> None:
        """Load the model (not needed for template-based approach)."""
        logger.info("Using template-based suggestion engine (no model loading required)")
        self._is_loaded = True
    
    def generate_suggestion(self, context: str, max_tokens: Optional[int] = None) -> str:
        """
        Generate a text suggestion based on context.
        
        Args:
            context: Input context text
            max_tokens: Maximum tokens to generate (not used in template mode)
            
        Returns:
            Generated suggestion text
        """
        try:
            # Retrieve relevant documents
            relevant_docs = self._retrieve_context(context)
            
            # Generate suggestion from templates
            suggestion = self._template_based_suggestion(context, relevant_docs)
            
            logger.debug(f"Generated suggestion: {suggestion[:100]}...")
            return suggestion
            
        except Exception as e:
            logger.error(f"Error generating suggestion: {e}")
            return ""
    
    def _retrieve_context(self, query: str) -> List[Dict]:
        """
        Retrieve relevant document chunks from vector store.
        
        Args:
            query: Query text
            
        Returns:
            List of relevant document chunks
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed_text(query)
            
            # Search vector store
            results = self.vector_store.search(
                query_embedding,
                k=config.rag_top_k,
                threshold=config.rag_similarity_threshold
            )
            
            logger.debug(f"Retrieved {len(results)} relevant chunks")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def _template_based_suggestion(self, context: str, relevant_docs: List[Dict]) -> str:
        """
        Generate suggestion using template-based approach with retrieved context.
        
        Args:
            context: User's current context
            relevant_docs: Retrieved relevant documents
            
        Returns:
            Suggested continuation
        """
        if not relevant_docs or len(relevant_docs) == 0:
            return ""
        
        # Get the most relevant document
        best_match = relevant_docs[0]
        match_text = best_match['text']
        
        # Extract last few words from context
        context_words = context.strip().split()
        if len(context_words) < 2:
            return self._extract_sentence_start(match_text)
        
        # Get last 3-5 words to find in the document
        search_phrase = ' '.join(context_words[-min(5, len(context_words)):])
        
        # Try to find similar phrase in the best match
        suggestion = self._find_continuation(search_phrase, match_text, context)
        
        if suggestion:
            return suggestion
        
        # Fallback: try with other matches
        for doc in relevant_docs[1:]:
            suggestion = self._find_continuation(search_phrase, doc['text'], context)
            if suggestion:
                return suggestion
        
        # Last resort: return a relevant sentence from best match
        return self._extract_relevant_sentence(match_text, context)
    
    def _find_continuation(self, search_phrase: str, text: str, context: str) -> str:
        """Find a natural continuation in the text."""
        # Case-insensitive search
        text_lower = text.lower()
        search_lower = search_phrase.lower()
        
        # Find phrase in text
        idx = text_lower.find(search_lower)
        
        if idx != -1:
            # Get what comes after
            continuation_start = idx + len(search_phrase)
            continuation = text[continuation_start:].strip()
            
            # Extract first sentence or clause
            sentences = re.split(r'[.!?]\s+', continuation)
            if sentences and len(sentences[0]) > 10:
                result = sentences[0]
                # Clean up
                if not result.endswith(('.', '!', '?')):
                    result += '.'
                return result
        
        # Try fuzzy matching - find similar words
        context_words = set(search_phrase.lower().split())
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            overlap = len(context_words & sentence_words)
            
            if overlap >= min(2, len(context_words)):
                # Found relevant sentence
                parts = sentence.split()
                if len(parts) > 5:
                    result = ' '.join(parts[:15])  # Take first 15 words
                    if not result.endswith(('.', '!', '?')):
                        result += '.'
                    return result
        
        return ""
    
    def _extract_sentence_start(self, text: str) -> str:
        """Extract the start of a relevant sentence."""
        sentences = re.split(r'[.!?]\s+', text)
        for sentence in sentences:
            if len(sentence.split()) >= 5:
                words = sentence.split()[:12]
                result = ' '.join(words)
                if not result.endswith(('.', '!', '?')):
                    result += '.'
                return result
        return ""
    
    def _extract_relevant_sentence(self, text: str, context: str) -> str:
        """Extract a sentence that seems relevant to the context."""
        context_words = set(context.lower().split())
        sentences = re.split(r'[.!?]\s+', text)
        
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            if len(sentence.split()) < 5:
                continue
            
            sentence_words = set(sentence.lower().split())
            overlap = len(context_words & sentence_words)
            
            if overlap > best_score:
                best_score = overlap
                best_sentence = sentence
        
        if best_sentence:
            words = best_sentence.split()[:12]
            result = ' '.join(words)
            if not result.endswith(('.', '!', '?')):
                result += '.'
            return result
        
        # Fallback
        return self._extract_sentence_start(text)
    
    def get_multiple_suggestions(self, context: str, count: int = 3) -> List[str]:
        """
        Generate multiple suggestion alternatives.
        
        Args:
            context: Input context
            count: Number of suggestions to generate
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        try:
            # Get relevant documents
            relevant_docs = self._retrieve_context(context)
            
            # Generate suggestions from different documents
            for i, doc in enumerate(relevant_docs[:count]):
                suggestion = self._find_continuation(
                    ' '.join(context.strip().split()[-5:]),
                    doc['text'],
                    context
                )
                
                if suggestion and suggestion not in suggestions:
                    suggestions.append(suggestion)
            
            # If we don't have enough, extract different sentences
            if len(suggestions) < count and relevant_docs:
                for doc in relevant_docs:
                    if len(suggestions) >= count:
                        break
                    
                    sentence = self._extract_relevant_sentence(doc['text'], context)
                    if sentence and sentence not in suggestions:
                        suggestions.append(sentence)
            
        except Exception as e:
            logger.error(f"Error generating multiple suggestions: {e}")
        
        return suggestions[:count]
