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
    Retrieve time-series data for specified building(s), zone(s), and variable(s) within a given time range.

    Args:
        conn: psycopg2 connection object.
        building_id (list or int or str): ID(s) of the building(s) or 'all' for all buildings.
        zone_name (list or str): Name(s) of the zone(s) or 'all' for all zones.
        variable_name (list or str): Name(s) of the variable(s) to retrieve or 'all' for all variables.
        start_datetime (datetime or str): Start datetime (YYYY-MM-DD HH:MM:SS) or 'none' for no start datetime filter.
        end_datetime (datetime or str): End datetime (YYYY-MM-DD HH:MM:SS) or 'none' for no end datetime filter.

    Returns:
        pd.DataFrame: Retrieved time-series data.

    Raises:
        MemoryError: If the size of the returned DataFrame exceeds an acceptable threshold.
        psycopg2.Error: For database-related errors.
    """
    try:
        # Initialize required IDs
        variable_ids = []
        datetime_ids = []

        # Step 1: Retrieve variable_IDs based on building_id, zone_name, variable_name
        variable_ids = get_variable_ids(conn, building_id, zone_name, variable_name)
        if not variable_ids:
            print("No matching variable IDs found.")
            return pd.DataFrame()  # Return empty DataFrame if no variables match

        # Step 2: Retrieve datetime_IDs based on start_datetime and end_datetime
        datetime_ids = get_datetime_ids(conn, start_datetime, end_datetime)
        if not datetime_ids:
            print("No matching datetime IDs found.")
            return pd.DataFrame()  # Return empty DataFrame if no datetimes match

        # Step 3: Query the timeseriesdata table using retrieved IDs
        # Construct the base query
        sql_query = """
            SELECT *
            FROM timeseriesdata
            WHERE 1=1
        """
        parameters = []

        # Add building_id filter
        if building_id != 'all':
            if isinstance(building_id, list):
                # If building_id is a list, use IN clause
                building_placeholders = ', '.join(['%s'] * len(building_id))
                sql_query += f" AND variable_id IN (SELECT variable_id FROM variables "
                sql_query += f"WHERE zone_id IN (SELECT zone_id FROM zones WHERE building_id IN ({building_placeholders})))"
                parameters.extend(building_id)
            else:
                # If building_id is a scalar, use = operator
                sql_query += f" AND variable_id IN (SELECT variable_id FROM variables "
                sql_query += f"WHERE zone_id IN (SELECT zone_id FROM zones WHERE building_id = %s))"
                parameters.append(building_id)

        # Add filter for variable_ids
        if variable_ids:
            placeholders = ', '.join(['%s'] * len(variable_ids))
            sql_query += f" AND variable_id IN ({placeholders})"
            parameters.extend(variable_ids)

        # Add filter for datetime_ids
        if datetime_ids:
            placeholders = ', '.join(['%s'] * len(datetime_ids))
            sql_query += f" AND datetime_id IN ({placeholders})"
            parameters.extend(datetime_ids)

        # Debugging: Print the query and parameters (optional)
        print(f"Executing query: {sql_query}")
        print(f"With parameters: {parameters}")

        # Execute the query and fetch the results into a pandas DataFrame
        with conn.cursor() as cursor:
            cursor.execute(sql_query, parameters)
            result_rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]  # Get column names for the DataFrame

        # Step 4: Create a DataFrame from the results
        df = pd.DataFrame(result_rows, columns=col_names)

        # Estimate memory usage of the DataFrame
        estimated_memory = df.memory_usage(deep=True).sum()
        print(f"Estimated memory usage: {estimated_memory} bytes")

        # If memory exceeds threshold, raise MemoryError
        # (You can adjust the threshold based on your application, here 1 GB is used)
        if estimated_memory > 1 * 1024 * 1024 * 1024:  # 1 GB threshold
            raise MemoryError("The DataFrame size exceeds the memory limit.")

        # Return the resulting DataFrame
        return df

    except psycopg2.Error as db_error:
        print("An error occurred while executing the database query.")
        raise db_error

    except MemoryError as mem_error:
        print("The resulting DataFrame is too large to fit in memory.")
        raise mem_error
# Passed

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
def get_building_id(conn, building_type, prototype, energy_code, climate_zone, heating_type=None, foundation_type=None):
    """
    Retrieve the building_id given specific building metadata.

    Args:
        conn: psycopg2 connection object.
        building_type (str): 'Commercial', 'Residential', or 'Manufactured'.
        prototype (str): The prototype name of the building.
        energy_code (str): The energy code of the building.
        climate_zone (str): The climate zone of the building.
        heating_type (optional, str): The heating type of the building.
        foundation_type (optional, str): The foundation type of the building.

    Returns:
        int: The building_id if found, or None if no matching record exists.

    Raises:
        psycopg2.Error: If there's an issue executing the SQL query.
    """
    try:
        # Base query
        sql_query = """
            SELECT building_id
            FROM building_prototypes
            WHERE building_type = %s
              AND prototype = %s
              AND energy_code = %s
              AND climate_zone = %s
        """
        parameters = [building_type, prototype, energy_code, climate_zone]

        # Add optional filters for heating_type and foundation_type
        if heating_type is not None:
            sql_query += " AND heating_type = %s"
            parameters.append(heating_type)

        if foundation_type is not None:
            sql_query += " AND foundation_type = %s"
            parameters.append(foundation_type)

        # Execute the query
        with conn.cursor() as cursor:
            cursor.execute(sql_query, parameters)
            result = cursor.fetchone()  # Fetch the first matching row

        # Return the building_id if found, otherwise None
        if result:
            return result[0]  # First column corresponds to building_id
        else:
            return None

    except psycopg2.Error as db_error:
        print("An error occurred while querying the database for building_id.")
        raise db_error
# Passed

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

def get_timeseries_data_test():

    conn = connect_to_db()
    building_id = 582
    zone_name = ['ATTIC', 'CORE_ZN']
    variable_name = 'Facility_Total_HVAC_Electric_Demand_Power_'
    start_datetime = datetime.strptime('2013-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.strptime('2013-01-01 01:35:00', '%Y-%m-%d %H:%M:%S')

    timeseries_data = get_timeseries_data(conn, building_id, zone_name, variable_name, start_datetime, end_datetime)
    print(timeseries_data)

def get_building_id_test():

    conn = connect_to_db()
    building_type = 'Commercial'
    prototype = 'Hospital'
    energy_code = 'ASHRAE2013'
    climate_zone = '2A'

    building_id = get_building_id(conn, building_type, prototype, energy_code, climate_zone)
    print(f"Building ID: {building_id}")

##### Main #####

#get_variable_ids_test()
#get_timeseries_data_test()
get_building_id_test()