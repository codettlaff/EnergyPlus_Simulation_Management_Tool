# -*- coding: utf-8 -*-
"""
Data Retrieval Script

Created on: 2025-05-05

Purpose:
- Retrieve time-series data from the `timeseriesdata` table based on user-defined parameters.
- Retrieve metadata about buildings, zones, and simulated variables.

"""

import psycopg2
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

def connect_to_db(host="localhost", port="5432", database="buildings", user="Casey", password="OfficeLarge"):

    # Define connection parameters
    connection_params = {
        'host': host,  # Replace with your database host (e.g., 'localhost')
        'port': port,  # Replace with your database port (default: '5432')
        'database': database,  # Replace with your database name
        'user': user,  # Replace with your database username
        'password': password  # Replace with your database password
    }

    conn = psycopg2.connect(**connection_params)
    return conn

# =============================================================================
# Helper Functions
# =============================================================================

def get_ids(conn, table_name, column_values):
    """
    Gets the primary key(s) of a table based on the values of the columns.
    """
    # Construct the WHERE clause
    where_clauses = " AND ".join([f"{col} = %s" for col in column_values.keys()])
    query = f"SELECT id FROM {table_name} WHERE {where_clauses}"

    column_values = list(column_values.values())

    # Execute the query
    with conn.cursor() as cur:
        cur.execute(query, column_values)
        result = cur.fetchone()

    return result[0] if result else None

def get_timeseries_data(conn, variable_ids, datetime_ids):
    """
    Retrieve time series data for the given variable IDs and datetime IDs.

    :param conn: Database connection object
    :param variable_ids: A list or tuple of variable IDs to filter
    :param datetime_ids: A list or tuple of datetime IDs to filter
    :return: Pandas DataFrame with the retrieved data
    """
    query = """
    SELECT variable_id, datetime_id, value
    FROM timeseriesdata
    WHERE variable_id = ANY(%s) AND datetime_id = ANY(%s)
    """

    with conn.cursor() as cur:
        cur.execute(query, (list(variable_ids), list(datetime_ids)))
        data = cur.fetchall()

    # Convert the result into a Pandas DataFrame
    df = pd.DataFrame(data, columns=["variable_id", "datetime_id", "value"])
    return df
# Passed