from logging import config

from constants import LOGGING_CONFIGURATION
from sap_hana_writer import create_writer
from sensor_follower import SensorFollower

config.dictConfig(LOGGING_CONFIGURATION)


def main():
    sap_hana_writer = create_writer()

    sensor_follower = SensorFollower(sap_hana_writer)
    sensor_follower.initialise()
    sensor_follower.start()


if __name__ == "__main__":
    main()
