
# Created: 20250203

import psycopg2

def create_database():
    conn = psycopg2.connect(dbname="postgres", user="Casey", password="OfficeLarge", host="localhost")
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE Buildings;")
    cursor.close()
    conn.close()
    
def get_create_table_query(tablename):
    
    # Building And Simulation Information Tables
            
    if tablename == "building_prototypes":
        query = """
            CREATE TABLE building_prototypes (
            building_id SERIAL PRIMARY KEY,
            building_type VARCHAR(100) NOT NULL,
            prototype VARCHAR(100) NOT NULL,
            energy_code VARCHAR(100) NOT NULL,
            climate_zone VARCHAR(100) NOT NULL,
            heating_type VARCHAR(100),
            foundation_type VARCHAR(100)); """
        
    # Variable Information Tables
        
    elif tablename == "aggregation_zones":
        query = """
            CREATE TABLE aggregation_zones (
            aggregation_zone_id INT NOT NULL,
            composite_zone_id INT NOT NULL,
            FOREIGN KEY (aggregation_zone_id) REFERENCES zones(zone_id),
            FOREIGN KEY (composite_zone_id) REFERENCES zones(zone_id),
            PRIMARY KEY (aggregation_zone_id, composite_zone_id));"""
        
    elif tablename == "zones":
        query = """
            CREATE TABLE zones (
            zone_id SERIAL PRIMARY KEY,
            building_id INT NOT NULL,
            zone_name VARCHAR(100) UNIQUE NOT NULL,
            FOREIGN KEY (building_id) REFERENCES building_prototypes(building_id));"""
        
    elif tablename == "variables":
        query = """
            CREATE TABLE variables (
            variable_id SERIAL PRIMARY KEY,
            variable_name VARCHAR(100) NOT NULL,
            zone_id INT NOT NULL,
            FOREIGN KEY (zone_id) REFERENCES zones(zone_id));"""
        
    # Time Series Data Tables
    
    elif tablename == "datetimes":
        query = """
        CREATE TABLE datetimes (
        datetime_id SERIAL PRIMARY KEY,
        datetime TIMESTAMP NOT NULL);"""
        
    elif tablename == "timeseriesdata":
        query = """
        CREATE TABLE timeseriesdata (
        variable_id INT NOT NULL,
        datetime_id INT NOT NULL,
        value FLOAT NOT NULL,
        FOREIGN KEY (variable_id) REFERENCES variables(variable_id),
        FOREIGN KEY (datetime_id) REFERENCES datetimes(datetime_id),
        PRIMARY KEY (variable_id, datetime_id));"""
    
    # Return Query
    
    return query

def create_table(query):
    conn = psycopg2.connect(dbname="buildings", user="Casey", password="OfficeLarge", host="localhost")
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    
def create_tables():
    
    # tables must be created in the following order
    tables = ["building_prototypes", 
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
#create_database()        
create_tables()
#delete_all_tables()