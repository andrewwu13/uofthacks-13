from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.events import EventBatch, EventResponse
from app.db.mongo_client import mongo_client
from app.sse.publisher import sse_publisher
from app.pipeline import reducer_pipeline
from app.models.reducer import ReducerOutput, ReducerContext, ReducerPayload
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)


async def process_telemetry_batch(batch: EventBatch):
    """
    Process telemetry batch in background:
    1. Save raw events to MongoDB 'telemetry' collection
    2. Save motor data to 'motor_telemetry' collection
    3. Run reducer pipeline to generate layout
    4. Publish layout update via SSE
    """
    try:
        # ========================================
        # Step 1: Save events to MongoDB
        # ========================================
        docs = []
        for event in batch.events:
            doc = event.model_dump()
            doc["session_id"] = batch.session_id
            doc["device_type"] = batch.device_type
            doc["batch_timestamp"] = batch.timestamp
            docs.append(doc)
            
        if docs:
            await mongo_client.telemetry.insert_many(docs)
            
        # Handle motor data if present
        if batch.motor:
            motor_doc = batch.motor.model_dump()
            motor_doc["session_id"] = batch.session_id 
            motor_doc["batch_timestamp"] = batch.timestamp
            await mongo_client.db.motor_telemetry.insert_one(motor_doc)

        logger.info(f"Stored {len(docs)} events for session {batch.session_id}")

        # ========================================
        # Step 2: Run Reducer Pipeline
        # ========================================
        # Create reducer payload from telemetry batch
        # In production, this would be computed from actual telemetry patterns
        reducer_output = ReducerOutput()  # Default preferences for now
        
        # Extract device_type for context
        device_type = batch.device_type if batch.device_type in ["desktop", "mobile", "tablet"] else "desktop"
        
        reducer_payload = ReducerPayload(
            output=reducer_output,
            context=ReducerContext(
                session_id=batch.session_id,
                device_type=device_type
            )
        )
        
        # Run pipeline to generate layout
        layout = await reducer_pipeline.process(reducer_payload)
        
        logger.info(f"Generated layout {layout.layout_id} for session {batch.session_id}")

        # ========================================
        # Step 3: Publish Layout via SSE
        # ========================================
        await sse_publisher.publish_layout_update(
            session_id=batch.session_id,
            layout_update={
                "layout_id": layout.layout_id,
                "layout_hash": layout.layout_hash,
                "components": [c.model_dump() for c in layout.components],
                "tokens": layout.tokens.model_dump(),
                "metadata": layout.metadata
            }
        )
        
        logger.info(f"Published layout update via SSE for session {batch.session_id}")

        # DEBUG: Log summary
        print(f"\n=== TELEMETRY → LAYOUT PIPELINE ===")
        print(f"Session: {batch.session_id}")
        print(f"Events: {len(docs)}")
        print(f"Layout: {layout.layout_id}")
        print(f"Components: {len(layout.components)}")
        print(f"===================================\n")
        
    except Exception as e:
        logger.error(f"Error processing telemetry batch: {e}")
        import traceback
        traceback.print_exc()


@router.post("/events", response_model=EventResponse)
async def receive_events(batch: EventBatch, background_tasks: BackgroundTasks):
    """
    Receive batched telemetry events from frontend.
    Processing is offloaded to background task to keep API fast.
    Returns immediately, pipeline runs async.
    """
    # Offload storage, pipeline, and SSE publishing to background
    background_tasks.add_task(process_telemetry_batch, batch)
    
    return EventResponse(
        received=len(batch.events),
        session_id=batch.session_id
    )

