import os
from faststream.rabbit import RabbitBroker

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
rabbit_broker = RabbitBroker(RABBITMQ_URL)
