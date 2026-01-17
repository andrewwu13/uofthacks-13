from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.events import EventBatch, EventResponse
from app.db.mongo_client import mongo_client
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

async def process_telemetry_batch(batch: EventBatch):
    """
    Process telemetry batch in background:
    1. Save raw events to MongoDB 'telemetry' collection
    2. Save motor data to 'motor_telemetry' (optional or merged)
    3. (Future) Forward to Agent/LangGraph
    """
    try:
        # Prepare docs for insertion
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
            # Ensure session_id matches (it should, but good to be safe)
            motor_doc["session_id"] = batch.session_id 
            motor_doc["batch_timestamp"] = batch.timestamp
            
            # Use specific collection for heavy motor data
            await mongo_client.db.motor_telemetry.insert_one(motor_doc)
            
        # DEBUG: Log full payload structure as requested
        import json
        print("\n=== TELEMETRY PAYLOAD RECEIVED ===")
        print(json.dumps(batch.model_dump(), indent=2, default=str))
        print("==================================\n")

        logger.info(f"Processed batch {batch.timestamp} for session {batch.session_id}: {len(docs)} events")
        
    except Exception as e:
        logger.error(f"Error processing telemetry batch: {e}")

@router.post("/events", response_model=EventResponse)
async def map_events(batch: EventBatch, background_tasks: BackgroundTasks):
    """
    Receive batched telemetry events from frontend.
    Processing is offloaded to background task to keep API fast.
    """
    # Quick validation or pre-processing could happen here
    
    # Offload storage and agent processing
    background_tasks.add_task(process_telemetry_batch, batch)
    
    return EventResponse(
        received=len(batch.events),
        session_id=batch.session_id
    )
