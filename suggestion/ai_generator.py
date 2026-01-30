"""
AI Text Generator Module
Provides AI-powered text generation using llama.cpp for natural language completions.
"""

from typing import List, Optional, Dict
from pathlib import Path
from loguru import logger

from config.settings import config

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    logger.warning("llama-cpp-python not installed - AI generation disabled")


class AITextGenerator:
    """
    AI-powered text generation engine using llama.cpp.
    Generates natural, contextual text completions.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize AI text generator.
        
        Args:
            model_path: Path to GGUF model file
        """
        self.model_path = Path(model_path or config.llm_model_path)
        self.llm: Optional[Llama] = None
        self._is_loaded = False
        
        # Generation parameters
        self.temperature = config.llm_temperature
        self.max_tokens = config.llm_max_tokens
        self.top_p = config.llm_top_p
        self.top_k = config.llm_top_k
        
        logger.info("AI Text Generator initialized")
    
    def load_model(self) -> bool:
        """
        Load the LLM model.
        
        Returns:
            True if successful, False otherwise
        """
        if not LLAMA_AVAILABLE:
            logger.error("llama-cpp-python not available")
            logger.info("Install with: pip install llama-cpp-python")
            return False
        
        if not self.model_path.exists():
            logger.warning(f"Model not found at: {self.model_path}")
            logger.info("\nTo download a model:")
            logger.info("1. Visit: https://huggingface.co/TheBloke")
            logger.info("2. Search for GGUF models (e.g., 'Phi-3-mini GGUF')")
            logger.info("3. Download Q4_K_M version (~2-4GB)")
            logger.info(f"4. Place in: {self.model_path.parent}")
            logger.info("\nRecommended models:")
            logger.info("  - Phi-3-mini-4k-instruct-Q4_K_M.gguf (~2GB)")
            logger.info("  - TinyLlama-1.1B-Chat-v1.0-Q4_K_M.gguf (~700MB)")
            logger.info("  - Mistral-7B-Instruct-v0.2-Q4_K_M.gguf (~4GB)")
            return False
        
        try:
            logger.info(f"Loading model from: {self.model_path}")
            
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=2048,  # Context window size
                n_threads=4,  # CPU threads
                n_gpu_layers=0,  # CPU-only mode
                verbose=False
            )
            
            self._is_loaded = True
            logger.info("✅ Model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        context: Optional[List[Dict]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate text completion using AI.
        
        Args:
            prompt: Input prompt/context
            context: Optional retrieved documents for RAG
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            Generated text
        """
        if not self._is_loaded:
            if not self.load_model():
                return ""
        
        try:
            # Build prompt with retrieved context (RAG)
            full_prompt = self._build_rag_prompt(prompt, context)
            
            # Generate completion
            response = self.llm(
                full_prompt,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                stop=["</s>", "\n\n\n"],  # Stop tokens
                echo=False
            )
            
            # Extract generated text
            generated_text = response['choices'][0]['text'].strip()
            
            logger.debug(f"Generated: {generated_text[:100]}...")
            return generated_text
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return ""
    
    def _build_rag_prompt(self, user_prompt: str, context: Optional[List[Dict]] = None) -> str:
        """
        Build RAG (Retrieval Augmented Generation) prompt.
        
        Args:
            user_prompt: User's input text
            context: Retrieved document chunks
            
        Returns:
            Formatted prompt with context
        """
        if not context or len(context) == 0:
            # No context - direct completion
            return f"""Complete the following text naturally:

{user_prompt}

Continuation:"""
        
        # Build context from retrieved documents
        context_text = "\n\n".join([
            f"Reference {i+1}: {doc.get('text', '')[:300]}"
            for i, doc in enumerate(context[:3])  # Top 3 results
        ])
        
        # Create RAG prompt
        prompt = f"""Based on the following reference materials, continue the text naturally and informatively.

Reference Materials:
{context_text}

Text to continue:
{user_prompt}

Natural continuation:"""
        
        return prompt
    
    def generate_multiple(
        self,
        prompt: str,
        context: Optional[List[Dict]] = None,
        count: int = 3
    ) -> List[str]:
        """
        Generate multiple diverse completions.
        
        Args:
            prompt: Input prompt
            context: Optional retrieved documents
            count: Number of completions to generate
            
        Returns:
            List of generated texts
        """
        suggestions = []
        temperatures = [0.5, 0.7, 0.9]  # Varying creativity
        
        for i in range(count):
            temp = temperatures[i % len(temperatures)]
            
            suggestion = self.generate(
                prompt,
                context=context,
                temperature=temp
            )
            
            if suggestion and suggestion not in suggestions:
                suggestions.append(suggestion)
        
        return suggestions
    
    def is_available(self) -> bool:
        """Check if AI generation is available."""
        return LLAMA_AVAILABLE and (self._is_loaded or self.model_path.exists())


# Global instance
_generator: Optional[AITextGenerator] = None


def get_generator() -> AITextGenerator:
    """Get global AI text generator instance."""
    global _generator
    if _generator is None:
        _generator = AITextGenerator()
    return _generator
