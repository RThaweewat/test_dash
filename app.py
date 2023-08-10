import streamlit as st


import os, time
from influxdb_client_3 import InfluxDBClient3, Point


def get_dataset():
	token = os.environ.get("OZpKr76YbuNbXqIzPSkVeLTkghXJuX7oZJiy4iBjDfEYrwD6swbSW7gQbH4qQMAq-oD9lQEwTD3CRGZzt3ekDQ==")
	org = "ytp"
	host = "https://us-east-1-1.aws.cloud2.influxdata.com"
	client = InfluxDBClient3(host=host, token=token, org=org)

	query = """SELECT *
	FROM "sensor_port"
	WHERE
	time >= now() - interval '1 day'"""

	# Execute the query
	table = client.query(query=query, database="sensor_processed", language='influxql')
	# Convert to dataframe
	df = table.to_pandas().sort_values(by="time")
	return df


st.dataframe(get_dataset().head(10))
st.title("Eureka Dashboard")

