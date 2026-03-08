
import pytest
import asyncio
from app.db.redis_client import redis_client
from app.db.mongo_client import mongo_client
from app.pipeline import reducer_pipeline
from app.models.reducer import ReducerOutput, ReducerContext, ReducerPayload

@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_e2e_live():
    """Live integration test for the full reducer pipeline."""
    # Connect to services
    await redis_client.connect()
    await mongo_client.connect()

    try:
        # Create test payload
        payload = ReducerPayload(
            output=ReducerOutput(), 
            context=ReducerContext(session_id="test_integration_001")
        )

        # Run pipeline
        layout = await reducer_pipeline.process(payload)

        assert layout.layout_id is not None
        assert len(layout.components) > 0
        assert len(layout.layout_hash) > 0
    finally:
        # Cleanup
        await redis_client.disconnect()
        await mongo_client.disconnect()
