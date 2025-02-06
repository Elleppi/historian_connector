import pytest
from ngn.follower.sap_hana_writer import SAPHanaWriter, SensorReading

SENSOR_KEY = "sensor_key"
SENSOR_NAME = "sensor_name"
BUILDING_NAME = "building_name"
ROOM_NAME = "room_name"
FLOOR_NAME = "floor_name"
SERVICE_TYPE = "service_type"
OBJECT_NAME = "object_name"
MEASUREMENT_TYPE = "measurement_type"
UNIT_OF_MEASURE = "unit_of_measure"
LAST_SHARED_VALUE = "last_shared_value"
LAST_SHARED_DATETIME = "last_shared_datetime"


@pytest.mark.parametrize(
    "sensor_info, exp_value",
    [
        (
            {
                SENSOR_KEY: "CO@2_0_205",
                SENSOR_NAME: "House 2_Floor1_Kitchen_Electric_Hob_Current",
                BUILDING_NAME: "House 2",
                ROOM_NAME: "Kitchen",
                FLOOR_NAME: "Floor1",
                SERVICE_TYPE: "Electric",
                OBJECT_NAME: "Hob",
                MEASUREMENT_TYPE: "Current",
                UNIT_OF_MEASURE: "MegaAmpere",
                LAST_SHARED_VALUE: 2.0,
                LAST_SHARED_DATETIME: 1738067935.285771,
            },
            SensorReading(
                key="CO@2_0_205",
                timestamp="2025-01-28T12:38:55+00:00",
                description="House 2_Floor1_Kitchen_Electric_Hob_Current",
                building_name="House 2",
                floor_name="Floor1",
                room_name="Kitchen",
                service_type="Electric",
                object_name="Hob",
                measurement_type="Current",
                unit_of_measure="MegaAmpere",
                data="2.0",
                float_data=2.0,
            ),
        ),
        (
            {
                SENSOR_KEY: "CO@1_3_13",
                SENSOR_NAME: "House 1_Floor1_Kitchen_Water_SinkHot_Temp",
                BUILDING_NAME: "House 1",
                ROOM_NAME: "Kitchen",
                FLOOR_NAME: "Floor1",
                SERVICE_TYPE: "Water",
                OBJECT_NAME: "SinkHot",
                MEASUREMENT_TYPE: "Temp",
                UNIT_OF_MEASURE: "Celsius",
                LAST_SHARED_VALUE: 2.0,
                LAST_SHARED_DATETIME: 1738067935.285771,
            },
            SensorReading(
                key="CO@1_3_13",
                timestamp="2025-01-28T12:38:55+00:00",
                description="House 1_Floor1_Kitchen_Water_SinkHot_Temp",
                building_name="House 1",
                floor_name="Floor1",
                room_name="Kitchen",
                service_type="Water",
                object_name="SinkHot",
                measurement_type="Temp",
                unit_of_measure="Celsius",
                data="2.0",
                float_data=2.0,
            ),
        ),
        (
            {
                SENSOR_KEY: "CO@4_3_148",
                SENSOR_NAME: "House 4_WWHRS_ShowerMIX_Temp",
                BUILDING_NAME: "House 4",
                ROOM_NAME: "",
                FLOOR_NAME: "",
                SERVICE_TYPE: "WWHRS",
                OBJECT_NAME: "ShowerMIX",
                MEASUREMENT_TYPE: "Temp",
                UNIT_OF_MEASURE: "Celsius",
                LAST_SHARED_VALUE: 2.0,
                LAST_SHARED_DATETIME: 1738067935.285771,
            },
            SensorReading(
                key="CO@4_3_148",
                timestamp="2025-01-28T12:38:55+00:00",
                description="House 4_WWHRS_ShowerMIX_Temp",
                building_name="House 4",
                floor_name="",
                room_name="",
                service_type="WWHRS",
                object_name="ShowerMIX",
                measurement_type="Temp",
                unit_of_measure="Celsius",
                data="2.0",
                float_data=2.0,
            ),
        ),
    ],
)
def test_add_to_queue(sensor_info, exp_value):
    writer = SAPHanaWriter()
    writer.add_to_queue(sensor_info)

    if exp_value:
        assert not writer._update_queue.empty()

        sensor_info = writer._update_queue.get(block=False)
        assert sensor_info.timestamp == exp_value.timestamp
        assert sensor_info.key == exp_value.key
        assert sensor_info.description == exp_value.description
        assert sensor_info.building_name == exp_value.building_name
        assert sensor_info.floor_name == exp_value.floor_name
        assert sensor_info.room_name == exp_value.room_name
        assert sensor_info.service_type == exp_value.service_type
        assert sensor_info.object_name == exp_value.object_name
        assert sensor_info.measurement_type == exp_value.measurement_type
        assert sensor_info.unit_of_measure == exp_value.unit_of_measure
        assert sensor_info.data == exp_value.data
        assert sensor_info.float_data == exp_value.float_data
