from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
from app.models.product import Product
from app.models.telemetry import MotorTelemetry, TelemetryEventsBatch
from app.services.product_service import product_service
from app.services.telemetry_service import telemetry_service

from app.services.shopify_service import Shopify500Scraper
import os

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str


@router.get("/products/{session_id}", response_model=List[Product])
async def get_products(session_id: str):
    # TODO: Load persistent user preferences using session_id
    return product_service.get_products_for_session(session_id)


def run_scraper(session_id: str, url: str):
    output_file = f"session_{session_id}_products.json"
    scraper = Shopify500Scraper(target_stores=[url], output_file=output_file)
    scraper.run()

@router.post("/scrape/{session_id}")
async def scrape_store(session_id: str, request: ScrapeRequest, background_tasks: BackgroundTasks):
    domain = request.url
    # Clean the URL if it contains http/https
    if "://" in domain:
        domain = domain.split("://")[1]
    if domain.endswith("/"):
        domain = domain[:-1]

    # Instead of running synchronously and blocking, we could run in background or run synchronously?
    # The user wants to show a loading state while scraping, so we probably want to run synchronously.
    # We will await it, but since `Shopify500Scraper` uses `requests` synchronously, we should run it in a threadpool
    # or just run it directly. Let's run it directly for now, or using run_in_threadpool
    import anyio.to_thread
    await anyio.to_thread.run_sync(run_scraper, session_id, domain)
    
    return {"status": "success", "message": f"Scraped {domain}", "session_id": session_id}


# @router.post("/telemetry/motor")
# async def post_motor_telemetry(data: MotorTelemetry):
#     return await telemetry_service.process_motor_telemetry(data)

# @router.post("/telemetry/events")
# async def post_events_telemetry(data: TelemetryEventsBatch):
#     # TODO: Identify if this session should be merged with an existing user profile for persistence
#     return await telemetry_service.process_events_telemetry(data)
