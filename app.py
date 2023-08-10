import os
import time
import streamlit as st
from influxdb_client_3 import InfluxDBClient3, Point
from streamlit_image_coordinates import streamlit_image_coordinates


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
    table = client.query(query=query, database="sensor_processed", language="sql")
    # Convert to dataframe
    df = table.to_pandas().sort_values(by="time")
    return df


def get_motor_log():
    token = "DTn62dB5pz-0oGvlXfbCJttObVR5dzQhLA4vcu2-qs8AVidQIeB643sbOBGjVix2zTZE9lpQX9eHRZQ5eA-F9g=="
    org = "ytp"
    host = "https://us-east-1-1.aws.cloud2.influxdata.com"
    client = InfluxDBClient3(host=host, token=token, org=org)
    query = """
    SELECT * 
    FROM 'command'
    """
    table = client.query(query=query, database="sensor_processed", language="sql")
    # Convert to dataframe
    df = table.to_pandas().sort_values(by="time")
    return df


st.dataframe(get_sensor_log().head(10))
st.dataframe(get_motor_log().head(10))
st.subheader(get_today_str())
st.title("Eureka Dashboard")
value = streamlit_image_coordinates("https://placekitten.com/200/300")
st.write(value)
