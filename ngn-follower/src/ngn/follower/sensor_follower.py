import json
import logging
import os
from time import sleep

from confluent_kafka import Consumer
from sap_hana_writer import SAPHanaWriter

log = logging.getLogger(__name__)


class SensorFollower:
    def __init__(self, sap_hana_writer: SAPHanaWriter):
        self._sap_hana_writer: SAPHanaWriter = sap_hana_writer
        self._kafka_conf: dict = {}

    def initialise(self):
        """Initialises the Sensor Follower by creating an Application
        connected to the Kafka cluster.
        """

        log.info("Initialising Sensor Follower...")
        kafka_broker_address = os.getenv("KAFKA_BROKER_ADDRESS")
        kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP")
        kafka_broker_sasl_port = os.getenv("KAFKA_BROKER_PORT")
        kafka_broker_sasl_username = os.getenv("KAFKA_SASL_USERNAME")
        kafka_broker_sasl_password = os.getenv("KAFKA_SASL_PASSWORD")
        kafka_broker_ca_certificate = os.getenv("KAFKA_CA_CERTIFICATE")

        self._kafka_conf = {
            "bootstrap.servers": f"{kafka_broker_address}:{kafka_broker_sasl_port}",
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN",
            "sasl.username": kafka_broker_sasl_username,
            "sasl.password": kafka_broker_sasl_password,
            "ssl.ca.location": kafka_broker_ca_certificate,
            "group.id": kafka_consumer_group,
        }

        log.info("Sensor Follower initialised successfully")

    def _receive_sensor_data(self):
        """Lists all topics from kafka and subscribe to all of them.
        Then it waits to receive kafka messages and adds them to the sap hana queue.
        """

        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                log.info("Connecting to Kafka broker...")
                consumer = Consumer(self._kafka_conf)
                log.info("Successfully connected to Kafka broker")
                # Subscribe to all topics
                consumer.subscribe(
                    [
                        "house_1",
                        "house_2",
                        "house_3",
                        "house_4",
                        "house_5",
                        "house_6",
                        "house_7",
                        "house_8",
                        "house_9",
                        "house_10",
                    ]
                )
                log.info("Subscribed to all topics. Waiting for Kafka messages...")

                while True:
                    # Wait for data from kafka
                    topic_msg = consumer.poll(1)

                    if topic_msg is None:
                        continue

                    if topic_msg.error() is not None:
                        log.error("Received a topic error %s", topic_msg.error())
                        continue

                    topic_name = topic_msg.topic()

                    # Decode kafka message
                    sensor_info = {}
                    try:
                        sensor_info: dict = json.loads(topic_msg.value())
                    except json.JSONDecodeError as ex:
                        log.warning(
                            "Failed to decode JSON msg %s from Kafka: %s", topic_msg, ex
                        )
                        continue
                    else:
                        log.debug(
                            "Received sensor info from topic %s: %s",
                            topic_name,
                            sensor_info,
                        )

                        # Add message to sap hana queue
                        self._sap_hana_writer.add_to_queue(sensor_info)
            except Exception as ex:
                log.error("Raised exception in publish_sensor_data %s", ex)
                log.debug(
                    "Attempting to reconnect in %ds (attempt n. %d)",
                    retry_delay,
                    attempt,
                )
                sleep(retry_delay)

    def start(self):
        self._receive_sensor_data()
