import asyncio
import logging

logger = logging.getLogger(__name__)

class LLMConcurrencyManager:
    """
    Manages global LLM concurrency to prevent API credit burn
    and enforce system-specific parallelization limits.
    """
    def __init__(self):
        self._semaphore = asyncio.Semaphore(1)  # Default to 1
        self._current_limit = 1

    def set_limit(self, limit: int):
        """Dynamic resizing of the semaphore is tricky in asyncio, 
        so we create a new one. This should be called between phases."""
        if limit == self._current_limit:
            return
            
        logger.info(f"[Concurrency] Updating LLM limit from {self._current_limit} to {limit}")
        self._semaphore = asyncio.Semaphore(limit)
        self._current_limit = limit

    async def acquire(self):
        """Acquire a concurrency slot"""
        return await self._semaphore.acquire()

    def release(self):
        """Release a concurrency slot"""
        self._semaphore.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()

llm_concurrency_manager = LLMConcurrencyManager()
