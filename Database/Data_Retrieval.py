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
    pass

# =============================================================================
# Data Retrieval Functions
# =============================================================================
def get_timeseries_data(conn, building_id, zone_id, variable_name, start_datetime, end_datetime):
    """
    Retrieve time-series data for a specified building, zone, and variable within a given time range.

    Args:
        conn: psycopg2 connection object
        building_id (int): ID of the building
        zone_id (int): ID of the zone
        variable_name (str): Name of the variable to retrieve
        start_datetime (str): Start datetime (YYYY-MM-DD HH:MM:SS)
        end_datetime (str): End datetime (YYYY-MM-DD HH:MM:SS)

    Returns:
        pd.DataFrame: Retrieved time-series data
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
