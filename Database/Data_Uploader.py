# Created: 20250205

import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle

def populate_datetimes_table(conn, start_datetime=datetime(2013, 1, 1, 0, 0)):
    """
        Populates the 'datetimes' table with timestamps at 5-minute intervals for one year.

        :param conn: psycopg2 connection object
        :param start_datetime: Start timestamp (default: January 1, 2013, 00:00)
        """
    try:
        with conn.cursor() as cursor:
            # Generate timestamps for one year at 5-minute intervals
            end_datetime = start_datetime + timedelta(days=365)
            timestamps = [start_datetime + timedelta(minutes=5 * i) for i in range((end_datetime - start_datetime).days * 24 * 12)]

            # Convert list into a format suitable for insertion
            records = [(ts,) for ts in timestamps]

            # Insert timestamps into the datetimes table
            query = """
            INSERT INTO datetimes (datetime)
            VALUES (%s)
            ON CONFLICT DO NOTHING;
            """
            
            cursor.executemany(query, records)
            conn.commit()
            print(f"Successfully inserted {len(records)} timestamps into datetimes table.")

    except Exception as e:
        conn.rollback()
        print(f"Error inserting into datetimes table: {e}")
# Fills datetimes table with timestamps at 5-minute intervals for one year.

def populate_buildings_table(conn):
    """
    Populates the 'building_prototypes' table with commercial, residential, and manufactured building prototypes.
    Assumes an auto-incrementing primary key for building_id.
    
    :param conn: psycopg2 connection object
    """

    # Define empty DataFrame with correct column names
    buildings_df = pd.DataFrame(columns=["building_type", "prototype", "energy_code", "climate_zone", "heating_type", "foundation_type"])
    
    # Define climate zones
    climate_zones = ["0A", "0B", "1A", "1B", "2A", "2B", "3A", "3B", "3C", "4A", "4B", "4C", "5A", "5B", "5C", "6A", "6B", "7", "8"]
    
    # Commercial Buildings
    commercial_prototypes = [
        "Hospital", "HotelLarge", "HotelSmall", "OfficeLarge", "OfficeMedium", "OfficeSmall",
        "OutPatientHealthCare", "RestaurantFastFood", "RestaurantSitDown", "RetailStandAlone",
        "RetailStripMall", "SchoolPrimary", "SchoolSecondary", "Warehouse"
    ]
    
    commercial_standards = ["ASHRAE2013", "ASHRAE2016", "ASHRAE2019", "IECC2012", "IECC2015", "IECC2018"]
    
    commercial_data = [
        ["Commercial", prototype, standard, climate_zone, None, None]
        for prototype in commercial_prototypes
        for standard in commercial_standards
        for climate_zone in climate_zones
    ]
    
    # Residential Buildings
    residential_prototypes = ["Multi-family", "Single-Family"]
    heating_types = ["Electric-Resistance", "Gas-Furnace", "Oil-Furnace", "Heat-Pump"]
    foundation_types = ["Slab", "Crawlspace", "Heated-basement", "Unheated-basement"]
    residential_standards = ["IECC2021", "IECC2018", "IECC2015"]
    
    residential_data = [
        ["Residential", prototype, standard, climate_zone, heating_type, foundation_type]
        for prototype in residential_prototypes
        for heating_type in heating_types
        for foundation_type in foundation_types
        for standard in residential_standards
        for climate_zone in climate_zones
    ]
    
    # Manufactured Homes
    configurations = ["Single-section", "Multi-section"]
    heating_system_types = ["Electric-Resistance", "Gas-Furnace", "Oil-Furnace", "Heat-Pump"]
    manufactured_standards = ["Final-Rule", "HUD-Baseline"]
    
    manufactured_data = [
        ["Manufactured", configuration, standard, climate_zone, heating_type, None]
        for configuration in configurations
        for heating_type in heating_system_types
        for standard in manufactured_standards
        for climate_zone in climate_zones
    ]

    # Combine all data
    all_building_data = commercial_data + residential_data + manufactured_data
    
    # Convert to DataFrame
    buildings_df = pd.DataFrame(all_building_data, columns=buildings_df.columns)

    try:
        with conn.cursor() as cursor:
            # Generate SQL query dynamically based on DataFrame columns
            columns = ", ".join(buildings_df.columns)
            values_placeholder = ", ".join(["%s"] * len(buildings_df.columns))

            query = f"""
            INSERT INTO building_prototypes ({columns})
            VALUES ({values_placeholder})
            ON CONFLICT DO NOTHING;
            """

            # Convert DataFrame to list of tuples for batch insert
            data_tuples = [tuple(row) for row in buildings_df.to_numpy()]

            # Execute batch insert
            cursor.executemany(query, data_tuples)
            conn.commit()
            print(f"Successfully inserted {len(buildings_df)} records into building_prototypes.")

    except Exception as e:
        conn.rollback()
        print(f"Error inserting into building_prototypes: {e}")
# Creates a record for each prototypical building IDF provided by PNNL.
# Uploads this dataframe to Database.
# This Function only needs to be run once.     

def get_building_id(conn, building_name):
    """
    Retrieves the building_id for a given building name from the database.

    :param conn: psycopg2 connection object
    :param building_name: Name of the building to look up
    :return: Building ID if found, None otherwise
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT building_id FROM building_prototypes WHERE prototype = %s;", (building_name,))
            result = cursor.fetchone()
            return result[0] if result else None

    except Exception as e:
        print(f"Error retrieving building_id for '{building_name}': {e}")
        return None
# Returns Building ID

def populate_zones_table(conn, data_dict, building_id):
    """
    Populates the 'zones' table with unique zone names from the provided data dictionary.
    
    :param conn: psycopg2 connection object
    :param data_dict: Dictionary where keys are zone names (some keys may contain metadata)
    """
    
    zones = [zone for zone in data_dict.keys() if "DateTime_List" not in zone and "Equipment" not in zone]
    
    try:
        with conn.cursor() as cursor:

            # Convert to DataFrame
            zones_df = pd.DataFrame(zones, columns=["zone_name"])

            # Prepare data for batch insertion
            records = [(zone,) for zone in zones_df["zone_name"].unique()]

            # Insert zones into the table with conflict handling
            query = """
            INSERT INTO zones (zone_name)
            VALUES (%s)
            ON CONFLICT (zone_name) DO NOTHING;
            """
            
            cursor.executemany(query, records)
            conn.commit()
            print(f"Successfully inserted {len(records)} unique zones into the zones table.")

    except Exception as e:
        conn.rollback()
        print(f"Error inserting into zones table: {e}")
# Creates a record for each zone in the data dictionary.
# Uploads tot eh zones database    
# Use for All-Zones Aggregation Only     

def populate_aggregation_zones_table(conn, data_dict, building_id):
    
    zones = [zone for zone in data_dict.keys() if "DateTime_List" not in zone and "Equipment" not in zone]
    
    one_zone_aggregation_zone_name = building_name + "SingleZone"
    
    try:
        with conn.cursor() as cur:
            # Insert the one_zone_aggregation_zone_name into the zones table if it doesn't exist
            cur.execute("""
                INSERT INTO zones (zone_name) 
                VALUES (%s) 
                ON CONFLICT (zone_name) DO NOTHING 
                RETURNING zone_id;
            """, (one_zone_aggregation_zone_name,))
            
            one_zone_aggregation_zone_id = cur.fetchone()
            
            # If zone already exists, fetch its zone_id
            if one_zone_aggregation_zone_id is None:
                cur.execute("SELECT zone_id FROM zones WHERE zone_name = %s;", (one_zone_aggregation_zone_name,))
                one_zone_aggregation_zone_id = cur.fetchone()[0]
            else:
                one_zone_aggregation_zone_id = one_zone_aggregation_zone_id[0]

            # Fetch zone IDs for all extracted zones
            cur.execute("SELECT zone_id, zone_name FROM zones WHERE zone_name = ANY(%s);", (zones,))
            zone_id_map = {name: zone_id for zone_id, name in cur.fetchall()}

            # Insert aggregation zone mappings
            records = [
                (zone_id, one_zone_aggregation_zone_id)
                for zone_name, zone_id in zone_id_map.items()
            ]

            if records:
                cur.executemany("""
                    INSERT INTO aggregation_zones (composite_zone_id, aggregation_zone_id) 
                    VALUES (%s, %s) 
                    ON CONFLICT DO NOTHING;
                """, records)

            conn.commit()
            print(f"Successfully populated aggregation_zones for building: {building_name}")

    except Exception as e:
        conn.rollback()
        print(f"Error populating aggregation_zones: {e}")
# Fills the Aggregation Zones Linking Table
# Each record has FK Composite Zone and FK Aggregation Zone  
# Use for Single-Zone Aggregation Only       
    


        

 