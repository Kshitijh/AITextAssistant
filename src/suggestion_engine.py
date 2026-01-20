"""
Suggestion Engine Module
Handles text generation using RAG (Retrieval Augmented Generation) with local LLM.
"""

from typing import List, Dict, Optional
from loguru import logger

from src.config import config
from src.embedder import Embedder
from src.vector_store import VectorStore

try:
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False
    logger.warning("GPT4All not available")


class SuggestionEngine:
    """
    Generates text suggestions using RAG with a local LLM.
    Retrieves relevant context from documents and generates continuations.
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
        self.llm: Optional[GPT4All] = None
        self._is_loaded = False
        
    def load_model(self) -> None:
        """Load the LLM model."""
        if not GPT4ALL_AVAILABLE:
            logger.error("GPT4All is not available. Please install gpt4all.")
            return
        
        try:
            logger.info(f"Loading LLM model: {config.llm_model_name}")
            
            # Initialize GPT4All
            self.llm = GPT4All(
                model_name=config.llm_model_name,
                model_path=config.llm_model_path,
                allow_download=True,
                device=config.embedding_device
            )
            
            self._is_loaded = True
            logger.info("LLM model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading LLM model: {e}")
            logger.info("Suggestion engine will run in fallback mode")
            self._is_loaded = False
    
    def generate_suggestion(self, context: str, max_tokens: Optional[int] = None) -> str:
        """
        Generate a text suggestion based on context.
        
        Args:
            context: Input context text
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated suggestion text
        """
        if not self._is_loaded:
            logger.warning("LLM not loaded, attempting to load...")
            self.load_model()
            
            if not self._is_loaded:
                return self._fallback_suggestion(context)
        
        try:
            # Retrieve relevant documents
            relevant_docs = self._retrieve_context(context)
            
            # Build prompt with retrieved context
            prompt = self._build_prompt(context, relevant_docs)
            
            # Generate completion
            max_tokens = max_tokens or config.llm_max_tokens
            
            response = self.llm.generate(
                prompt,
                max_tokens=max_tokens,
                temp=config.llm_temperature,
                top_k=config.llm_top_k,
                top_p=config.llm_top_p,
            )
            
            # Extract and clean the suggestion
            suggestion = self._clean_suggestion(response, context)
            
            logger.debug(f"Generated suggestion: {suggestion[:100]}...")
            return suggestion
            
        except Exception as e:
            logger.error(f"Error generating suggestion: {e}")
            return self._fallback_suggestion(context)
    
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
    
    def _build_prompt(self, context: str, relevant_docs: List[Dict]) -> str:
        """
        Build a prompt for the LLM with retrieved context.
        
        Args:
            context: User's current context
            relevant_docs: Retrieved relevant documents
            
        Returns:
            Formatted prompt
        """
        # Construct context from retrieved documents
        retrieved_context = ""
        if relevant_docs:
            retrieved_context = "\n\n".join([
                f"Reference {i+1}: {doc['text'][:300]}"
                for i, doc in enumerate(relevant_docs)
            ])
            
            # Limit total context length
            max_context = config.rag_max_context_length
            if len(retrieved_context) > max_context:
                retrieved_context = retrieved_context[:max_context] + "..."
        
        # Build prompt
        if retrieved_context:
            prompt = f"""Based on the following reference materials, continue the text naturally.

Reference Materials:
{retrieved_context}

Text to continue:
{context}

Continue the text naturally (write only the continuation, not the original text):"""
        else:
            prompt = f"""Continue the following text naturally:

{context}

Continuation:"""
        
        return prompt
    
    def _clean_suggestion(self, response: str, original_context: str) -> str:
        """
        Clean and format the generated suggestion.
        
        Args:
            response: Raw LLM response
            original_context: Original context text
            
        Returns:
            Cleaned suggestion
        """
        # Remove common artifacts
        suggestion = response.strip()
        
        # Remove quotes if present
        if suggestion.startswith('"') and suggestion.endswith('"'):
            suggestion = suggestion[1:-1]
        
        # Remove the original context if LLM repeated it
        if suggestion.startswith(original_context):
            suggestion = suggestion[len(original_context):].strip()
        
        # Take only the first sentence or two
        sentences = suggestion.split('. ')
        if len(sentences) > 2:
            suggestion = '. '.join(sentences[:2]) + '.'
        
        # Limit length
        max_length = config.llm_max_tokens * 4  # Rough estimate
        if len(suggestion) > max_length:
            suggestion = suggestion[:max_length].rsplit(' ', 1)[0] + '...'
        
        return suggestion
    
    def _fallback_suggestion(self, context: str) -> str:
        """
        Provide a fallback suggestion when LLM is unavailable.
        
        Args:
            context: Input context
            
        Returns:
            Fallback suggestion
        """
        # Try to retrieve similar content from documents
        try:
            relevant_docs = self._retrieve_context(context)
            
            if relevant_docs and len(relevant_docs) > 0:
                # Extract a relevant snippet
                best_match = relevant_docs[0]['text']
                
                # Find context in the snippet
                context_words = context.strip().split()[-5:]  # Last 5 words
                context_end = ' '.join(context_words)
                
                # Try to find where context appears in the match
                idx = best_match.lower().find(context_end.lower())
                
                if idx != -1:
                    # Return what comes after
                    continuation = best_match[idx + len(context_end):].strip()
                    sentences = continuation.split('. ')
                    if sentences:
                        return sentences[0] + '.'
                
                # Otherwise return first sentence of best match
                sentences = best_match.split('. ')
                if sentences:
                    return sentences[0] + '.'
            
        except Exception as e:
            logger.error(f"Error in fallback suggestion: {e}")
        
        return ""
    
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
        
        # Generate with different temperature settings
        temperatures = [0.5, 0.7, 0.9]
        
        for i in range(min(count, len(temperatures))):
            try:
                # Temporarily modify temperature
                original_temp = config.llm_temperature
                
                if self.llm and self._is_loaded:
                    suggestion = self.generate_suggestion(context)
                    if suggestion and suggestion not in suggestions:
                        suggestions.append(suggestion)
                
            except Exception as e:
                logger.error(f"Error generating suggestion {i+1}: {e}")
        
        # Fill remaining with fallback if needed
        while len(suggestions) < count:
            fallback = self._fallback_suggestion(context)
            if fallback and fallback not in suggestions:
                suggestions.append(fallback)
            else:
                break
        
        return suggestions[:count]
