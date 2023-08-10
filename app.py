import os
import time
import streamlit as st
from influxdb_client_3 import InfluxDBClient3, Point
from streamlit_image_coordinates import streamlit_image_coordinates


def get_today_str():
    now = time.localtime()
    # YYYY-MM-DD HH-MM
    return f"{now.tm_year}-{now.tm_mon}-{now.tm_mday} {now.tm_hour}-{now.tm_min}"


def get_dataset():
    token = "OZpKr76YbuNbXqIzPSkVeLTkghXJuX7oZJiy4iBjDfEYrwD6swbSW7gQbH4qQMAq-oD9lQEwTD3CRGZzt3ekDQ=="
    org = "ytp"
    host = "https://us-east-1-1.aws.cloud2.influxdata.com"
    client = InfluxDBClient3(host=host, token=token, org=org)
    query = """SELECT * FROM "sensor_port" WHERE time >= now() - interval '1 day'"""
    table = client.query(query=query, database="sensor_processed", language="influxql")
    # Convert to dataframe
    df = table.to_pandas().sort_values(by="time")
    return df


st.dataframe(get_dataset().head(10))
st.subheader(get_today_str())
st.title("Eureka Dashboard")
value = streamlit_image_coordinates("https://placekitten.com/200/300")
st.write(value)
