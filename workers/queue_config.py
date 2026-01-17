"""
Queue configuration for Kafka/RedPanda
"""
from pydantic import BaseModel


class QueueConfig(BaseModel):
    """Configuration for event streaming queues"""
    
    # Kafka/RedPanda
    bootstrap_servers: str = "localhost:9092"
    
    # Topic names
    telemetry_topic: str = "telemetry-events"
    motor_state_topic: str = "motor-state-updates"
    layout_updates_topic: str = "layout-updates"
    
    # Consumer groups
    motor_state_group: str = "motor-state-processors"
    context_analyst_group: str = "context-analysts"
    layout_generator_group: str = "layout-generators"
    
    # Batch settings
    batch_size: int = 100
    batch_timeout_ms: int = 1000


queue_config = QueueConfig()
