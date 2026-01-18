import json
import logging
import math
from typing import List, Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.events import EventBatch, EventResponse, MotorTelemetryPayload
from app.db.mongo_client import mongo_client
from app.db.redis_client import redis_client
from app.pipeline.redis_keys import RedisKeys
from app.sse.publisher import sse_publisher
from app.pipeline import reducer_pipeline
from app.models.reducer import ReducerOutput, ReducerContext, ReducerPayload

# Import Agent Graph
import sys
import os
# Ensure root directory is in path for agents import
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from agents.graph import run_layout_generation
except ImportError:
    logging.getLogger(__name__).warning("Could not import agents.graph. Inference will be disabled.")
    run_layout_generation = None


router = APIRouter()
logger = logging.getLogger(__name__)


def transform_motor_samples(motor: MotorTelemetryPayload) -> List[Dict]:
    """
    Transform frontend motor samples [[x, y], ...] into format expected by motor_analyzer.
    
    Calculates velocity and acceleration from position samples.
    """
    if not motor or not motor.samples or len(motor.samples) < 2:
        return []
    
    samples = motor.samples
    dt_sec = motor.dt / 1000.0  # Convert ms to seconds
    result = []
    
    prev_vel_x, prev_vel_y = 0.0, 0.0
    
    for i, sample in enumerate(samples):
        x, y = sample[0], sample[1]
        timestamp = motor.t0 + (i * motor.dt)
        
        # Calculate velocity (derivative of position)
        if i > 0:
            prev_x, prev_y = samples[i-1][0], samples[i-1][1]
            vel_x = (x - prev_x) / dt_sec if dt_sec > 0 else 0
            vel_y = (y - prev_y) / dt_sec if dt_sec > 0 else 0
        else:
            vel_x, vel_y = 0.0, 0.0
        
        # Calculate acceleration (derivative of velocity)
        if i > 0:
            acc_x = (vel_x - prev_vel_x) / dt_sec if dt_sec > 0 else 0
            acc_y = (vel_y - prev_vel_y) / dt_sec if dt_sec > 0 else 0
        else:
            acc_x, acc_y = 0.0, 0.0
        
        result.append({
            "timestamp": timestamp,
            "position": {"x": x, "y": y},
            "velocity": {"x": vel_x, "y": vel_y},
            "acceleration": {"x": acc_x, "y": acc_y},
        })
        
        prev_vel_x, prev_vel_y = vel_x, vel_y
    
    return result


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
        
        # 1. Fetch current preferences from Redis
        current_preferences = {}
        try:
            cached_state = await redis_client.get(RedisKeys.state(batch.session_id))
            if cached_state:
                current_preferences = json.loads(cached_state)
        except Exception as e:
            logger.warning(f"Failed to fetch cached state: {e}")

        # 2. Run Agent Graph (Inference)
        reducer_output = None
        
        if run_layout_generation:
            try:
                # Prepare arguments for agent graph
                # Transform motor samples to format expected by motor_analyzer
                motor_data = []
                if batch.motor:
                    motor_data = transform_motor_samples(batch.motor)
                    logger.info(f"Transformed {len(motor_data)} motor samples for analysis")
                
                # Extract interaction events (all events in batch)
                interaction_events = [e.model_dump() for e in batch.events]
                
                # Filter 'loud' module events as a subset
                loud_events = [
                    e for e in interaction_events
                    if (e.get('metadata') or {}).get('is_loud', False) or
                    "loud" in (e.get('target_id') or "").lower()
                ]
                
                logger.info(f"Triggering Agent Workflow for session {batch.session_id}...")
                
                user_profile_dict = await run_layout_generation(
                    session_id=batch.session_id,
                    telemetry_batch=motor_data,
                    interactions=interaction_events,
                    loud_module_events=loud_events,
                    current_preferences=current_preferences,
                )
                
                # Map UserProfile to ReducerOutput
                if user_profile_dict:
                    # UserProfile has 'visual', 'interaction', 'behavioral' which match ReducerOutput
                    # ReducerOutput will ignore 'inferred' field if configured to ignore extras,
                    # or we can construct explicitly to be safe.
                    reducer_output = ReducerOutput(
                        visual=user_profile_dict.get('visual', {}),
                        interaction=user_profile_dict.get('interaction', {}),
                        behavioral=user_profile_dict.get('behavioral', {}),
                    )
                    logger.info(f"Agent Workflow successful. Generated profile: {user_profile_dict.get('inferred', {}).get('summary')}")
                    
            except Exception as e:
                logger.error(f"Agent Workflow failed: {e}")
                # Fallback to default will happen below if reducer_output is None
        
        # Fallback if agent failed or disabled
        if not reducer_output:
            logger.warning("Using default ReducerOutput (Agent skipped or failed)")
            reducer_output = ReducerOutput() 
        
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

