# backend/scripts/test_pipeline_e2e.py
import asyncio
from app.db.redis_client import redis_client
from app.db.mongo_client import mongo_client
from app.pipeline import reducer_pipeline
from app.models.reducer import ReducerOutput, ReducerContext, ReducerPayload

async def main():
    # Connect to services
    await redis_client.connect()
    await mongo_client.connect()
    
    # Create test payload
    payload = ReducerPayload(
        output=ReducerOutput(),
        context=ReducerContext(session_id="test_e2e_001")
    )
    
    # Run pipeline
    layout = await reducer_pipeline.process(payload)
    
    print(f"✅ Layout generated: {layout.layout_id}")
    print(f"   Components: {len(layout.components)}")
    print(f"   Hash: {layout.layout_hash[:16]}...")
    
    # Cleanup
    await redis_client.disconnect()
    await mongo_client.disconnect()

asyncio.run(main())