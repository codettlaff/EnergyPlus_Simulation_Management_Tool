"""
Created on Mon Jun 09 10:42:28 2025

@author: Athul Jose P
"""

# Importing Required Modules
import math
import os
import sys
import pandas as pd
import psycopg2
from datetime import date
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

database_creator_script_dir = os.path.join(os.path.dirname(__file__), '..', 'Database_v2')
sys.path.append(database_creator_script_dir)
import Database_Creator as db_creator
import Data_Uploader as db_uploader

DATABASES_CSV_FILEPATH = os.path.join(os.path.dirname(__file__), 'databases.csv')
def databases_csv_filepath(): return DATABASES_CSV_FILEPATH

# Layout
tab_layout = [
    dbc.Row([

        # Column 1
        dbc.Col([

            html.Br(),

            # Box 1 C1
            # Using Database?
            html.Div([
                html.Label("Database Selection", style={
                    'font-weight': 'bold',
                    'font-size': '1.2rem',
                    'margin-bottom': '10px',
                    'display': 'block'
                }),

                html.Label(
                    "Use Database:",
                    style={
                        'margin': '1.5% 0 1% 3%',
                        'font-weight': '600',
                        'font-size': '1.1rem'
                    }
                ),

                dcc.RadioItems(
                    id='PSQL_RadioButton_UsingDatabase',
                    labelStyle={'display': 'block'},
                    options=[
                        {'label': " Yes", 'value': True},
                        {'label': " No", 'value': False}
                    ],
                    value='',
                    style={
                        'margin-left': '3%',
                        'margin-bottom': '2%'
                    }
                ),
            ],
            id='PSQL_Div_UsingDatabase',
            # hidden=True,
            style={
                'borderWidth': '1px',
                'borderStyle': 'solid',
                'borderRadius': '5px',
                'padding': '2%'
            }),

            

            html.Br(),

            # Box 2 C1
            # Create/Select Database?
            html.Div([
                dcc.RadioItems(
                id = 'PSQL_RadioButton_CreateSelectDatabase',
                labelStyle = {'display': 'block'},
                options = [
                    {'label' : " Create Database", 'value' : 1},
                    {'label' : " Select Database", 'value' : 2}
                    ]  ,
                value = '',
                className = 'ps-4 p-3',
                ),
            ],id = 'PSQL_Div_CreateSelectDatabase',
            hidden = True,
            style = {
                'borderWidth': '1px',
                'borderStyle': 'solid',
                'borderRadius': '5px',
                },),

            html.Br(),

            ], xs = 12, sm = 12, md = 6, lg = 6, xl = 6), # width = 12

        # Column 2
        dbc.Col([
            html.Br(),

            # Box 1 C2 — Enter Information
            html.Div([
                html.H6("Enter Information", 
                    # className='text-left ms-4 mt-1',
                    style={
                        'margin': '1.5% 0 1% 3%',  # top, right, bottom, left
                        'font-weight': '600',
                        'font-size': '1.1rem'
                    }
                ),

                dbc.Stack([
                    # Username
                    dbc.Stack([
                        html.Label(
                            "Username:",
                            style={
                                'width': '30%',
                                'margin-top': 'auto',
                                'margin-bottom': 'auto'
                            }
                        ),
                        dcc.Textarea(
                            id='PSQL_Textarea_Username',
                            value='',
                            style={
                                'width': '70%',
                                'height': 50
                            }
                        ),
                    ], direction="horizontal", style={
                        'align-items': 'center',
                        'margin': '2%'
                    }),

                    # Password
                    dbc.Stack([
                        html.Label(
                            "Password:",
                            style={
                                'width': '30%',
                                'margin-top': 'auto',
                                'margin-bottom': 'auto'
                            }
                        ),
                        dcc.Textarea(
                            id='PSQL_Textarea_Password',
                            value='',
                            style={
                                'width': '70%',
                                'height': 50
                            }
                        ),
                    ], direction="horizontal", style={
                        'align-items': 'center',
                        'margin': '2%'
                    }),

                    # Port Number
                    dbc.Stack([
                        html.Label(
                            "Port Number:",
                            style={
                                'width': '30%',
                                'margin-top': 'auto',
                                'margin-bottom': 'auto'
                            }
                        ),
                        dcc.Textarea(
                            id='PSQL_Textarea_PortNumber',
                            value='',
                            style={
                                'width': '70%',
                                'height': 50
                            }
                        ),
                    ], direction="horizontal", style={
                        'align-items': 'center',
                        'margin': '2%'
                    }),

                    # Host Name
                    dbc.Stack([
                        html.Label(
                            "Host Name:",
                            style={
                                'width': '30%',
                                'margin-top': 'auto',
                                'margin-bottom': 'auto'
                            }
                        ),
                        dcc.Textarea(
                            id='PSQL_Textarea_HostName',
                            value='',
                            style={
                                'width': '70%',
                                'height': 50
                            }
                        ),
                    ], direction="horizontal", style={
                        'align-items': 'center',
                        'margin': '2%'
                    }),

                    # Database Name
                    dbc.Stack([
                        html.Label(
                            "Name of Database:",
                            style={
                                'width': '30%',
                                'margin-top': 'auto',
                                'margin-bottom': 'auto'
                            }
                        ),
                        dcc.Textarea(
                            id='PSQL_Textarea_DbName',
                            value='',
                            style={
                                'width': '70%',
                                'height': 50
                            }
                        ),
                    ], direction="horizontal", style={
                        'align-items': 'center',
                        'margin': '2%'
                    }),
                ]),

                html.Button(
                    'Create Database',
                    id='PSQL_Button_CreateDatabase',
                    className="btn btn-primary btn-lg",
                    style={
                        'width': '94%',
                        'margin': '2% 3% 3% 3%',  # top, right, bottom, left
                        'padding': '10px'
                    }
                ),
            ],
            id='PSQL_Div_EnterInfo',
            hidden=True,
            style={
                'borderWidth': '1px',
                'borderStyle': 'solid',
                'borderRadius': '5px',
                'padding': '2%',
                'padding-bottom': '1%' 
            }),

            html.Br(),

            # Box 2 C2 — Select Existing Database
            html.Div([
                html.Label(
                    "Select Database from List",
                    style={
                        'margin': '1.5% 0 1% 3%',
                        'font-weight': '600',
                        'font-size': '1.1rem'
                    }
                ),
                dcc.Dropdown(
                    options=[],
                    placeholder="Select...",
                    id='PSQL_Dropdown_ExistDbList',
                    value=None,
                    style={
                        'width': '94%',
                        'margin': '0 3% 2% 3%'  # top, right, bottom, left
                    }
                ),
            ], 
            id='PSQL_Div_SelectDbfromExist',
            hidden=True,
            style={
                'borderWidth': '1px',
                'borderStyle': 'solid',
                'borderRadius': '5px',
                'padding-bottom': '1%',
            })

        ]),

        
        html.Button('End Session',
            id = 'PSQL_Button_EndSession',
            className = "btn btn-primary btn-lg col-12",
            style = {
                'width':'98%',
                },),

        ], justify = "center", align = "center"),

]


# Casey's Code

def connect(db_settings):
    if 'port' in db_settings:
        if not (isinstance(db_settings['port'], int) and db_settings['port'] > 0): db_settings.pop('port')
    if 'host' in db_settings:
        if db_settings['host'] is None: db_settings.pop('host')
    return psycopg2.connect(**db_settings)

def create_database(db_settings):

    dbname = db_settings['dbname']
    db_settings['dbname'] = 'postgres'
    try:
        conn = connect(db_settings)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE {dbname};")
        conn.close()
    except psycopg2.Error as e:
        if e.pgcode == '42P04': return "Database Already Created" # Duplicate Database
        else: return "Invalid Information"

    # Try Connecting to Newly Created Database
    db_settings['dbname'] = dbname
    try:
        conn = connect(db_settings)
        conn.close()
    except psycopg2.Error as e:
        return "Invalid Information"

    # Create Empty Tables, Populate Prototypical Buildings Table
    try:
        conn = connect(db_settings)
        db_creator.create_database(conn)
        db_creator.create_tables(conn)
        db_uploader.populate_buildings_table(conn)
    except psycopg2.Error as e:
        print("Failed to Create Tables: ", e)
        return "Failed to Create Database"

    if not os.path.isfile(DATABASES_CSV_FILEPATH):
        pd.DataFrame(columns=["dbname", "user", "password", "host", "port"]).to_csv(DATABASES_CSV_FILEPATH, index=False)

    df = pd.read_csv(DATABASES_CSV_FILEPATH)
    df = pd.concat([df, pd.DataFrame([db_settings])], ignore_index=True)
    df.to_csv(DATABASES_CSV_FILEPATH, index=False)

    return 'Database Created'

def get_db_names():
    df = pd.read_csv(DATABASES_CSV_FILEPATH)
    dbnames = df["dbname"].dropna().unique().tolist()
    return [{"label": name, "value": name} for name in dbnames]

def get_db_settings(dbname):
    df = pd.read_csv(DATABASES_CSV_FILEPATH)
    record = df[df["dbname"] == dbname].iloc[0]
    record_dict = record.to_dict()
    return record_dict

"""

def populate_existing_db_dropdown(selection):
    # Only update the dropdown if "Select Database" was chosen (value = 2)
    if selection != 2:
        return []

    # Load database names from CSV
    if not os.path.isfile(DATABASES_CSV_FILEPATH):
        return []

    df = pd.read_csv(DATABASES_CSV_FILEPATH)
    if "database_name" not in df.columns:
        return []
    dbnames = df["database_name"].dropna().unique().tolist()
    return [{"label": name, "value": name} for name in dbnames]

def get_conn_from_dbname(database_name):

    db_settings = None
    try:
        df = pd.read_csv(DATABASES_CSV_FILEPATH)
        record = df[df["database_name"] == database_name].iloc[0]

        if record["port"] == "localhost":
            conn = psycopg2.connect(
                dbname=record["database_name"],
                user=record["username"],
                password=record["password"],
                host="localhost"
            )
            db_settings = {
                "dbname": record["database_name"],
                "user": record["username"],
                "password": record["password"],
                "host": "localhost"
            }
        else:
            conn = psycopg2.connect(
                dbname=record["database_name"],
                user=record["username"],
                password=record["password"],
                port=record["port"]
            )
            db_settings = {
                "dbname": record["database_name"],
                "user": record["username"],
                "password": record["password"],
                "post": record["port"]
            }

        conn.close()

        print(f"Connected to {database_name}")
        return db_settings
    except Exception as e:
        print(f"Could not 

"""