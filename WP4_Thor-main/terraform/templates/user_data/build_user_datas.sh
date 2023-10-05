#! /bin/bash

path="scripts/"

cat "${path}"common_script_for_hive_and_sensors_HEADER.sh > user_data_for_hive.sh
cat "${path}"script_for_hive.sh >> user_data_for_hive.sh
cat "${path}"common_script_for_hive_and_sensors_TAIL.sh >> user_data_for_hive.sh


cat "${path}"common_script_for_hive_and_sensors_HEADER.sh > user_data_for_sensor.sh
cat "${path}"script_for_sensor.sh >> user_data_for_sensor.sh
cat "${path}"deploy_sensor_to_hive.sh >> user_data_for_sensor.sh
cat "${path}"common_script_for_hive_and_sensors_TAIL.sh >> user_data_for_sensor.sh
