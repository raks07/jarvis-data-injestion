from typing import List, Optional, Dict, Any
import asyncio
import logging
import os
from functools import lru_cache

# For local model support
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# For OpenAI support
import openai
from openai import AsyncOpenAI

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for interacting with language models.
    """

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipe = None
        self.client = None
        self.use_openai = settings.OPENAI_API_KEY is not None
        self.chat_model = "gpt-3.5-turbo"  # Default chat model
        self.embedding_model = settings.OPENAI_MODEL  # For embeddings

        # Initialize OpenAI client if API key is available
        if self.use_openai:
            openai.api_key = settings.OPENAI_API_KEY
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("Using OpenAI for LLM service")
        else:
            logger.info("Using local model for LLM service")

    async def generate_answer(self, question: str, context: str) -> str:
        """
        Generate an answer for a question based on the context.
        """
        if not context:
            return "I don't have enough information to answer that question."

        # Prepare prompt
        prompt = self._create_prompt(question, context)

        # Use OpenAI if configured
        if self.use_openai:
            return await self._generate_with_openai(prompt)

        # Otherwise use local model
        return await self._generate_with_local_model(prompt)

    async def split_text(
        self, text: str, chunk_size: int = 500, chunk_overlap: int = 50
    ) -> List[str]:
        """
        Split text into chunks for processing.
        """
        # Simple text splitting by sentences
        # In a real implementation, this would use a more sophisticated approach
        sentences = text.split(". ")
        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence = sentence.strip() + ". "
            sentence_size = len(sentence)

            if current_size + sentence_size > chunk_size and current_chunk:
                chunks.append("".join(current_chunk))

                # Keep some sentences for overlap
                overlap_sentences = (
                    current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                )
                current_chunk = overlap_sentences
                current_size = sum(len(s) for s in current_chunk)

            current_chunk.append(sentence)
            current_size += sentence_size

        if current_chunk:
            chunks.append("".join(current_chunk))

        return chunks

    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate response using OpenAI API."""
        try:
            # Use a chat model, not an embeddings model
            response = await self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on the provided context.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {str(e)}")
            return (
                f"Sorry, I encountered an error while generating your answer: {str(e)}"
            )

    async def _generate_with_local_model(self, prompt: str) -> str:
        """Generate response using local Hugging Face model."""
        try:
            # Lazy load the model
            if self.pipe is None:
                await self._load_local_model()

            # Run text generation in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.pipe(
                    prompt,
                    max_length=512,
                    temperature=0.7,
                    top_p=0.9,
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.eos_token_id,
                ),
            )

            generated_text = result[0]["generated_text"]

            # Extract the answer part (remove the prompt)
            answer = generated_text[len(prompt) :].strip()

            return (
                answer
                if answer
                else "I couldn't generate a proper response based on the information provided."
            )
        except Exception as e:
            logger.error(f"Error generating response with local model: {str(e)}")
            return (
                f"Sorry, I encountered an error while generating your answer: {str(e)}"
            )

    async def _load_local_model(self):
        """Load the local Hugging Face model."""
        try:
            logger.info(f"Loading local model for text generation")

            # For text generation, we need a different model than the embedding one
            # Use a smaller model suitable for generation on CPU/small GPU
            model_name = "facebook/opt-125m"  # A smaller model suitable for generation

            # Use device specified in settings or CUDA if available
            device = settings.DEVICE
            if device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map=device,
            )

            # Create a text generation pipeline
            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=device,
            )

            logger.info(f"Model loaded successfully on {device}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def _create_prompt(self, question: str, context: str) -> str:
        """Create a prompt for the language model."""
        return f"""Answer the question based on the context below.

Context:
{context}

Question: {question}

Answer:"""
