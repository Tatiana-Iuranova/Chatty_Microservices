# utils/messaging.py
from faststream.rabbit import RabbitBroker
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

# Экспортируем брокер, с которым можно работать (в том числе публиковать)
rabbit_broker = RabbitBroker(RABBITMQ_URL)
