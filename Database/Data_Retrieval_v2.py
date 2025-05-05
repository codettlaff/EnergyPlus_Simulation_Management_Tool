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

    # Execute the query
    with conn.cursor() as cur:
        cur.execute(query, list(column_values.values()))
        result = cur.fetchone()

    return result[0] if result else None

def get_building_ids(conn, building_type='all', prototype='all', energy_code='all', idf_climate_zone='all', heating_type='all', foundation_type='all'):

    column_values = {}
    if not building_type == 'all': column_values['building_type'] = building_type
    if not prototype == 'all': column_values['prototype'] = prototype
    if not energy_code == 'all': column_values['energy_code'] = energy_code
    if not idf_climate_zone == 'all': column_values['idf_climate_zone'] = idf_climate_zone
    if not heating_type == 'all' or heating_type == 'none': column_values['heating_type'] = heating_type
    if not foundation_type == 'all' or foundation_type == 'none': column_values['foundation_type'] = foundation_type

    ids = get_ids(conn, 'building_prototypes', column_values)
    return ids

conn = connect_to_db()
ids = get_building_ids(conn, building_type='Commercial', prototype='Hospital', energy_code='ASHRAE2013', idf_climate_zone='A1')
print(ids)