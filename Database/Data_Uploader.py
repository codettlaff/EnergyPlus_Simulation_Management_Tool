# Created: 20250205

import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import re

def get_climate_zone(location):
    climate_zones = {
        "Miami": "1A",
        "Tampa": "2A",
        "Tucson": "2B",
        "Atlanta": "3A",
        "ElPaso": "3B",
        "SanDiego": "3C",
        "NewYork": "4A",
        "Albuquerque": "4B",
        "Seattle": "4C",
        "Buffalo": "5A",
        "Denver": "5B",
        "PortAngeles": "5C",
        "Rochester": "6A",
        "GreatFalls": "6B",
        "InternationalFalls": "7",
        "Fairbanks": "8"
    }

    return climate_zones.get(location, "Climate Zone not found.")
# Passed

def populate_datetimes_table(conn, base_time_resolution=1, start_datetime=datetime(2013, 1, 1, 0, 0)):
    """
        Populates the 'datetimes' table with timestamps at 5-minute intervals for one year.

        :param conn: psycopg2 connection object
        :param start_datetime: Start timestamp (default: January 1, 2013, 00:00)
        """
    try:
        with conn.cursor() as cursor:
            # Generate timestamps for one year at 5-minute intervals
            end_datetime = start_datetime + timedelta(days=365)
            timestamps = [start_datetime + timedelta(minutes=base_time_resolution * i) for i in range((end_datetime - start_datetime).days * 24 * 12)]

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
# Fills datetimes table with timestamps at 1-minute intervals for one year.
# Passed

def populate_buildings_table(conn):
    """
    Populates the 'building_prototypes' table with commercial, residential, and manufactured building prototypes.
    Assumes an auto-incrementing primary key for building_id.
    
    :param conn: psycopg2 connection object
    """

    # Define empty DataFrame with correct column names
    buildings_df = pd.DataFrame(columns=["building_type", "prototype", "energy_code", "idf_climate_zone", "heating_type", "foundation_type"])
    
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
    manufactured_standards = ["Final-Rule-Tier1", "Final-Rule-Tier2", "HUD-Baseline"]
    
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
# Passed

def get_building_id(conn, building_type, building_name):
    """
    Retrieves the building_id for a given building name from the database.

    :param conn: psycopg2 connection object
    :param building_type: 'Commercial', 'Residential', 'Manufactured'
    :param building_name: Formatted building name based on the type
    :return: Building ID if found, None otherwise
    """

    cursor = conn.cursor()

    # Initialize query parameters
    prototype, energy_code, climate_zone, heating_type, foundation_type = None, None, None, None, None

    if building_type == "Commercial":
        # Example Name: ASHRAE901_Hospital_STD2013_Tampa
        match = re.match(r"(ASHRAE\d{3}|IECC\d{4})_(\w+)_STD(\d{4})_([A-Za-z]+)", building_name)
        if match:
            energy_code = match.group(1).replace('901', '') + match.group(3)  # Combine standard and year
            prototype = match.group(2)
            location = match.group(4)
            climate_zone = get_climate_zone(location)

    elif building_type == "Residential":
        # Example Name: US+MF+CZ1AWH+elecres+crawlspace+IECC_2021
        match = re.match(r"US\+([A-Za-z-]+)\+CZ(\d+[A-Z]*)\+([a-z-]+)\+([a-z-]+)\+(IECC_\d{4})", building_name)
        if match:
            prototype = match.group(1).replace('MF', 'Multi-family').replace('SF', 'Single-family')
            climate_zone = match.group(2).replace('CZ', '').replace('W', '').replace('H', '')
            heating_type = match.group(3).replace('elecres', 'Electric-Resistance').replace('hp', 'Heat-Pump').replace('gasfurnace', 'Gas-Furnace').replace('oilfurnace', 'Oil-Furnace')
            foundation_type = match.group(4).replace('crawlspace', 'Crawlspace').replace('unheatedbsmt', 'Unheated-basement').replace('heatedbsmt', 'Heated-basement').replace('slab', 'Slab')
            energy_code = match.group(5).replace('_', '')

    elif building_type == "Manufactured":
        # Example Name: MS_Miami_1A_HUD_electricfurnace
        match = re.match(r"([A-Za-z]+)_([A-Za-z]+)_(\d+[A-Z]*)_(HUD|Final-Rule)_(\w+)", building_name)
        if match:
            prototype = match.group(1).replace('SS', 'Single-section').replace('MS', 'Multi-section')
            climate_zone = match.group(3)
            energy_code = match.group(4).replace('tier1', 'Final-Rule-Tier1').replace('tier2', 'Final-Rule-Tier2').replace('HUD', 'HUB-Baseline')
            heating_type = match.group(5).replace('elecres', 'Electric-Resistance').replace('hp', 'Heat-Pump').replace('gasfurnace', 'Gas-Furnace').replace('oilfurnace', 'Oil-Furnace')

    # If parsing failed, return None
    if not prototype or not energy_code or not climate_zone:
        return None

    # Construct SQL query
    query = """
        SELECT building_id FROM building_prototypes
        WHERE building_type = %s AND prototype = %s AND energy_code = %s AND idf_climate_zone = %s
    """
    params = [building_type, prototype, energy_code, climate_zone]

    if heating_type:
        query += " AND heating_type = %s"
        params.append(heating_type)
    if foundation_type:
        query += " AND foundation_type = %s"
        params.append(foundation_type)

    try:
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error retrieving building ID: {e}")
        cursor.close()
        return None
# Passed

##### Below here Populated at Runtime #####

def populate_simulations_table(conn, building_id, simulation_name='Unnamed Simulation', epw_climate_zone=None,
                               time_resolution=5):
    """
    Populate the simulations table with a new simulation record.

    :param conn: Database connection object.
    :param building_id: The ID of the building for which the simulation is being added.
    :param simulation_name: The name of the simulation (default: 'Unnamed Simulation').
    :param epw_climate_zone: The climate zone for the simulation (default: None).
    :param time_resolution: The time resolution for the simulation in minutes (default: 5).
    """
    try:
        # If epw_climate_zone is not provided, fetch it from the 'building_prototypes' table
        if epw_climate_zone is None:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT idf_climate_zone 
                    FROM building_prototypes 
                    WHERE building_id = %s
                    """,
                    (building_id,)
                )
                result = cursor.fetchone()
                if result:
                    epw_climate_zone = result[0]
                else:
                    raise ValueError(f"Climate zone not found for building_id {building_id}")

        # Insert simulation data into the simulations table
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO simulations (simulation_name, building_id, epw_climate_zone, time_resolution)
                VALUES (%s, %s, %s, %s)
                RETURNING simulation_id
                """,
                (simulation_name, building_id, epw_climate_zone, time_resolution)
            )
            # Fetch the generated simulation_id
            simulation_id = cursor.fetchone()[0]

        # Commit the transaction
        conn.commit()
        print("Simulation data successfully added to the simulations table.")

        return simulation_id

    except ValueError as ve:
        print(f"Error: {ve}")
        conn.rollback()  # Rollback in case of error

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Rollback in case of error
# Passed

def get_equipment_levels(data_dict):

    equipment_zones = [zone for zone in data_dict.keys() if "DateTime_List" not in zone and "Equipment" in zone]

    # make dataframe with columns "zone_name", "people", "lights", "electric", "gas", "hot_water", "steam" "other"
    equipment_levels = pd.DataFrame(columns=["zone_name", "people", "lights", "electric", "gas", "hot_water", "steam", "other"])

    for zone in equipment_zones:
        zone_name = zone.replace("_Equipment", "")
        people = float(data_dict[zone]["People_Level"].iloc[0]) if "People_Level" in data_dict[zone] and not data_dict[zone]["People_Level"].empty else 0.0
        lights = float(data_dict[zone]["Lights_Level"].iloc[0]) if "Lights_Level" in data_dict[zone] and not data_dict[zone]["Lights_Level"].empty else 0.0
        electric = float(data_dict[zone]["ElectricEquipment_Level"].iloc[0]) if "ElectricEquipment_Level" in data_dict[zone] and not data_dict[zone]["ElectricEquipment_Level"].empty else 0.0
        gas = float(data_dict[zone]["GasEquipment_Level"].iloc[0]) if "GasEquipment_Level" in data_dict[zone] and not data_dict[zone]["GasEquipment_Level"].empty else 0.0
        hot_water = float(data_dict[zone]["HotWaterEquipment_Level"].iloc[0]) if "HotWaterEquipment_Level" in data_dict[zone] and not data_dict[zone]["HotWaterEquipment_Level"].empty else 0.0
        steam = float(data_dict[zone]["SteamEquipment_Level"].iloc[0]) if "SteamEquipment_Level" in data_dict[zone] and not data_dict[zone]["SteamEquipment_Level"].empty else 0.0
        other = float(data_dict[zone]["OtherEquipment_Level"].iloc[0]) if "OtherEquipment_Level" in data_dict[zone] and not data_dict[zone]["OtherEquipment_Level"].empty else 0.0
        # Add a row to the DataFrame
        equipment_levels.loc[len(equipment_levels)] = [zone_name, people, lights, electric, gas, hot_water, steam, other]

    return equipment_levels
# Passed

def populate_zones_table(conn, data_dict, simulation_id):
    """
    Populates the 'zones' table with unique zone names from the provided data dictionary
    and returns a DataFrame with 'zone_id' and 'zone_name' columns for the inserted zones.

    :param conn: psycopg2 connection object
    :param data_dict: Dictionary where keys are zone names (some keys may contain metadata)
    :param simulation_id: ID to associate each record with the simulation
    :return: DataFrame with columns 'zone_id' and 'zone_name'
    """

    # Get Equipment Levels from data_dict
    equipment_levels = get_equipment_levels(data_dict)  # Assumes this returns a DataFrame with the required zone data
    # Convert the DataFrame to a list of tuples and add simulation_id as the first item
    zones_data = [(simulation_id, *row) for row in equipment_levels.itertuples(index=False, name=None)]

    try:
        with conn.cursor() as cursor:
            # Insert zones into the table and return their zone_ids
            query = """
                INSERT INTO zones (simulation_id, zone_name, equipment_level_people, equipment_level_lights, equipment_level_electric,
                                   equipment_level_gas, equipment_level_hot_water, equipment_level_steam, equipment_level_other)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING zone_id, zone_name
            """

            # Execute the query for all rows and fetch the returned zone_ids
            cursor.executemany(query, zones_data)
            conn.commit()

            # Fetch zone_id and zone_name for the inserted zones
            cursor.execute("SELECT zone_id, zone_name FROM zones WHERE simulation_id = %s", (simulation_id,))
            result = cursor.fetchall()

        # Convert to DataFrame
        df = pd.DataFrame(result, columns=["zone_id", "zone_name"])
        return df

    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f"Error inserting into zones table: {e}")
        raise  # Re-raise exception after rollback to handle it properly
# Passed

def insert_aggregation_zones(conn, data_dict, simulation_id, aggregation_zones):
    """
    Inserts aggregation zones into the zones table and creates a mapping of
    aggregation zone IDs to their corresponding composite zone IDs.
    Returns a DataFrame with columns 'zone_id' and 'zone_name' for the inserted zones.

    :param conn: psycopg2 connection object
    :param data_dict: Data dictionary containing zone information.
    :param simulation_id: ID to associate the zones with the simulation.
    :param aggregation_zones: Dictionary of aggregation zones.
                              Keys are aggregation zone names,
                              Values are lists of associated composite zone ids.
    :return: DataFrame with columns 'zone_id' and 'zone_name'
    """

    aggregation_zones_ids_dict = {}  # Initialize an empty dictionary to store results

    # Step 1: Insert aggregation zones into the zones table
    aggregated_zones_df = populate_zones_table(conn, data_dict, simulation_id)  # DataFrame with 'zone_id', 'zone_name'
    aggregation_zone_id = aggregated_zones_df.at[0, "zone_id"]

    i = 0
    for aggregation_zone, composite_zone_df in aggregation_zones.items():

        # Map the aggregation zone ID (indexed by i in aggregated_zones_df) to the composite zone IDs
        composite_zone_ids = composite_zone_df["zone_id"]
        zone_names = composite_zone_df.iloc[i]["zone_name"]
        aggregation_zones_ids_dict[aggregation_zone_id] = composite_zone_ids
        i += 1  # Increment the index to match the next aggregation zone

        # Step 2: Upload aggregation_zones_ids to the 'aggregation_zones' linking table
        # The linking table has columns 'aggregation_zone_id' and 'composite_zone_id'
    try:
        with conn.cursor() as cursor:
            # Insert query for the aggregation_zones linking table
            query = """
                INSERT INTO aggregation_zones (aggregation_zone_id, composite_zone_id)
                VALUES (%s, %s)
            """

            # Create a list of tuples for batch insertion
            linking_data = []
            for aggregation_zone_id, composite_zone_ids in aggregation_zones_ids_dict.items():
                for composite_zone_id in composite_zone_ids:
                    linking_data.append((int(aggregation_zone_id), int(composite_zone_id)))

            # Execute batch insert using executemany
            cursor.executemany(query, linking_data)

            # Commit the transaction
            conn.commit()
            print(f"Successfully inserted {len(linking_data)} records into the aggregation_zones table.")

    except Exception as e:
        # Rollback the transaction in case of an error
        conn.rollback()
        print(f"Error inserting into aggregation_zones table: {e}")
        raise  # Re-raise the exception to handle upstream

    # Return the DataFrame with 'zone_id' and 'zone_name'
    return aggregated_zones_df

def populate_variables_table(conn, data_dict, zone_ids):
    keys = list(data_dict.keys())  # Convert keys to a list
    zone_names = []
    for key in keys[1:]:
        if "Equipment" in key:
            continue
        else:
            zone_names.append(key)

    insert_zone_ids = []
    insert_variable_names = []

    i = 0
    for zone_name in zone_names:

        variable_names = data_dict[zone_name].columns.tolist()

        for variable_name in variable_names:
            insert_zone_ids.append(zone_ids[i])
            insert_variable_names.append(variable_name)
        i += 1

    records = list(zip(insert_variable_names, insert_zone_ids))

    query = """
    INSERT INTO variables (variable_name, zone_id)
    VALUES (%s, %s)
    ON CONFLICT DO NOTHING
    RETURNING variable_id, variable_name, zone_id;
    """

    with conn.cursor() as cursor:
        cursor.executemany(query, records)  # Batch insert
        conn.commit()

        # Fetch the variable_id and variable_name for the inserted/updated records
        cursor.execute("SELECT variable_id, variable_name, zone_id FROM variables ORDER BY variable_id;")
        result = cursor.fetchall()

    # Convert to DataFrame
    df = pd.DataFrame(result, columns=["variable_id", "variable_name", "zone_id"])
    return df

def get_datetime_id_list(conn, data_dict):
    """
    Retrieves a list of datetime_ids from the 'datetimes' table based on the time resolution
    given in data_dict. The 'datetimes' table is assumed to have a 5-minute resolution,
    and the time resolution is assumed to be a multiple of 5 minutes.

    Ensures the returned datetime_id list matches the length of the DateTime_List in data_dict.

    :param conn: psycopg2 connection object
    :param data_dict: Dictionary containing 'DateTime_List' with at least one timestamp
    :return: List of datetime_ids matching the specified time resolution
    """
    try:
        cursor = conn.cursor()

        # Get DateTime_List from data_dict
        datetime_list = data_dict.get("DateTime_List", [])
        if not datetime_list:
            raise ValueError("DateTime_List is missing or empty in data_dict")

        # Determine time resolution from DateTime_List
        if len(datetime_list) > 1:
            time_resolution = (datetime_list[1] - datetime_list[0]).seconds // 60  # Convert to minutes
        else:
            raise ValueError("Not enough timestamps in DateTime_List to determine resolution")

        if time_resolution % 5 != 0:
            raise ValueError("Time resolution must be a multiple of 5 minutes")

        start_datetime = datetime_list[0] - timedelta(minutes=time_resolution) # First timestamp in DateTime_List, shifted.
        end_datetime = datetime_list[-1] + timedelta(days=1) - timedelta(minutes=time_resolution) # Last timestamp in DateTime_List, shifted

        step = time_resolution // 1 # Step size for selecting datetime_ids

        # Query the database to get the datetime_id of the first timestamp
        cursor.execute("SELECT datetime_id FROM datetimes WHERE datetime = %s;", (start_datetime,))
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Start datetime {start_datetime} not found in datetimes table")

        start_datetime_id = result[0]

        # Query the database to get the datetime_id of the first timestamp
        cursor.execute("SELECT datetime_id FROM datetimes WHERE datetime = %s;", (end_datetime,))
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Start datetime {end_datetime} not found in datetimes table")

        end_datetime_id = result[0] # Returns Correct Datetime

        # Retrieve all datetime_ids within the given time range
        cursor.execute("""
            SELECT datetime_id FROM datetimes 
            WHERE datetime >= %s AND datetime <= %s 
            ORDER BY datetime_id;
        """, (start_datetime, end_datetime))
        all_datetime_ids = [row[0] for row in cursor.fetchall()]

        # Select datetime_ids based on the time resolution step
        selected_datetime_ids = all_datetime_ids[::step]

        # Ensure the selected list matches the length of datetime_list
        if len(selected_datetime_ids) != len(datetime_list): # BUG: len(datetime_list) is longer than it should be. There are 289 rows in CSV. Looks like it is duplicated.
            raise ValueError("Mismatch between expected and retrieved datetime_id list lengths")

        cursor.close()
        return selected_datetime_ids

    except Exception as e:
        print(f"Error in get_datetime_id_list: {e}")
        return []
# passed

def get_variables(conn, zone_id):
    """
    Retrieves all variable_ids and variable_names associated with a given zone_name.

    :param conn: psycopg2 connection object
    :param zone_name: Name of the zone for which variables should be fetched
    :return: List of tuples [(variable_id, variable_name), ...]
    """
    try:
        cursor = conn.cursor()

        # Step 1: Get zone_id for the given zone_name
        cursor.execute("SELECT zone_id FROM zones WHERE zone_id = %s;", (zone_id,))
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"Zone '{zone_id}' not found in zones table")

        zone_id = result[0]

        # Step 2: Get all variable_ids and variable_names where zone_id matches
        cursor.execute("SELECT variable_id, variable_name FROM variables WHERE zone_id = %s;", (zone_id,))
        variables = cursor.fetchall()

        cursor.close()
        return variables  # List of (variable_id, variable_name)

    except Exception as e:
        print(f"Error in get_variables: {e}")
        return []
# passed

def upload_time_series_data(conn, data_dict, simulation_name, building_id, epw_climate_zone=None, time_resolution=5, aggregation_zones=None):

    # Create new entry in the simulations table, returning simulation_id
    simulation_id = populate_simulations_table(conn, building_id, simulation_name, epw_climate_zone)

    # populate zones table
    if not aggregation_zones:
        zones = populate_zones_table(conn, data_dict, simulation_id)
        return zones
    else:
        zones = insert_aggregation_zones(conn, data_dict, simulation_id, aggregation_zones)

    # populate variables table
    variables = populate_variables_table(conn, data_dict, zones['zone_id'].tolist())

    # zones has columns 'zone_id', 'zone_name'
    # variables has columns 'variable_id, variable_name, zone_id'
    # combine the dataframes by adding a 'zone_name' column to variables
    variables_with_zone_name = variables.merge(zones, on='zone_id', how='left')

    # get datetime id list
    datetime_ids = get_datetime_id_list(conn, data_dict)

    # Extract zone names from data_dict, ignoring "Equipment" keys
    keys = list(data_dict.keys())
    zone_names = [key for key in keys[1:] if "Equipment" not in key]

    for zone in zone_names:

        zone_id = variables_with_zone_name[variables_with_zone_name["zone_name"] == zone]["zone_id"].tolist()[0]
        variable_names = (variables_with_zone_name[variables_with_zone_name["zone_name"] == zone])["variable_name"].tolist()

        for variable_name in variable_names:

            values = data_dict[zone][variable_name].tolist()

            # Check Values
            # Schedule Values may be empty for some zones.
            # If values are not empty, length should equal length of datetime list.
            all_nan = all(
                pd.isna(x) if not isinstance(x, (list, np.ndarray, pd.Series)) else pd.isna(x).all() for x in
                values)
            if all_nan:
                print(f"Warning: Variable '{variable_name}' data is empty for zone '{zone}'")
            elif len(datetime_ids) != len(values):
                raise ValueError(f"Mismatch in data lengths for variable '{variable_name}' in zone '{zone}'")

            variable_id = variables_with_zone_name[
                (variables_with_zone_name["variable_name"] == variable_name) &
                (variables_with_zone_name["zone_id"] == zone_id)
                ]["variable_id"].tolist()[0]

            # Do not Upload empty Values
            if not all_nan:
                # Prepare data for batch upload
                data_to_insert = [(variable_id, datetime_id, value)
                                  for datetime_id, value in zip(datetime_ids, values)]

                try:

                    cursor = conn.cursor()
                    # Insert data using executemany for efficiency
                    insert_query = """
                                INSERT INTO timeseriesdata (variable_id, datetime_id, value)
                                VALUES (%s, %s, %s);
                                """

                    cursor.executemany(insert_query, data_to_insert)
                    conn.commit()
                    conn.close()

                except Exception as e:
                    print(f"Error in populate_time_series_data_table: {e}")

# NEW TEST CODE

dbname = "buildings"
user = "Casey"
password = "OfficeLarge"
host = "localhost"

# Create the connection object
conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)

populate_datetimes_table(conn)
populate_buildings_table(conn)

test_building_name = 'ASHRAE901_OfficeSmall_STD2013_Seattle'
building_id = get_building_id(conn, 'Commercial', test_building_name)

all_zone_aggregated_pickle_filepath = r"D:\Seattle_ASHRAE_2013_2day\ASHRAE901_OfficeSmall_STD2013_Seattle\Sim_AggregatedData\Aggregation_Dict_AllZones.pickle"
with (open(all_zone_aggregated_pickle_filepath,"rb") as file):
    all_zone_data_dict = pickle.load(file)

one_zone_aggregated_pickle_filepath = r"D:\Seattle_ASHRAE_2013_2day\ASHRAE901_OfficeSmall_STD2013_Seattle\Sim_AggregatedData\Aggregation_Dict_OneZone.pickle"
with (open(one_zone_aggregated_pickle_filepath,"rb") as file):
    one_zone_data_dict = pickle.load(file)

# Upload All-Zones (un-aggregated) pickle file.
zones = upload_time_series_data(conn, all_zone_data_dict, test_building_name, building_id)

# Upload One-Zone (aggregated) pickle file.
aggregation_zones = {
    "aggregation_zone_1z": zones
}
zones = upload_time_series_data(conn, one_zone_data_dict, test_building_name, building_id, aggregation_zones=aggregation_zones)
