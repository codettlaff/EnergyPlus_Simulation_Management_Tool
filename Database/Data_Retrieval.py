# -*- coding: utf-8 -*-
"""
Data Retrieval Script

Created on: 2025-03-10

Purpose:
- Retrieve time-series data from the `timeseriesdata` table based on user-defined parameters.
- Retrieve metadata about buildings, zones, and simulated variables.

"""

import psycopg2
import pandas as pd
from datetime import datetime

# =============================================================================
# Database Connection
# =============================================================================
def connect_to_db():
    """
    Establish a connection to the buildings database.

    Returns:
        conn: psycopg2 connection object
    """
    try:
        # Define connection parameters
        connection_params = {
            'host': "localhost",  # Replace with your database host (e.g., 'localhost')
            'port': '5432',  # Replace with your database port (default: '5432')
            'database': "buildings",  # Replace with your database name
            'user': 'Casey',  # Replace with your database username
            'password': 'OfficeLarge'  # Replace with your database password
        }

        # Create connection to the database
        conn = psycopg2.connect(**connection_params)
        return conn

    except psycopg2.Error as e:
        print(f"Error while connecting to the database: {e}")
        raise

# =============================================================================
# Data Retrieval Functions
# =============================================================================
def get_variable_ids(conn, building_id='all', zone_name='all', variable_name='all'):
    """
    Retrieve a list of variable_ids based on building_id, zone_name, and variable_name.

    Args:
        conn: psycopg2 connection object.
        building_id (int or str): ID of the building or 'all' to ignore this filter.
        zone_name (list or str): List of zone names or 'all' to ignore this filter.
        variable_name (list or str): List of variable names or 'all' to ignore this filter.

    Returns:
        List of Ints: List of variable_ids if matches are found, None otherwise.

    Raises:
        psycopg2.Error: If there's an issue executing the SQL query.
    """
    try:
        # Step 1: Start constructing the base SQL query
        sql_query = """
            SELECT variables.variable_id
            FROM variables
            JOIN zones ON variables.zone_id = zones.zone_id
            WHERE 1=1
        """

        # Step 2: Prepare parameters for the SQL query
        parameters = []

        # Step 2.1: Filter by building_id, if provided
        if building_id != 'all':
            sql_query += " AND zones.building_id = %s"
            parameters.append(building_id)

        # Step 2.2: Filter by zone_name, if provided (accept list or single value)
        if zone_name != 'all':
            if isinstance(zone_name, list):
                sql_placeholders = ', '.join(['%s'] * len(zone_name))  # Create placeholders for the list
                sql_query += f" AND zones.zone_name IN ({sql_placeholders})"
                parameters.extend(zone_name)  # Add all items from the list to parameters
            else:
                sql_query += " AND zones.zone_name = %s"
                parameters.append(zone_name)

        # Step 2.3: Filter by variable_name, if provided (accept list or single value)
        if variable_name != 'all':
            if isinstance(variable_name, list):
                sql_placeholders = ', '.join(['%s'] * len(variable_name))  # Create placeholders for the list
                sql_query += f" AND variables.variable_name IN ({sql_placeholders})"
                parameters.extend(variable_name)  # Add all items from the list to parameters
            else:
                sql_query += " AND variables.variable_name = %s"
                parameters.append(variable_name)

        # Step 3: Execute the constructed query and fetch results
        with conn.cursor() as cursor:
            cursor.execute(sql_query, parameters)  # Execute the SQL query with parameters
            result_rows = cursor.fetchall()  # Fetch all matching rows

        # Step 4: Process the results
        if not result_rows:
            return None  # No variable_ids found
        else:
            return [row[0] for row in result_rows]  # Extract and return variable_id values

    except psycopg2.Error as database_error:
        print("An error occurred while executing the database query.")
        raise database_error
# Passed

def get_datetime_ids(conn, start_datetime='none', end_datetime='none'):
    """
    Retrieve datetime_ids based on the given start and end datetime range.

    Args:
        conn: psycopg2 connection object
        start_datetime (str): Start datetime (YYYY-MM-DD HH:MM:SS) or 'none' to ignore this filter.
        end_datetime (str): End datetime (YYYY-MM-DD HH:MM:SS) or 'none' to ignore this filter.

    Returns:
        List of Ints: A list of datetime_ids matching the given range, or None if no matches are found.

    Raises:
        psycopg2.Error: If there's an issue executing the SQL query.
    """
    try:
        # Step 1: Start building the base SQL query
        sql_query = """
            SELECT datetime_id
            FROM datetimes
            WHERE 1=1
        """

        # Step 2: Prepare parameters for the query
        parameters = []

        # Step 2.1: Add filter for start_datetime if provided
        if start_datetime != 'none':
            sql_query += " AND datetime >= %s"
            parameters.append(start_datetime)

        # Step 2.2: Add filter for end_datetime if provided
        if end_datetime != 'none':
            sql_query += " AND datetime <= %s"
            parameters.append(end_datetime)

        # Step 3: Execute the constructed SQL query
        with conn.cursor() as cursor:
            cursor.execute(sql_query, parameters)
            result_rows = cursor.fetchall()

        # Step 4: Process the results
        if not result_rows:
            return None  # No datetime_ids found
        else:
            return [row[0] for row in result_rows]  # Extract and return datetime_id values from the rows

    except psycopg2.Error as database_error:
        print("An error occurred while executing the database query.")
        raise database_error
# Passed

def get_timeseries_data(conn, building_id='all', zone_name='all', variable_name='all', start_datetime='none',
                        end_datetime='none'):
    """
    Retrieve time-series data for a specified building, zone, and variable within a given time range.

    Args:
        conn: psycopg2 connection object
        building_id (int or str): ID of the building or 'all' for all buildings
        zone_id (int or str): ID of the zone or 'all' for all zones
        variable_name (str): Name of the variable to retrieve or 'all' for all variables
        start_datetime (str): Start datetime (YYYY-MM-DD HH:MM:SS) or 'all' for no start datetime filter
        end_datetime (str): End datetime (YYYY-MM-DD HH:MM:SS) or 'all' for no end datetime filter

    Returns:
        pd.DataFrame: Retrieved time-series data

    Raises:
        MemoryError: If the size of the returned data frame is too large to load in memory.

    NEW Requirements:
    The columns in the timeseriesdata table are: variable_id, datetime_id, and value.
    variable_id is the primary key for the 'variables' table, with columns: variable_id, zone_id
    zone_id is the primary key for the 'zones' table, with columns: building_id, zone_name

    Process:
    from building_id, zone_name, variable_name, get variable_id
    from start_datetime, end_datetime, get array of datetime_id's

    TRY:
        # Initialize required IDs
        variable_ids = []
        datetime_ids = []

        # Step 1: Retrieve variable IDs based on given parameters (building_id, zone_name, variable_name).
        variable_ids = get_variable_ids(conn, building_id, zone_name, variable_name)

        # Step 2: Retrieve datetime IDs based on given time range (start_datetime, end_datetime).
        datetime_ids = get_datetime_ids(conn, start_datetime, end_datetime)

        # Step 3: Query the timeseriesdata table using retrieved IDs (variable_ids and datetime_ids).
        QUERY =
            SELECT *
            FROM timeseriesdata
            WHERE 1=1

        # Add filters:
        IF variable_ids is not empty:
            QUERY += " AND variable_id IN (%s)"  # Format for array
        IF datetime_ids is not empty:
            QUERY += " AND datetime_id IN (%s)"  # Format for array

        # Execute query to fetch the time-series data.
        QUERY_EXECUTION = EXECUTE QUERY with variable_ids and datetime_ids as parameters.
        FETCH RESULTS into a pandas DataFrame (df).

        # Step 4: Check DataFrame size in memory.
        ESTIMATED_MEMORY = Calculate memory usage of the DataFrame.
        IF ESTIMATED_MEMORY exceeds an appropriate threshold:
            RAISE MemoryError.

        RETURN the resulting DataFrame.

    EXCEPT psycopg2.Error AS db_error:
        PRINT database query error message.
        RAISE db_error.

    EXCEPT MemoryError AS mem_error:
        PRINT memory error message.
        RAISE mem_error.
    """
    pass

def get_buildings(conn):
    """
    Retrieve all buildings stored in the database.

    Args:
        conn: psycopg2 connection object

    Returns:
        pd.DataFrame: List of buildings with their metadata
    """
    pass

def get_zones_in_building(conn, building_id):
    """
    Retrieve all zones associated with a specific building.

    Args:
        conn: psycopg2 connection object
        building_id (int): ID of the building

    Returns:
        pd.DataFrame: List of zones in the building
    """
    pass

def get_variables_for_zone(conn, zone_id):
    """
    Retrieve all variables simulated for a specific zone.

    Args:
        conn: psycopg2 connection object
        zone_id (int): ID of the zone

    Returns:
        pd.DataFrame: List of variables associated with the zone
    """
    pass

def get_variables_for_building(conn, building_id):
    """
    Retrieve all variables simulated across all zones in a building.

    Args:
        conn: psycopg2 connection object
        building_id (int): ID of the building

    Returns:
        pd.DataFrame: List of unique variables across all zones in the building
    """
    pass

def get_datetime_range(conn):
    """
    Retrieve the available datetime range in the `timeseriesdata` table.

    Args:
        conn: psycopg2 connection object

    Returns:
        tuple: (min_datetime, max_datetime)
    """
    pass

# =============================================================================
# Helper Functions
# =============================================================================
def get_building_id(conn, building_name):
    """
    Retrieve the building_id given a building name.

    Args:
        conn: psycopg2 connection object
        building_name (str): Name of the building

    Returns:
        int: building_id if found, None otherwise
    """
    pass

def get_zone_id(conn, building_id, zone_name):
    """
    Retrieve the zone_id given a zone name and building_id.

    Args:
        conn: psycopg2 connection object
        building_id (int): ID of the building
        zone_name (str): Name of the zone

    Returns:
        int: zone_id if found, None otherwise
    """
    pass

def get_variable_id(conn, zone_id, variable_name):
    """
    Retrieve the variable_id given a zone_id and variable name.

    Args:
        conn: psycopg2 connection object
        zone_id (int): ID of the zone
        variable_name (str): Name of the variable

    Returns:
        int: variable_id if found, None otherwise
    """
    pass

##### Test #####

def get_datetime_ids_test():

    conn = connect_to_db()
    start_datetime = datetime.strptime('2013-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.strptime('2013-01-01 01:35:00', '%Y-%m-%d %H:%M:%S')

    datetime_ids = get_datetime_ids(conn, start_datetime, end_datetime)
    print(datetime_ids)

def get_variable_ids_test():

    conn = connect_to_db()

    # Test 1
    building_id = 582
    zone_name = 'CORE_ZN'
    variable_name = ['Facility_Total_HVAC_Electric_Demand_Power_', 'Site_Diffuse_Solar_Radiation_Rate_per_Area_']
    variable_ids = get_variable_ids(conn, building_id, zone_name, variable_name)
    print(f"Test 1 Variable IDs: {variable_ids}")

    # Test 2
    building_id = 582
    variable_name = 'Facility_Total_HVAC_Electric_Demand_Power_'
    print(f"Test 2 Variable IDs: {get_variable_ids(conn, building_id, variable_name=variable_name)}")

##### Main #####

get_variable_ids_test()