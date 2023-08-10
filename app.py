import os
import time
import streamlit as st
from influxdb_client_3 import InfluxDBClient3, Point
from streamlit_image_coordinates import streamlit_image_coordinates
import pandas as pd


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
    select_col = ['humidity', 'temperature', 'ldrValue', 'pirValue', 'time', 'rssi', 'soilValue']
    # resample time to 1 sec
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time').resample('1S').mean().reset_index().bfill().ffill()
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
    return df


df_raw = get_sensor_log()
col1, col2, col3 = st.columns(3)
# get avg temp and change in pass 5 mins
st.title("Eureka Dashboard")
col1.metric("Avg Temperature", df_raw['temperature'].mean())
col2.metric("Wind", "9 mph", "-8%")
col3.metric("Humidity", "86%", "4%")
st.dataframe(get_motor_log().head(10))
st.subheader(get_today_str())

value = streamlit_image_coordinates("https://placekitten.com/200/300")
st.write(value)
