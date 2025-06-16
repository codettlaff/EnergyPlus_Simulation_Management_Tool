"""
Created on Mon Jun 09 10:42:28 2025

@author: Athul Jose P
"""

# Importing Required Modules
from datetime import date
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


# Layout
tab_layout = [
    dbc.Row([

        # Column 1
        dbc.Col([

            html.Br(),

            # Box 1 C1
            # Using Database?
            html.Div([
                html.Br(),

                html.Label(
                    "Are you using a database?",
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
                        {'label': " Yes", 'value': 1},
                        {'label': " No", 'value': 2}
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
                    ['Db1', 'Db2', 'Db3'],
                    '',
                    id='PSQL_Dropdown_ExistDbList',
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


# Helper Functions
def PSQL_Radiobutton_UsingDatabase_Interaction_Function(data_selection):
    if data_selection == 1:
        return False
    else:
        return True 
    
def PSQL_Radiobutton_CreateSelectDatabase_Interaction_Function(data_source):
    """
    Determines the behavior of data selection and upload controls 
    based on the selected data source radio button.

    Args:
        data_source (int): 1 for upload, 2 for selection, others for both.

    Returns:
        tuple: (data_selection, upload_data)
    """
    options = {
        1: (False, True),   # Enter Info
        2: (True, False)    # Existing Db list
    }

    # Default to (True, True) if data_source is not 1 or 2
    return options.get(data_source, (True, True))

