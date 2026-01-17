"""
Reducer Pipeline Orchestrator
Main entry point for post-reducer processing.
Implements the 5-step workflow with proper blocking/non-blocking separation.
"""
import asyncio
import json
import logging
import time
from typing import Optional, Set
from datetime import datetime

from app.db.redis_client import redis_client
from app.db.mongo_client import mongo_client
from app.models.reducer import ReducerOutput, ReducerContext, ReducerPayload
from app.models.constraints import Constraints
from app.pipeline.redis_keys import RedisKeys, TTL
from app.pipeline.constraint_builder import constraint_builder
from app.pipeline.component_selector import component_selector
from app.pipeline.layout_assembler import layout_assembler, LayoutSchema

logger = logging.getLogger(__name__)


class ReducerPipeline:
    """
    Orchestrates the post-reducer processing pipeline.
    
    Flow:
    1. Redis Write (BLOCKING) - Store reducer state
    2. Fan-Out (PARALLEL) - Constraints, Vector Search, MongoDB
    3. Component Selection - Deterministic selection
    4. Layout Assembly - Build schema
    5. Output - Return layout schema
    """
    
    async def process(
        self,
        payload: ReducerPayload,
        skip_persistence: bool = False
    ) -> LayoutSchema:
        """
        Process reducer output and return layout schema.
        
        Args:
            payload: Complete reducer payload with context
            skip_persistence: Skip MongoDB writes (for testing)
            
        Returns:
            LayoutSchema for frontend rendering
        """
        start_time = time.perf_counter()
        session_id = payload.context.session_id
        
        logger.info(f"[Pipeline] Starting for session: {session_id}")
        
        # ========================================
        # STEP 1: Redis Write (BLOCKING)
        # ========================================
        await self._write_session_state(session_id, payload.output)
        step1_time = time.perf_counter()
        logger.debug(f"[Step 1] Redis write: {(step1_time - start_time)*1000:.2f}ms")
        
        # ========================================
        # STEP 2: Parallel Fan-Out (NON-BLOCKING)
        # ========================================
        # Build constraints synchronously (fast, no I/O)
        constraints = constraint_builder.build(payload.output, payload.context)
        
        # Store constraints in Redis
        await redis_client.set(
            RedisKeys.constraints(session_id),
            constraints.model_dump_json(),
            ttl=TTL.SESSION
        )
        
        # Fire and forget: MongoDB persistence (don't await)
        if not skip_persistence:
            asyncio.create_task(
                self._persist_to_mongodb(session_id, payload, constraints)
            )
        
        # Fire and forget: Vector search (don't await)
        asyncio.create_task(
            self._vector_search_and_cache(session_id, payload.output, constraints)
        )
        
        step2_time = time.perf_counter()
        logger.debug(f"[Step 2] Fan-out setup: {(step2_time - step1_time)*1000:.2f}ms")
        
        # ========================================
        # STEP 3: Component Selection
        # ========================================
        recently_used = await self._get_recently_used(session_id)
        
        selection = component_selector.select(
            constraints=constraints,
            recently_used=recently_used,
            required_types=["hero", "product-grid", "cta"]
        )
        
        # Update recently used set
        await self._update_recently_used(session_id, selection)
        
        # Store selection in Redis
        selected_ids = [c.component_id for c in selection.selected_components]
        await redis_client.set(
            RedisKeys.selected(session_id),
            json.dumps(selected_ids),
            ttl=TTL.CANDIDATES
        )
        
        step3_time = time.perf_counter()
        logger.debug(f"[Step 3] Selection: {(step3_time - step2_time)*1000:.2f}ms")
        
        # ========================================
        # STEP 4: Layout Assembly
        # ========================================
        previous_hash = await redis_client.get(RedisKeys.layout_hash(session_id))
        
        layout = layout_assembler.assemble(
            session_id=session_id,
            selection=selection,
            reducer_output=payload.output,
            previous_hash=previous_hash
        )
        
        # Cache layout in Redis
        await redis_client.set(
            RedisKeys.layout(session_id),
            layout.model_dump_json(),
            ttl=TTL.LAYOUT
        )
        await redis_client.set(
            RedisKeys.layout_hash(session_id),
            layout.layout_hash,
            ttl=TTL.LAYOUT
        )
        
        step4_time = time.perf_counter()
        logger.debug(f"[Step 4] Assembly: {(step4_time - step3_time)*1000:.2f}ms")
        
        # ========================================
        # STEP 5: Output
        # ========================================
        total_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"[Pipeline] Complete in {total_time:.2f}ms (session: {session_id})")
        
        return layout
    
    async def _write_session_state(self, session_id: str, output: ReducerOutput):
        """Step 1: Write reducer state to Redis (blocking)."""
        await redis_client.set(
            RedisKeys.state(session_id),
            output.model_dump_json(),
            ttl=TTL.SESSION
        )
    
    async def _persist_to_mongodb(
        self,
        session_id: str,
        payload: ReducerPayload,
        constraints: Constraints
    ):
        """Step 2C: Append snapshot to MongoDB (non-blocking background task)."""
        try:
            doc = {
                "session_id": session_id,
                "page_type": payload.context.page_type,
                "device_type": payload.context.device_type,
                "timestamp": datetime.utcnow(),
                "reducer_output": payload.output.model_dump(),
                "constraints_summary": {
                    "hard": constraints.hard.model_dump(),
                    "exploration_budget": constraints.exploration_budget
                }
            }
            await mongo_client.db.reducer_snapshots.insert_one(doc)
            logger.debug(f"[MongoDB] Persisted snapshot for {session_id}")
        except Exception as e:
            logger.error(f"[MongoDB] Persistence failed: {e}")
    
    async def _vector_search_and_cache(
        self,
        session_id: str,
        output: ReducerOutput,
        constraints: Constraints
    ):
        """Step 2B: Vector search and cache results (non-blocking background task)."""
        try:
            # TODO: Implement actual vector search
            # For now, just log that this would happen
            logger.debug(f"[Vector] Would search for session {session_id}")
            
            # In production:
            # 1. Generate semantic intent string from reducer output
            # 2. Check semantic cache
            # 3. Embed if needed
            # 4. Query vector DB with constraint filters
            # 5. Store top-K in Redis
            
        except Exception as e:
            logger.error(f"[Vector] Search failed: {e}")
    
    async def _get_recently_used(self, session_id: str) -> Set[str]:
        """Get set of recently used component IDs."""
        try:
            data = await redis_client.get(RedisKeys.recently_used(session_id))
            if data:
                return set(json.loads(data))
        except Exception:
            pass
        return set()
    
    async def _update_recently_used(self, session_id: str, selection):
        """Update recently used set with new selections."""
        try:
            current = await self._get_recently_used(session_id)
            for comp in selection.selected_components:
                current.add(comp.component_id)
            
            # Keep only last 20 components
            if len(current) > 20:
                current = set(list(current)[-20:])
            
            await redis_client.set(
                RedisKeys.recently_used(session_id),
                json.dumps(list(current)),
                ttl=TTL.RECENTLY_USED
            )
        except Exception as e:
            logger.error(f"[Redis] Failed to update recently_used: {e}")
    
    async def get_cached_layout(self, session_id: str) -> Optional[LayoutSchema]:
        """Get cached layout from Redis if available."""
        try:
            data = await redis_client.get(RedisKeys.layout(session_id))
            if data:
                return LayoutSchema.model_validate_json(data)
        except Exception:
            pass
        return None


# Singleton instance
reducer_pipeline = ReducerPipeline()
