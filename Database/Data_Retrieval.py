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
    Retrieve a single variable_id based on building_id, zone_name, and variable_name.

    Args:
        conn: psycopg2 connection object
        building_id (int or str): ID of the building or 'all' to ignore this filter
        zone_name (list or str): List of names of the zones or 'all' to ignore this filter
        variable_name (list or str): List of name of the variables or 'all' to ignore this filter

    Returns:
        List of Ints: Variable_ids if found, None otherwise

    Raises:
        psycopg2.Error: If there's an issue executing the SQL query.

    TRY:
        # Step 1: Start constructing the base SQL query
        SQL_QUERY =
            SELECT variables.variable_id
            FROM variables
            JOIN zones ON variables.zone_id = zones.zone_id
            WHERE 1=1

        # Step 2: Prepare parameters for the SQL query
        PARAMETERS = []

        # Step 2.1: Filter by building_id, if provided
        IF building_id != 'all':
            SQL_QUERY += " AND zones.building_id = %s"
            ADD building_id TO PARAMETERS

        # Step 2.2: Filter by zone_name, if provided (accept list or single value)
        IF zone_name != 'all':
            IF zone_name IS A LIST:
                SQL_PLACEHOLDERS = CREATE PLACEHOLDER STRING USING THE LIST LENGTH (e.g., %s, %s, ...)
                SQL_QUERY += f" AND zones.zone_name IN ({SQL_PLACEHOLDERS})"
                ADD ALL ITEMS FROM zone_name TO PARAMETERS
            ELSE:
                SQL_QUERY += " AND zones.zone_name = %s"
                ADD zone_name TO PARAMETERS

        # Step 2.3: Filter by variable_name, if provided (accept list or single value)
        IF variable_name != 'all':
            IF variable_name IS A LIST:
                SQL_PLACEHOLDERS = CREATE PLACEHOLDER STRING USING THE LIST LENGTH (e.g., %s, %s, ...)
                SQL_QUERY += f" AND variables.variable_name IN ({SQL_PLACEHOLDERS})"
                ADD ALL ITEMS FROM variable_name TO PARAMETERS
            ELSE:
                SQL_QUERY += " AND variables.variable_name = %s"
                ADD variable_name TO PARAMETERS

        # Step 3: Execute the constructed query and fetch results
        WITH conn.cursor() AS CURSOR:
            CURSOR.EXECUTE(SQL_QUERY, PARAMETERS)
            RESULT_ROWS = FETCH ALL ROWS

        # Step 4: Process the result
        IF RESULT_ROWS IS EMPTY:
            RETURN None  # No variable IDs found
        ELSE:
            RETURN A LIST OF variable_id VALUES FROM RESULT_ROWS

    EXCEPT psycopg2.Error AS DATABASE_ERROR:
        PRINT "An error occurred while executing the database query."
        RAISE DATABASE_ERROR

    """
    pass

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

    TRY:
        # Step 1: Start building the base SQL query
        SQL_QUERY =
            SELECT datetime_id
            FROM datetimes
            WHERE 1=1

        # Step 2: Prepare parameters for the query
        PARAMETERS = []

        # Step 2.1: Add filter for start_datetime if it is not 'none'
        IF start_datetime != 'none':
            SQL_QUERY += " AND datetime_value >= %s"
            ADD start_datetime TO PARAMETERS

        # Step 2.2: Add filter for end_datetime if it is not 'none'
        IF end_datetime != 'none':
            SQL_QUERY += " AND datetime_value <= %s"
            ADD end_datetime TO PARAMETERS

        # Step 3: Execute the constructed SQL query
        WITH conn.cursor() AS CURSOR:
            CURSOR.EXECUTE(SQL_QUERY, PARAMETERS)
            RESULT_ROWS = FETCH ALL ROWS

        # Step 4: Process the results
        IF RESULT_ROWS IS EMPTY:
            RETURN None  # No datetime_ids found
        ELSE:
            RETURN A LIST OF datetime_id VALUES FROM RESULT_ROWS

    EXCEPT psycopg2.Error AS DATABASE_ERROR:
        PRINT "An error occurred while executing the database query."
        RAISE DATABASE_ERROR
    """
    pass

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

conn = connect_to_db()

df = get_timeseries_data(building_id = '5')