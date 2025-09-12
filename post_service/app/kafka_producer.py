from confluent_kafka import Producer
import json
import os

conf = {
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
}

producer = Producer(conf)


def send_event(topic: str, value: dict):
    producer.produce(topic, key=value.get("user_id", ""), value=json.dumps(value).encode("utf-8"))
    producer.flush()