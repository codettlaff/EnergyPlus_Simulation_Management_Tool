
# Created: 20250203

import psycopg2

# Casey, OfficeLarge - LabPC
# casey, OfficeLarge - Laptop

def create_database():
    conn = psycopg2.connect(dbname="postgres", user="casey", password="OfficeLarge", host="localhost")
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE Buildings;")
    cursor.close()
    conn.close()
    
def get_create_table_query(tablename):
    
    # Building Information Tables
    # Each Record corresponds to a unique IDF file.
    if tablename == "building_prototypes":
        query = """
            CREATE TABLE building_prototypes (
            id SERIAL PRIMARY KEY,
            building_type VARCHAR(100) NOT NULL,
            prototype VARCHAR(100) NOT NULL,
            energy_code VARCHAR(100) NOT NULL,
            idf_climate_zone VARCHAR(100) NOT NULL,
            heating_type VARCHAR(100),
            foundation_type VARCHAR(100),
            UNIQUE (building_type, prototype, energy_code, idf_climate_zone, heating_type, foundation_type)); """

    # Simulation Information Table
    # Each record corresponds to a unique Simulation
    elif tablename == "simulations":
        query = """
        CREATE TABLE simulations (
        id SERIAL PRIMARY KEY,
        simulation_name VARCHAR(100) NOT NULL,
        building_id INT NOT NULL,
        epw_climate_zone VARCHAR(100) NOT NULL,
        time_resolution INT NOT NULL,
        FOREIGN KEY (building_id) REFERENCES building_prototypes(id),
        UNIQUE (id, simulation_name, building_id, epw_climate_zone, time_resolution)
        );
        """

    # Aggregation Zones Table
    # Links an aggregated zone to its composite zones.
    elif tablename == "aggregation_zones":
        query = """
            CREATE TABLE aggregation_zones (
            aggregation_zone_id INT NOT NULL,
            composite_zone_id INT NOT NULL,
            FOREIGN KEY (aggregation_zone_id) REFERENCES zones(id),
            FOREIGN KEY (composite_zone_id) REFERENCES zones(id),
            PRIMARY KEY (aggregation_zone_id, composite_zone_id));"""

    # Zones Table
    elif tablename == "zones":
        query = """
            CREATE TABLE zones (
            id SERIAL PRIMARY KEY,
            simulation_id INT NOT NULL,
            zone_name VARCHAR(100) NOT NULL,
            equipment_level_people FLOAT,
            equipment_level_lights FLOAT,
            equipment_level_electric FLOAT,
            equipment_level_gas FLOAT,
            equipment_level_hot_water FLOAT,
            equipment_level_steam FLOAT,
            equipment_level_other FLOAT,
            FOREIGN KEY (simulation_id) REFERENCES simulations(id),
            UNIQUE (simulation_id, zone_name));"""

    # Variables Table
    elif tablename == "variables":
        query = """
            CREATE TABLE variables (
            id SERIAL PRIMARY KEY,
            variable_name VARCHAR(100) NOT NULL,
            zone_id INT NOT NULL,
            FOREIGN KEY (zone_id) REFERENCES zones(id),
            UNIQUE (variable_name, zone_id));"""
        
    # Time Series Data Tables
    
    elif tablename == "datetimes":
        query = """
        CREATE TABLE datetimes (
        id SERIAL PRIMARY KEY,
        datetime TIMESTAMP UNIQUE NOT NULL);"""
        
    elif tablename == "timeseriesdata":
        query = """
        CREATE TABLE timeseriesdata (
        variable_id INT NOT NULL,
        datetime_id INT NOT NULL,
        value FLOAT NOT NULL,
        FOREIGN KEY (variable_id) REFERENCES variables(id),
        FOREIGN KEY (datetime_id) REFERENCES datetimes(id),
        PRIMARY KEY (variable_id, datetime_id));"""
    
    # Return Query
    
    return query

def create_table(query):
    conn = psycopg2.connect(dbname="buildings", user="casey", password="OfficeLarge", host="localhost")
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    
def create_tables():
    
    # tables must be created in the following order
    tables = ["building_prototypes",
              "simulations",
              "datetimes",
              "zones",
              "variables",
              "aggregation_zones",
              "timeseriesdata"]
    
    for table in tables:
        try:
            query = get_create_table_query(table)
            create_table(query)
            print(f"Table '{table}' created successfully.\n")
        except Exception as e:
            print(f"Error creating table '{table}': {e}\n")
            
def delete_all_tables(dbname="buildings", user="Casey", password="OfficeLarge", host="localhost"):
    
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    cursor = conn.cursor()

    # Fetch all table names
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public';
    """)
    tables = cursor.fetchall()

    # Drop each table
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        print(f"Deleted table: {table_name}")

    conn.commit()
    cursor.close()
    conn.close()
                  
#Main
# create_database()
#delete_all_tables()
# create_tables()
