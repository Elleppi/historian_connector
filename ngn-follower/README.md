# iotics-connector-ngn-saphana - SAP Hana Database Interface Package

Package to handle writing updates from CEV sensors into NGN's SAP Hana database

This package queues updates and then every `HISTORIAN_SAP_HANA_STORE_EVERY_SEC` seconds writes a batch of up to `HISTORIAN_SAP_HANA_MAX_BATCH_UPDATE` updates from the queue to the configured SAP Hana database.

### Example usage

Note: requires the following environmental variables to be set: HISTORIAN_SAP_HANA_USER, HISTORIAN_SAP_HANA_PASSWORD, HISTORIAN_SAP_HANA_ADDRESS

```python
import datetime
from time import sleep
from ngn.follower.sap_hana_writer import create_writer

# get an initialised writer
writer = create_writer()

# queue an update to be written to the database
writer.queue_update(datetime.datetime.now(datetime.timezone.utc).isoformat(), "1234", "House9_EnSuite_Electric_Lights_CumEnergy", "http://qudt.org/vocab/unit/W", "123")

# queue more updates here...

# wait for the update to be written
sleep(100)

# close the connection to the database before exiting the application
writer.close()
```

## Environment variables

-   HISTORIAN_SAP_HANA_USER - SAP Hana database user name - required
-   HISTORIAN_SAP_HANA_PASSWORD - SAP Hana database user password - required
-   HISTORIAN_SAP_HANA_ADDRESS - SAP Hana database address - required
-   HISTORIAN_SAP_HANA_PORT - SAP Hana database port - default value 443
-   HISTORIAN_SAP_HANA_DATABASE_SCHEMA - SAP Hana database schema - default value CEV
-   HISTORIAN_SAP_HANA_DATABASE_TABLE_NAME - SAP Hana database table name i.e. insert statement will contain [HISTORIAN_SAP_HANA_DATABASE_SCHEMA].[HISTORIAN_SAP_HANA_DATABASE_TABLE_NAME] e.g. CEV.EVENTLOG - default value EVENTLOG

-   HISTORIAN_SAP_HANA_MAX_BATCH_UPDATE - max number of updates that are batched to the db in one batch insert - default value 5000
-   HISTORIAN_SAP_HANA_STORE_EVERY_SEC - number of seconds to wait between pulling updates from the queue to be sent to the db as a batch - default value 30s
-   HISTORIAN_SAP_HANA_BUILDING_NAME_VALUES - a comma separated list of valid building names used to help parse the device's label into separate columns - default value -> list from spreadsheet
-   HISTORIAN_SAP_HANA_FLOOR_NAME_VALUES - ditto floor names
-   HISTORIAN_SAP_HANA_ROOM_NAME_VALUES - ditto room names
-   HISTORIAN_SAP_HANA_SERVICE_TYPE_VALUES - ditto service types
-   HISTORIAN_SAP_HANA_OBJECT_NAME_VALUES - ditto object names
-   HISTORIAN_SAP_HANA_MEASUREMENT_TYPE_VALUES - ditto measurement types

## Database Schema

The code is expecting the following schema

```sql
CREATE SCHEMA HISTORIAN;

CREATE COLUMN TABLE HISTORIAN.EventLog (timestamp TIMESTAMP, Key NVARCHAR(100) NOT NULL, Description NVARCHAR(1000), BuildingName NVARCHAR(100), FloorName NVARCHAR(100), RoomName NVARCHAR(100), ServiceType NVARCHAR(100), ObjectName NVARCHAR(100), MeasurementType NVARCHAR(100), UnitOfMeasure NVARCHAR(1000), Data NVARCHAR(100) NOT NULL, FloatData DOUBLE NULL);

ALTER TABLE HISTORIAN.EventLog ADD PRIMARY KEY(timestamp, key);
```
