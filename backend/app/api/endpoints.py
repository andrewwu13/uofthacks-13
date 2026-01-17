from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.product import Product
from app.models.telemetry import MotorTelemetry, TelemetryEventsBatch
from app.services.product_service import product_service
from app.services.telemetry_service import telemetry_service

router = APIRouter()

@router.get("/products/{session_id}", response_model=List[Product])
async def get_products(session_id: str):
    # TODO: Load persistent user preferences using session_id
    return product_service.get_products_for_session(session_id)

@router.post("/telemetry/motor")
async def post_motor_telemetry(data: MotorTelemetry):
    return await telemetry_service.process_motor_telemetry(data)

@router.post("/telemetry/events")
async def post_events_telemetry(data: TelemetryEventsBatch):
    # TODO: Identify if this session should be merged with an existing user profile for persistence
    return await telemetry_service.process_events_telemetry(data)
