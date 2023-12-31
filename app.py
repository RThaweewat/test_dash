import os
import time
import streamlit as st
from influxdb_client_3 import InfluxDBClient3, Point
from streamlit_image_coordinates import streamlit_image_coordinates
import pandas as pd
import numpy as np


def get_today_str():
    now = time.localtime()
    # YYYY-MM-DD HH-MM
    return f"{now.tm_year}-{now.tm_mon}-{now.tm_mday} {now.tm_hour}-{now.tm_min}"


def get_sensor_log():
    token = "OZpKr76YbuNbXqIzPSkVeLTkghXJuX7oZJiy4iBjDfEYrwD6swbSW7gQbH4qQMAq-oD9lQEwTD3CRGZzt3ekDQ=="
    org = "ytp"
    host = "https://us-east-1-1.aws.cloud2.influxdata.com"
    client = InfluxDBClient3(host=host, token=token, org=org)
    query = """
    SELECT * 
    FROM 'sensor_port' 
    """
    table = client.query(query=query, database="sensor_ytp", language="sql")
    # Convert to dataframe
    df = table.to_pandas().sort_values(by="time")
    select_col = ['humidity', 'temperature', 'ldrValue', 'pirValue', 'time', 'rssi', 'soilValue', 'waterTemperature']
    # resample time to 1 sec
    df['time'] = pd.to_datetime(df['time'])
    # drop where water temp is below 0
    df = df[df['waterTemperature'] > 0]
    # filter time 1 days ago
    df = df[df['time'] > pd.to_datetime('now') - pd.Timedelta(days=1)]
    df = df.groupby(pd.Grouper(key='time', freq='1s')).mean(numeric_only=True).reset_index().bfill().ffill()
    return df[select_col]


def get_motor_log():
    token = "DTn62dB5pz-0oGvlXfbCJttObVR5dzQhLA4vcu2-qs8AVidQIeB643sbOBGjVix2zTZE9lpQX9eHRZQ5eA-F9g=="
    org = "ytp"
    host = "https://us-east-1-1.aws.cloud2.influxdata.com"
    client = InfluxDBClient3(host=host, token=token, org=org)
    query = """
    SELECT * 
    FROM 'command'
    """
    table = client.query(query=query, database="sensor_ytp", language="sql")
    # Convert to dataframe
    df = table.to_pandas().sort_values(by="time")
    # drop where location_x, location_y is na
    df = df.dropna(subset=['location_x', 'location_y'])
    select_cols = ['time', 'run_time', 'location_x', 'location_y', 'command_time']
    df = df.sort_values(by='time')
    return df[select_cols].rename(columns={'command_time': 'duration'})


df_raw = get_sensor_log()
st.title("Eureka Dashboard")
col1, col2, col3, col4, col5 = st.columns(5)
# get avg temp and change in pass 5 mins


def get_percent_diff(df_raw, target_col):
    # Calculate the average temperature and round it
    avg_temperature = round(df_raw.set_index('time')[target_col].mean())

    # Assuming 'temperature' data is at a minute level
    last_minute_temperature = df_raw.set_index('time').last('1T')[target_col]

    # Calculate the percentage difference
    if len(last_minute_temperature) > 1:
        percent_diff = ((last_minute_temperature[-1] - last_minute_temperature[0]) / last_minute_temperature[0]) * 100
    else: # You can't compute % diff if there is no change in time
        percent_diff = np.nan

    # RuntimeError handling: If you try to compute % diff when last_minute_temperature[0] = 0
    try:
        percent_diff = ((last_minute_temperature[-1] - last_minute_temperature[0]) / last_minute_temperature[0]) * 100
    except ZeroDivisionError:
        percent_diff = np.nan

    return round(percent_diff, 2)


# Assume col1 is a Streamlit object that uses the metric method to display metrics on an app
col1.metric("Avg Temperature", round(df_raw['temperature'].mean()), str(get_percent_diff(df_raw, 'temperature')) + "%")
col2.metric("Avg Humidity", round(df_raw['humidity'].mean()), str(get_percent_diff(df_raw, 'humidity')) + "%")
col3.metric("Avg LDR", round(df_raw['ldrValue'].mean()), str(get_percent_diff(df_raw, 'ldrValue')) + "%")
col4.metric("Avg Water Temp", round(df_raw['waterTemperature'].mean()), str(get_percent_diff(df_raw, 'waterTemperature')) + "%")
col5.metric("Avg Soil Moisture", round(df_raw['soilValue'].mean()), str(get_percent_diff(df_raw, 'soilValue')) + "%")

st.subheader("Water Schedule")
st.dataframe(get_motor_log().head(10), use_container_width=True)

#%%
