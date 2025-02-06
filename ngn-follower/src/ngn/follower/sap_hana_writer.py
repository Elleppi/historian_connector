import logging
import os
from collections import namedtuple
from datetime import datetime
from queue import Queue
from threading import Thread
from time import sleep

import constants as cnt
import pytz
from hdbcli import dbapi

log = logging.getLogger(__name__)

SensorReading = namedtuple(
    "SensorReading",
    [
        "timestamp",
        "key",
        "description",
        "building_name",
        "floor_name",
        "room_name",
        "service_type",
        "object_name",
        "measurement_type",
        "unit_of_measure",
        "data",
        "float_data",
    ],
)


class SAPHanaWriter:
    """Class to queue updates and then every `HISTORIAN_SAP_HANA_STORE_EVERY_SEC` seconds
    write in a batch up to `HISTORIAN_SAP_HANA_MAX_BATCH_UPDATE` updates from the queue
    to the configured SAP Hana database.
    """

    def __init__(
        self,
        database_schema: str = cnt.DEFAULT_DATABASE_SCHEMA,
        database_table_name: str = cnt.DEFAULT_DATABASE_TABLE_NAME,
        max_batch_update: int = cnt.DEFAULT_MAX_BATCH_UPDATE,
        store_every_sec: int = cnt.DEFAULT_STORE_EVERY_SEC,
    ):
        self._store_every_sec = store_every_sec
        self._max_batch_update = max_batch_update
        self._update_queue = Queue()
        self._conn = None
        self._insert_statement = cnt.INSERT_COMMAND.format(
            schema=database_schema, table_name=database_table_name
        )
        log.debug("self._insert_statement %s", self._insert_statement)

    def open(
        self, user: str, password: str, address: str, port: int = cnt.DEFAULT_PORT
    ):
        """opens the sap hana database, the connection should automatically
        reconnect if the connection is broken
        https://help.sap.com/docs/HANA_SERVICE_CF/1efad1691c1f496b8b580064a6536c2d/ee592e89dcce4480a99571a4ae7a702f.html?locale=en-US

        Starts a background thread to periodically read from the
        update queue and store to the database

        Args:
            user (str): db user name
            password (str): db user password
            address (str): db instance address
            port (str, optional): db instance port. Defaults to "443".
            max_batch_update (int, optional): how large a batch of inserts
                to send to the db at one time. Defaults to 5000.

        Raises:
            dbapi.Error: if failed to open

        Returns:
            bool: True if database opened successfully otherwise False
        """

        log.info("Connecting to SAP Hana...")
        try:
            self._conn = dbapi.connect(
                address=address, port=port, user=user, password=password
            )
        except dbapi.Error as ex:
            log.error("Failed connecting to SAP Hana. %s", ex)
            raise

        log.info("Successfully connected to SAP Hana")

        # Start the store thread
        Thread(target=self._store).start()

    def close(self):
        """close connection to SAP Hana database"""

        if self._conn:
            log.info("Closing connection to SAP Hana")
            self._conn.close()
            self._conn = None

    def _write_from_queue(self):
        """write a batch of updates to the database"""

        try:
            rows = []
            while not self._update_queue.empty():
                item: SensorReading = self._update_queue.get()
                log.debug("Received a new message from queue: %s", item)
                rows.append(item)
                if len(rows) >= self._max_batch_update:
                    log.debug(
                        "breaking out of pulling from the queue _max_batch_update reached %d."
                        " Remaining queue size %d",
                        self._max_batch_update,
                        self._update_queue.qsize(),
                    )
                    break

            if rows:
                with self._conn and self._conn.cursor() as cursor:
                    cursor.executemany(self._insert_statement, rows)

                log.info("Written %d rows", len(rows))
        except Exception as ex:
            log.error("Error while writing to database: %s", ex)

    def _store(self):
        """write the queue of updates to the database every _store_every_sec seconds"""
        while self._conn:
            self._write_from_queue()
            sleep(self._store_every_sec)

    def add_to_queue(self, sensor_info: dict):
        """Queue a sensor update to be written to the database

        Args:
            sensor_info (dict): the update to queue for storage
        """

        last_shared_datetime_unix: float = sensor_info.get(cnt.LAST_SHARED_DATETIME)
        last_shared_value: float = sensor_info.get(cnt.LAST_SHARED_VALUE)

        float_data = None
        try:
            float_data = float(last_shared_value)
        except ValueError:
            # if data cannot be converted to a float
            # just store NULL as float_data
            pass

        last_shared_datetime = datetime.fromtimestamp(
            last_shared_datetime_unix
        ).replace(microsecond=0)
        timezone_aware = last_shared_datetime

        # Make timestamp timezone aware if it isn't already
        if last_shared_datetime.tzinfo is None:
            timezone_aware = last_shared_datetime.replace(tzinfo=pytz.UTC)

        new_item = SensorReading(
            key=sensor_info.get(cnt.SENSOR_KEY),
            timestamp=timezone_aware.isoformat(),
            description=sensor_info.get(cnt.SENSOR_NAME),
            building_name=sensor_info.get(cnt.BUILDING_NAME),
            floor_name=sensor_info.get(cnt.FLOOR_NAME),
            room_name=sensor_info.get(cnt.ROOM_NAME),
            service_type=sensor_info.get(cnt.SERVICE_TYPE),
            object_name=sensor_info.get(cnt.OBJECT_NAME),
            measurement_type=sensor_info.get(cnt.MEASUREMENT_TYPE),
            unit_of_measure=sensor_info.get(cnt.UNIT_OF_MEASURE),
            data=str(last_shared_value),
            float_data=float_data,
        )

        self._update_queue.put(new_item)

    @staticmethod
    def _conv_upper(in_list: list) -> list:
        if not in_list:
            log.warning("converting value list to upper, passed in list was empty")
            return []

        return [val.upper() for val in in_list]


def create_writer() -> SAPHanaWriter:
    """creates an instance of a SAPHanaWriter

    Raises:
        exceptions if failed to construct SAPHanaWriter or open connection

    Returns:
        SAPHanaWriter: an open SAPHanaWriter, caller should call close
        on the writer when they are finished with it
    """

    writer = SAPHanaWriter(
        database_schema=os.getenv(
            "HISTORIAN_SAP_HANA_DATABASE_SCHEMA", cnt.DEFAULT_DATABASE_SCHEMA
        ),
        database_table_name=os.getenv(
            "HISTORIAN_SAP_HANA_DATABASE_TABLE_NAME", cnt.DEFAULT_DATABASE_TABLE_NAME
        ),
        max_batch_update=int(
            os.getenv(
                "HISTORIAN_SAP_HANA_MAX_BATCH_UPDATE", str(cnt.DEFAULT_MAX_BATCH_UPDATE)
            )
        ),
        store_every_sec=int(
            os.getenv(
                "HISTORIAN_SAP_HANA_STORE_EVERY_SEC", str(cnt.DEFAULT_STORE_EVERY_SEC)
            )
        ),
    )
    writer.open(
        os.getenv("HISTORIAN_SAP_HANA_USER"),
        os.getenv("HISTORIAN_SAP_HANA_PASSWORD"),
        os.getenv("HISTORIAN_SAP_HANA_ADDRESS"),
        int(os.getenv("HISTORIAN_SAP_HANA_PORT", str(cnt.DEFAULT_PORT))),
    )

    return writer
