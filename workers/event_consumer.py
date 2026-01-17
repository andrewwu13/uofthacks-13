"""
Event consumer - Kafka/RedPanda consumer for telemetry events
"""
import asyncio
from typing import Callable
from workers.queue_config import queue_config


class EventConsumer:
    """
    Consumes telemetry events from Kafka/RedPanda.
    Distributes events to appropriate processing streams.
    """
    
    def __init__(self):
        self.consumer = None
        self.running = False
        self.handlers: dict[str, Callable] = {}
    
    async def start(self):
        """Start consuming events"""
        # TODO: Initialize Kafka consumer
        # from aiokafka import AIOKafkaConsumer
        # self.consumer = AIOKafkaConsumer(
        #     queue_config.telemetry_topic,
        #     bootstrap_servers=queue_config.bootstrap_servers,
        #     group_id=queue_config.motor_state_group,
        # )
        # await self.consumer.start()
        self.running = True
        await self._consume_loop()
    
    async def stop(self):
        """Stop consuming events"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register handler for event type"""
        self.handlers[event_type] = handler
    
    async def _consume_loop(self):
        """Main consumption loop"""
        while self.running:
            # TODO: Replace with actual Kafka consumption
            # async for msg in self.consumer:
            #     await self._process_message(msg)
            await asyncio.sleep(0.1)
    
    async def _process_message(self, message):
        """Process a consumed message"""
        try:
            # TODO: Deserialize and route to handler
            event_type = message.get("type")
            if event_type in self.handlers:
                await self.handlers[event_type](message)
        except Exception as e:
            print(f"Error processing message: {e}")


event_consumer = EventConsumer()
