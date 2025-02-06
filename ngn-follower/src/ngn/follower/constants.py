import os

SENSOR_NAME = "sensor_name"
SENSOR_KEY = "sensor_key"
BUILDING_NAME = "building_name"
FLOOR_NAME = "floor_name"
ROOM_NAME = "room_name"
SERVICE_TYPE = "service_type"
OBJECT_NAME = "object_name"
MEASUREMENT_TYPE = "measurement_type"
LAST_SHARED_VALUE = "last_shared_value"
LAST_SHARED_DATETIME = "last_shared_datetime"
UNIT_OF_MEASURE = "unit_of_measure"

DEFAULT_MAX_BATCH_UPDATE = 5000
DEFAULT_STORE_EVERY_SEC = 30
DEFAULT_PORT = 443
DEFAULT_DATABASE_SCHEMA = "CEV"
DEFAULT_DATABASE_TABLE_NAME = "EVENTLOG"

INSERT_COMMAND = (
    "INSERT INTO {schema}.{table_name} VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
)

# Logging Configurations
logging_level = os.getenv("LOGGING_LEVEL")
LOGGING_CONFIGURATION = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[%(asctime)s] [%(module)s] %(levelname)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": logging_level,
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {"level": logging_level, "handlers": ["console"]},
}
