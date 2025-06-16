"""
Created on Tue Jan 30 15:32:25 2024

@author: Athul Jose P
Latest update is in Buildings_app_modularized.py
"""

# Importing Required Modules
import shutil
import os
import re
import datetime
import pickle
import copy
from datetime import date
from dash import Dash, dcc, html, Input, Output, State, dash_table
import pandas as pd
import numpy as np
import opyplus as op
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Importing User-Defined Modules
import MyDashApp_Module as AppFuncs

UPLOAD_DIRECTORY = os.path.join(os.getcwd(), "EP_APP_Uploads")
UPLOAD_DIRECTORY_AGG_PICKLE = os.path.join(UPLOAD_DIRECTORY, "Pickle_Upload")
UPLOAD_DIRECTORY_AGG_EIO = os.path.join(UPLOAD_DIRECTORY, "EIO_Upload")
UPLOAD_DIRECTORY_VIS = os.path.join(UPLOAD_DIRECTORY, "Visualization")
WORKSPACE_DIRECTORY = os.path.join(os.getcwd(), "EP_APP_Workspace")
SIMULATION_FOLDERPATH = 'abc123'
SIMULATION_FOLDERNAME = 'abc123'
DATA_DIRECTORY =  os.path.join(os.getcwd(), "..", "..", "Data")

OUR_VARIABLE_LIST = ['Schedule_Value_',
                        'Facility_Total_HVAC_Electric_Demand_Power_',
                        'Site_Diffuse_Solar_Radiation_Rate_per_Area_',
                        'Site_Direct_Solar_Radiation_Rate_per_Area_',
                        'Site_Outdoor_Air_Drybulb_Temperature_',
                        'Site_Solar_Altitude_Angle_',
                        'Surface_Inside_Face_Internal_Gains_Radiation_Heat_Gain_Rate_',
                        'Surface_Inside_Face_Lights_Radiation_Heat_Gain_Rate_',
                        'Surface_Inside_Face_Solar_Radiation_Heat_Gain_Rate_',
                        'Surface_Inside_Face_Temperature_',
                        'Zone_Windows_Total_Transmitted_Solar_Radiation_Rate_',
                        'Zone_Air_Temperature_',
                        'Zone_People_Convective_Heating_Rate_',
                        'Zone_Lights_Convective_Heating_Rate_',
                        'Zone_Electric_Equipment_Convective_Heating_Rate_',
                        'Zone_Gas_Equipment_Convective_Heating_Rate_',
                        'Zone_Other_Equipment_Convective_Heating_Rate_',
                        'Zone_Hot_Water_Equipment_Convective_Heating_Rate_',
                        'Zone_Steam_Equipment_Convective_Heating_Rate_',
                        'Zone_People_Radiant_Heating_Rate_',
                        'Zone_Lights_Radiant_Heating_Rate_',
                        'Zone_Electric_Equipment_Radiant_Heating_Rate_',
                        'Zone_Gas_Equipment_Radiant_Heating_Rate_',
                        'Zone_Other_Equipment_Radiant_Heating_Rate_',
                        'Zone_Hot_Water_Equipment_Radiant_Heating_Rate_',
                        'Zone_Steam_Equipment_Radiant_Heating_Rate_',
                        'Zone_Lights_Visible_Radiation_Heating_Rate_',
                        'Zone_Total_Internal_Convective_Heating_Rate_',
                        'Zone_Total_Internal_Radiant_Heating_Rate_',
                        'Zone_Total_Internal_Total_Heating_Rate_',
                        'Zone_Total_Internal_Visible_Radiation_Heating_Rate_',
                        'Zone_Air_System_Sensible_Cooling_Rate_',
                        'Zone_Air_System_Sensible_Heating_Rate_',
                        'System_Node_Temperature_',
                        'System_Node_Mass_Flow_Rate_']


# Instantiate our App and incorporate BOOTSTRAP theme Stylesheet
# Themes - https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/#available-themes
# Themes - https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/
# hackerthemes.com/bootstrap-cheatsheet/

app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])

# App Layout using Dash Bootstrap

app.layout = dbc.Container([

    dbc.Row([
        html.H1("EnergyPlus Simulation Management Tool", className = 'text-center text-primary mb-4')
    ]),

    dcc.Tabs([

#################################################################################################

# # # # # #  EP Generation Tab # # # # # # # # #

#################################################################################################

        # EP Generation Tab
        dcc.Tab(label='EP Generation', className = 'text-center text-primary mb-4', children=[

            # Row 1
            dbc.Row([

                # Column 1
                dbc.Col([

                    html.Br(),

                    # Box 11 C1
                    html.Div([
                        dcc.Input(
                            id='folder_name',
                            type='text',
                            value='',
                            placeholder='Enter simulation name',
                            className="center-placeholder center-input",
                            style={
                                'width':'100%',
                                'height':'50px',
                                'margin':'0%',
                                'text-align': 'center',
                                'font-size': '24px'
                                },),

                        ],id = 'create_directory',
                        style = {
                            # 'borderWidth': '1px',
                            # 'borderStyle': 'solid',
                            # 'borderRadius': '5px',
                            },),

                    html.Br(),

                    # Box 1 C1
                    # Database selection
                    dcc.RadioItems(
                        id = 'database_selection',
                        labelStyle = {'display': 'block'},
                        value = '1',
                        options = [
                            {'label' : " Our Database", 'value' : 1},
                            {'label' : " Your Files", 'value' : 2}
                            ]  ,
                        className = 'ps-4 p-3',
                        style = {
                            'width': '100%',
                            'borderWidth': '1px',
                            'borderStyle': 'solid',
                            'borderRadius': '5px',
                            }
                        ),

                    html.Br(),

                    # Box 2 C1
                    html.Div([

                        # Upload IDF file
                        dcc.Upload(['Upload IDF file'],
                            id = 'upload_idf',
                            className = 'center',
                            style = {
                                'width': '90%',
                                'height': '40px',
                                'lineHeight': '40px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin-left': '5%',
                                'margin-top': '5%'
                                }),

                        # Upload EPW file
                        dcc.Upload(['Upload EPW file'],
                            id = 'upload_epw',
                            className = 'center',
                            style = {
                                'width': '90%',
                                'height': '40px',
                                'lineHeight': '40px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '5%',
                                }),

                        # Version selection
                        dbc.Stack([
                            html.Label("Energy Plus Version:",
                                className = 'text'),
                            dcc.Dropdown(['8.0.0','9.0.0','22.0.0','23.0.0'], '',
                                id='version_selection',
                                style = {
                                    'width':'60%',
                                    'margin-left':'8%'
                                }),
                            ],direction="horizontal",
                            style = {
                                'width': '90%',
                                'margin': '5%',
                                }),

                        ],id = 'upload_files',
                        hidden = True,
                        style = {
                            'borderWidth': '1px',
                            'borderStyle': 'solid',
                            'borderRadius': '5px',
                            }),

                    html.Br(),

                    # Box 3 C1
                    html.Div([

                        # Time-step selection
                        dbc.Stack([
                            html.Label("Time Step:",
                                className = 'text'),
                            daq.NumericInput(
                                id='sim_TimeStep',
                                value=5,
                                style={'margin-left':'28%'}
                            ),
                            ],direction = "horizontal",
                            style = {'margin': '5%'}
                        ),

                        # Simulation run period
                        html.Label("Simulation Run Period:",
                                className = 'text', style={'margin-left': '5%'}),
                        dcc.DatePickerRange(
                            id='sim_run_period',
                            min_date_allowed=date(2000, 1, 1),
                            max_date_allowed=date(2021, 12, 31),
                            #initial_visible_month=date(2020, 1, 1),
                            start_date=date(2020, 1, 1),
                            end_date=date(2020, 12, 31),
                            display_format='M/D',
                            style = {
                                'width': '100%',
                                'margin': '5%',
                                'display': 'block'
                                },
                        ),
                        # html.Div(id='sim-run-period2'),


                        # Simulation reporting frequency selection
                        dbc.Stack([
                            html.Label("Simulation Reporting Frequency:",
                                className = 'text'),
                            dcc.Dropdown(['timestep','hourly','detailed','daily','monthly','runperiod','environment','annual'],
                                '',
                                id = 'simReportFreq_selection',
                                style = {
                                    'width':'70%',
                                    'margin':'2%'
                                    }),
                            ],direction = "horizontal",
                            style = {
                                'margin': '5%',
                                }),

                        ],id = 'simulation_details',
                        hidden = True,
                        style = {
                            'borderWidth': '1px',
                            'borderStyle': 'solid',
                            'borderRadius': '5px',
                            },),

                    html.Br(),

                    ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4), # width = 12

                # Column 2
                dbc.Col([

                    # Box 2 C2
                    html.Div([
                        html.Button('Generate Variables',
                            id = 'EPGen_Button_GenerateVariables',
                            className = "btn btn-secondary btn-lg col-12",
                            n_clicks = 0,
                            style = {
                                'width':'90%',
                                'margin':'5%'
                                },),

                        html.Label("Select Custom Variables",
                            className = 'text-left ms-4'),
                        dcc.Dropdown(options = [],
                            value = '',
                            id = 'your_variable_selection',
                            multi = True,
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        html.Label("Preselected variables",
                            className = 'text-left ms-4 mt-0'),
                        dcc.Dropdown(options = [],
                            value = '',
                            id = 'our_variable_selection',
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        dcc.RadioItems(
                            id = 'EPGen_Radiobutton_VariableSelection',
                            labelStyle = {'display': 'block'},
                            value = '',
                            options = [
                                {'label' : " Preselected Variables", 'value' : 1},
                                {'label' : " Custom Variable Selection", 'value' : 2}
                                ]  ,
                            className = 'ps-4 p-3',
                            style = {
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }
                            ),

                        dcc.RadioItems(
                            id = 'EPGen_Radiobutton_EditSchedules',
                            labelStyle = {'display': 'block'},
                            value = '',
                            options = [
                                {'label' : " Edit Schedules", 'value' : 1},
                                {'label' : " Keep Original Schedules", 'value' : 2}
                                ]  ,
                            className = 'ps-4 p-3',
                            style = {
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }
                            ),

                            ],id = 'generate_variables',
                            hidden = True,
                            style = {
                                'borderWidth': '1px',
                                'borderStyle': 'solid',
                                'borderRadius': '5px',
                            },),

                    html.Br(),

                    # Box 1 C2
                    html.Div([
                        html.H3("Edit Schedules",
                            className = 'text-center mt-1'),
                        html.H6("People",
                            className = 'ms-4'),
                        dcc.Dropdown(options = [],
                            value = '',
                            id = 'people_schedules',
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        html.H6("Equipment",
                            className = 'ms-4'),
                        dcc.Dropdown(options = [],
                            value = '',
                            id = 'equip_schedules',
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        html.H6("Light",
                            className = 'ms-4'),
                        dcc.Dropdown(options = [],
                            value = '',
                            id = 'light_schedules',
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        html.H6("Heating",
                            className = 'ms-4'),
                        dcc.Dropdown(options = [],
                            value = '',
                            id = 'heating_schedules',
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        html.H6("Cooling",
                            className = 'ms-4'),
                        dcc.Dropdown(options = [],
                            value = '',
                            id = 'cooling_schedules',
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        html.H6("Temperature",
                            className = 'ms-4'),
                        dcc.Dropdown(options = [],
                            value = '',
                            id = 'temperature_schedules',
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        html.H6("Paste your custom schedule",
                            className = 'ms-4'),
                        dcc.Textarea(
                            id='schedule_input',
                            value='',
                            style={'width': '90%',
                                   'margin-left':'5%',
                                   'height': 100},
                        ),

                        html.Button('Select single schedule',
                            id = 'update_selected_schedule',
                            className = "btn btn-secondary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin':'5%'
                                },),

                        html.Button('Done Updating Schedule',
                            id = 'done_updating_schedule',
                            className = "btn btn-secondary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin':'5%'
                                },),

                        ],id = 'schedules',
                        hidden = True,
                        style = {
                            'borderWidth': '1px',
                            'borderStyle': 'solid',
                            'borderRadius': '5px',
                            },),

                    html.Br(),

                    # Box 3 C2
                    html.Div([

                        dcc.Checklist([
                            {'label' : " Simulation Variables", 'value' : 1},
                            {'label' : " EIO", 'value' : 2}
                            ],
                            '',
                            id = 'download_selection',
                            style = {
                                'width':'95%',
                                'margin':'5%',
                            }),

                        ],id = 'download_variables',
                        hidden = True,
                        style = {
                            'borderWidth': '1px',
                            'borderStyle': 'solid',
                            'borderRadius': '5px',
                            },),

                    html.Br(),

                            ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4,),

                # Column 3
                dbc.Col([

                    html.Br(),

                    # Box 1 C3
                    html.Div([

                        # Building type selection
                        html.Label("Building Type",
                            className = 'text-left ms-4 mt-1'),
                        dcc.Dropdown(['Commercial_Prototypes','Manufactured_Prototypes','Residential_Prototypes'], '',
                            id='buildingType_selection',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%',   
                                }),

                        # Sub Level 1
                        html.Label("Sub Level 1",
                            className = 'text-left ms-4'),
                        dcc.Dropdown(options = [],
                            value = None,
                            id = 'level_1',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%',   
                                }),

                        # Sub Level 2
                        html.Label("Sub Level 2",
                            className = 'text-left ms-4'),
                        dcc.Dropdown(options = [],
                            value = None,
                            id='level_2',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%',   
                                }),

                        # Sub Level 3
                        html.Label("Sub Level 3",
                            className = 'text-left ms-4'),
                        dcc.Dropdown(options = [],
                            value = None,
                            id = 'level_3',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%',   
                                }),

                        # Location selection
                        html.Label("Location",
                            className = 'text-left ms-4'),
                        dcc.Dropdown(options = [],
                            value = None,
                            id = 'location_selection',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%',
                                'margin-bottom': '3%',   
                                },),

                        ],id = 'building_details',
                        hidden = True,
                        style = {
                            'borderWidth': '1px',
                            'borderStyle': 'solid',
                            'borderRadius': '5px',
                            }),

                    html.Br(),

                    # Box 2 C3
                    html.Div([

                        html.Button('Generate Data',
                            id = 'EPGen_Button_GenerateData',
                            className = "btn btn-secondary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin':'5%'
                                },),

                        html.Button('Download Files',
                            id = 'EPGen_Button_DownloadFiles',
                            className = "btn btn-primary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin-left':'5%',
                                'margin-bottom':'5%'
                                },),
                        dcc.Download(id = 'EPGen_Download_DownloadFiles'),

                        ],id = 'final_download',
                        hidden = True,
                        style = {
                            'borderWidth': '1px',
                            'borderStyle': 'solid',
                            'borderRadius': '5px',
                            },),

                    ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4,),

                html.Button('End Session',
                    id = 'EPGen_Button_EndSession',
                    className = "btn btn-primary btn-lg col-12",
                    style = {
                        'width':'98%',
                        },),

                ], justify = "center", align = "center"),

        ]),

#################################################################################################

# # # # # #  Aggregation Tab # # # # # # # # #

#################################################################################################


        dcc.Tab(label = 'Aggregation', className = 'text-center text-primary mb-4', children = [

            dbc.Row([

                # First Column
                dbc.Col([

                    # Input selection
                    dcc.RadioItems(
                    id = 'EPAgg_RadioButton_InputSelection',
                    labelStyle = {'display': 'block'},
                    options = [
                        {'label' : " Continue Session", 'value' : 1},
                        {'label' : " Upload Files", 'value' : 2}
                        ]  ,
                    value = '',
                    className = 'ps-4 p-3',
                    style = {
                        'width': '100%',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        }
                    ),

                    html.Br(),

                    # Box 2 C1
                    html.Div([

                        # Upload Pickled Variable file
                        dcc.Upload(['Upload Pickled Variable file'],
                            className = 'center',
                            id = 'EPAgg_Upload_Pickle',
                            style = {
                                'width': '90%',
                                'height': '40px',
                                'lineHeight': '40px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin-left': '5%',
                                'margin-top': '5%'
                                }),

                        # Upload EIO file
                        dcc.Upload(['Upload EIO file'],
                            className = 'center',
                            id = 'EPAgg_Upload_EIO',
                            style = {
                                'width': '90%',
                                'height': '40px',
                                'lineHeight': '40px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '5%',
                                }),

                        ],id = 'EPAgg_Div_UploadFiles',
                        hidden = True,
                        style = {
                            'borderWidth': '1px',
                            'borderStyle': 'solid',
                            'borderRadius': '5px',
                            #'display':'none'
                            }),

                    html.Br(),

                    # Aggregation Variables
                    html.Div([
                        dcc.RadioItems(
                            id = 'EPAgg_RadioButton_AggregationVariables',
                            labelStyle = {'display': 'block'},
                            options = [
                                {'label' : " Preselected Variables", 'value' : 1},
                                {'label' : " Custom Variables", 'value' : 2}
                                ]  ,
                            value = '',
                            className = 'ps-4 p-3',
                        ),

                        html.Label("Preselected Variables",
                            className = 'text-left ms-4'),
                        dcc.Dropdown(['Var1','Var2','Var3'], '',
                            id='EPAgg_DropDown_PreselectedVariables',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%',
                                'margin-bottom': '2.5%'
                                }),

                        html.Label("Select custom variables",
                            className = 'text-left ms-4'),
                        dcc.Dropdown(['Var1','Var2','Var3'], '',
                            id='EPAgg_DropDown_CustomVariables',
                            multi = True,
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%',
                                'margin-bottom': '2.5%'
                                }),

                    ],id = 'EPAgg_Div_AggregationVariables',
                    hidden = True,
                    style = {
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        },),

                    html.Br(),

                ], xs = 12, sm = 12, md = 6, lg = 6, xl = 6,),


                # Second Column
                dbc.Col([

                    # Box 1 C2
                    html.Div([

                        # Zone selection
                        html.Label("Zone Lists",
                            className = 'text-left ms-4 mt-1'),
                        dcc.Dropdown(['Zone list 1','Zone list 2','Zone list 3'], '',
                            id='EPAgg_DropDown_ZoneList',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%',   
                                }),

                        dcc.RadioItems(
                            id = 'EPAgg_RadioButton_AggregateTo',
                            labelStyle = {'display': 'block'},
                            options = [
                                {'label' : " Aggregate to one", 'value' : 1},
                                {'label' : " Custom Aggregation", 'value' : 2}
                                ]  ,
                            value = '',
                            className = 'ps-4 p-3',
                        ),

                        html.Label("Input Custom Aggregation Zone List (No spaces, only \",\" and \";\" for seperators)",
                            className = 'text-left ms-4 mt-1'),
                        dcc.Textarea(
                            id='EPAgg_DropDown_CustomAggregationZoneList',
                            value='',
                            style={'width': '90%',
                                   'margin-left':'5%',
                                   'height': 30},
                        ),

                        # Type of Aggregation
                        html.Label("Type of Aggregation",
                            className = 'text-left ms-4 mt-1'),
                        dcc.Dropdown([
                            {'label' : " Average", 'value' : 1},
                            {'label' : " Weighted Floor Area Average", 'value' : 2},
                            {'label' : " Weighted Volume Average", 'value' : 3},
                            ], '',
                            id='EPAgg_DropDown_TypeOfAggregation',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%', 
                                'margin-bottom': '2.5%'  
                                }),

                    ],id = 'EPAgg_Div_AggregationDetails',
                    hidden = True,
                    style = {
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        },),

                    html.Br(),

                    # Box 2 C2
                    html.Div([

                        html.Button('Aggregate',
                            id = 'EPAgg_Button_Aggregate',
                            className = "btn btn-secondary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin':'5%'
                                },),

                        html.Button('Download',
                            id = 'EPAgg_Button_Download',
                            className = "btn btn-primary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin-left':'5%',
                                'margin-bottom':'5%'
                                },),
                        dcc.Download(id = 'EPAgg_Download_DownloadFiles'),

                    ],id = 'EPAgg_Div_FinalDownload',
                    hidden = True,
                    style = {
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        },),

                    html.Br(),

                ], xs = 12, sm = 12, md = 6, lg = 6, xl = 6,),

                html.Button('End Session',
                    id = 'Button_es_aggregation',
                    className = "btn btn-primary btn-lg col-12",
                    style = {
                        'width':'98%',
                        'margin-left':'1%'
                        },),

                ])
            ]),

#################################################################################################

# # # # # #  Visualization & Analysis Tab # # # # # # # # #

#################################################################################################


        dcc.Tab(label = 'Visualization & Analysis', className = 'text-center text-primary mb-4', children = [

            # Row 3
            dbc.Row([

                dbc.Col([

                    html.Div([

                        html.H5("Data Source",
                            className = 'text-left text-secondary mb-1 ms-3 mt-2'),

                        dcc.RadioItems(
                            id = 'EPVis_RadioButton_DataSource',
                            labelStyle = {'display': 'block'},
                            options = [
                                {'label' : " Continue Session", 'value' : 1},
                                {'label' : " Upload Files", 'value' : 2},
                                ],
                            value = '',
                            className = 'ps-4 p-2',
                        ),
                    ],
                    style = {
                        'width': '100%',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        }
                    ),], xs = 12, sm = 12, md = 6, lg = 6, xl = 6), # width = 12

                dbc.Col([

                    html.Div([

                        html.H5("Data to be selected",
                                className = 'text-left text-secondary mb-1 ms-3 mt-2'),

                        dcc.RadioItems(
                            id = 'EPVis_RadioButton_DataToBeSelected',
                            labelStyle = {'display': 'block'},
                            options = [
                                {'label' : " Generated Data", 'value' : 1},
                                {'label' : " Aggregated Data", 'value' : 2},
                                {'label' : " Both", 'value' : 3}
                                ]  ,
                            value = '',
                            className = 'ps-4 p-2',
                        ),
                    ],
                    id = 'EPVis_Div_Datatobeselected',
                    hidden = True,
                    style = {
                        'width': '100%',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        }
                    ),], xs = 12, sm = 12, md = 6, lg = 6, xl = 6), # width = 12

                ], justify = "center", align = "center"),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Row 5, upload files
                html.Div([

                    # Upload Generated data
                    dcc.Upload(
                        id='EPVis_Upload_GeneratedData',
                        children='Drag and Drop or Select Files for Generated Data',
                        style={
                            'width': '98.5%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                    ),

                    # Break Row
                    dbc.Row([dbc.Col([html.Br()], width = 12),]),

                    # Upload Aggregated data
                    dcc.Upload(
                        id='EPVis_Upload_AggregatedData',
                        children='Drag and Drop or Select Files for Aggregated Data',
                        style={
                            'width': '98.5%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                    ),

                    ],id = 'EPVis_Div_UploadData',
                    hidden = True,
                    style = {
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        #'display':'none'
                        }),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Row 7
            dbc.Row([

                dbc.Col([

                    html.Div([

                        html.H5("Date Range from Uploaded File:",
                            className = 'text-left text-secondary mb-2'),

                        dcc.DatePickerRange(
                            id='EPVis_DatePickerRange_UploadedFile',
                            min_date_allowed=date(2000, 1, 1),
                            max_date_allowed=date(2021, 12, 31),
                            initial_visible_month=date(2020, 1, 1),
                            start_date=date(2020, 1, 1),
                            end_date=date(2020, 12, 31)
                        ),

                    ],
                    id = 'EPVis_Div_DateRangeUploadedFile',
                    hidden = True
                    ),

                    ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

                ], justify = "left", align = "center"),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            dbc.Row([

                dbc.Col([

                    html.Div([

                        html.H5("Select Date Range for Visualization:",
                            className = 'text-left text-secondary mb-2'),

                        dcc.DatePickerRange(
                            id='EPVis_DatePickerRange_Visualization',
                            min_date_allowed=date(2000, 1, 1),
                            max_date_allowed=date(2021, 12, 31),
                            initial_visible_month=date(2020, 1, 1),
                        ),

                    ],
                    id = 'EPVis_Div_DateRangeVis',
                    hidden = True
                    ),

                    ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

                ], justify = "left", align = "center"),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Row 12
            dbc.Row([

                dbc.Col([

                    html.H3("Select Variable:",
                            className = 'text-left text-secondary mb-2'),

                    ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

                ], justify = "left", align = "center"),

            # Row 13
            dbc.Row([

                dbc.Col([

                    html.Div([

                        html.H5("Generated Data",
                            className = 'text-left text-secondary mb-2 ms-4 mt-2'),

                        dcc.Dropdown([], '',
                            id='EPVis_DropDown_GeneratedDataTables',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%', 
                                'margin-bottom': '2.5%'  
                                }),

                        dcc.Dropdown([], '',
                            id='EPVis_DropDown_GeneratedDataColumns',
                            multi = True,
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%', 
                                'margin-bottom': '2.5%'  
                                }),

                    ],
                    id = 'EPVis_Div_SelectVariableGenerateData',
                    hidden = True,
                    style = {
                                'width': '100%',
                                'borderWidth': '1px',
                                'borderStyle': 'solid',
                                'borderRadius': '5px',
                                }),

                    ], xs = 12, sm = 12, md = 6, lg = 6, xl = 6), # width = 12

                dbc.Col([

                    html.Div([

                        html.H5("Aggregated Data",
                            className = 'text-left text-secondary mb-2 ms-4 mt-2'),

                        dcc.Dropdown([], '',
                            id='EPVis_DropDown_AggregatedDataTables',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%', 
                                'margin-bottom': '2.5%'  
                                }),

                        dcc.Dropdown([], '',
                            id='EPVis_DropDown_AggregatedDataColumns',
                            multi = True,
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%', 
                                'margin-bottom': '2.5%'  
                                }),

                    ],
                    id = 'EPVis_Div_SelectVariableAggregateData',
                    hidden = True,
                    style = {
                                'width': '100%',
                                'borderWidth': '1px',
                                'borderStyle': 'solid',
                                'borderRadius': '5px',
                                }),

                    ], xs = 12, sm = 12, md = 6, lg = 6, xl = 6), # width = 12

                ], justify = "center", align = "center"),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),


            dbc.Row(
                dbc.Col(
                    html.H3("Distribution Plot:", className = 'text-left text-secondary mb-2'),
                    width = 12
                ), # width = 12
                justify = "left",
                align = "center"
            ),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Row 14
            dbc.Row([

                dbc.Col([

                    html.Button(
                        'Generated Data',
                        id = 'EPVis_Button_DistGeneratedData',
                        hidden = True,
                        className = "btn btn-primary btn-lg col-12"
                    ),

                    ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4), # width = 12

                dbc.Col([

                    html.Button(
                        'Aggregated Data',
                        id = 'EPVis_Button_DistAggregatedData',
                        hidden = True,
                        className = "btn btn-primary btn-lg col-12"
                    ),

                    ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4), # width = 12

                dbc.Col([

                    html.Button('Both',
                                id = 'EPVis_Button_DistBothData',
                                hidden = True,
                                className = "btn btn-primary btn-lg col-12"),

                    ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4), # width = 12

                ], justify = "center", align = "center"),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Row 15
            dbc.Row([

                dbc.Col([

                    dcc.Graph(id = 'EPVis_Graph_Distribution', figure ={}),

                    ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

            ], justify = "center", align = "center"),

            dbc.Row([
                dbc.Col([
                    html.Br()
                ], width = 12),
            ]),

            html.Div([
                dbc.Row([
                    dash_table.DataTable(
                        id='EPVis_Table_GeneratedData',
                        columns=['Variable', 'Mean', 'Variance', 'Standard Deviation', 'Range'],
                        data=None
                    ),
                ]),
                dbc.Row([
                    dbc.Col([html.H4('Generated Data')], width = 2),
                    dbc.Col([html.H4('Mean:')], width = 2),
                    dbc.Col([html.H4('Variance:')], width = 2),
                    dbc.Col([html.H4('Standard Deviation:')], width = 3),
                    dbc.Col([html.H4('Range:')], width = 3),
                ]),
                ],id = 'EPVis_Row_GeneratedDataDetails',
                hidden = True,
                style = {
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderRadius': '5px',
                    },),

            # Break Row
            dbc.Row([
                dbc.Col([
                    html.Br()
                ], width = 12),

            ]),

            html.Div([
                dbc.Row([
                    dbc.Col([html.H4('Aggregated Data')], width = 2),
                    dbc.Col([html.H4('Mean:')], width = 2),
                    dbc.Col([html.H4('Variance:')], width = 2),
                    dbc.Col([html.H4('Standard Deviation:')], width = 3),
                    dbc.Col([html.H4('Range:')], width = 3),
                ]),
                ],id = 'EPVis_Row_AggregatedDataDetails',
                hidden = True,
                style = {
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderRadius': '5px',
                    },),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Row 11
            dbc.Row([

                dbc.Col([

                    html.H3("Scatter Plot:",
                            className = 'text-left text-secondary mb-2')

                    ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

                ], justify = "left", align = "center"),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            dbc.Row([

                dbc.Col([

                    html.H5("Please select two variables",
                            className = 'text-left text-secondary mb-2',
                            id = 'EPVis_H5_ScatterPlotComment',
                            hidden = False)

                    ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

                ], justify = "left", align = "center"),

            # Row 14
            dbc.Row([

                dbc.Col([

                    html.Button('Generated Data',
                                id = 'EPVis_Button_ScatterGeneratedData',
                                hidden = True,
                                className = "btn btn-primary btn-lg col-12"),

                    ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4), # width = 12

                dbc.Col([

                    html.Button('Aggregated Data',
                                id = 'EPVis_Button_ScatterAggregatedData',
                                hidden = True,
                                className = "btn btn-primary btn-lg col-12"),

                    ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4), # width = 12

                dbc.Col([

                    html.Button('Both',
                                id = 'EPVis_Button_ScatterBothData',
                                hidden = True,
                                className = "btn btn-primary btn-lg col-12"),

                    ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4), # width = 12

                ], justify = "center", align = "center"),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Row 15
            dbc.Row([

                dbc.Col([

                    dcc.Graph(id = 'EPVis_Graph_Scatter', figure ={}),

                    ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

                ], justify = "center", align = "center"),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Row 16
            dbc.Row([

                dbc.Col([

                    html.H3("Time Series Plot:",
                            className = 'text-left text-secondary mb-2')

                    ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

                ], justify = "left", align = "center"),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Row 14
            dbc.Row([

                dbc.Col([

                    html.Button('Generated Data',
                                id = 'EPVis_Button_TimeGeneratedData',
                                hidden = True,
                                className = "btn btn-primary btn-lg col-12"),

                    ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4), # width = 12

                dbc.Col([

                    html.Button('Aggregated Data',
                                id = 'EPVis_Button_TimeAggregatedData',
                                hidden = True,
                                className = "btn btn-primary btn-lg col-12"),

                    ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4), # width = 12

                dbc.Col([

                    html.Button('Both',
                                id = 'EPVis_Button_TimeBothData',
                                hidden = True,
                                className = "btn btn-primary btn-lg col-12"),

                    ], xs = 12, sm = 12, md = 4, lg = 4, xl = 4), # width = 12

                ], justify = "center", align = "center"),

            # Break Row
            dbc.Row([dbc.Col([html.Br()], width = 12),]),

            # Row 15
            dbc.Row([

                dbc.Col([

                    dcc.Graph(id = 'EPVis_Graph_TimeSeries', figure ={}),

                    ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

                ], justify = "center", align = "center"),

            # Break Row
            dbc.Row([

                dbc.Col([

                    html.Br(),
                    html.Button('End Session',
                    id = 'Button_es_visualization',
                    className = "btn btn-primary btn-lg col-12",
                    ),

                    ], width = 12),

                ]),

            ])

    ])

], fluid = False)

# App Callbacks - Providing Functionality

@app.callback(
    Output(component_id = 'building_details', component_property = 'hidden'),
    Output(component_id = 'upload_files', component_property = 'hidden'),
    Output(component_id = 'simulation_details', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'schedules', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'generate_variables', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'download_variables', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'final_download', component_property = 'hidden', allow_duplicate = True),
    State(component_id = 'folder_name', component_property = 'value'),
    Input(component_id = 'database_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Radiobutton_DatabaseSelection_Interaction(folder_name, database_selection):
    global SIMULATION_FOLDERPATH
    global SIMULATION_FOLDERNAME
    if database_selection == 1:
        building_details = False
        upload_files = True
        simulation_details = True
        schedules = True
        generate_variables = True
        download_variables = True
        final_download = True

    elif database_selection == 2:
        building_details = True
        upload_files = False
        simulation_details = True
        schedules = True
        generate_variables = True
        download_variables = True
        final_download = True

    else:
        building_details = True
        upload_files = True
        simulation_details = True
        schedules = True
        generate_variables = True
        download_variables = True
        final_download = True

    if folder_name is None:
        z = 0
    else:
        SIMULATION_FOLDERNAME = folder_name

    SIMULATION_FOLDERPATH = os.path.join(WORKSPACE_DIRECTORY, SIMULATION_FOLDERNAME)

    if os.path.isdir(SIMULATION_FOLDERPATH):
        z = 0
    else:
        os.mkdir(SIMULATION_FOLDERPATH)

    return building_details, upload_files, simulation_details , schedules, generate_variables, download_variables, final_download

@app.callback(
    Output(component_id = 'upload_idf', component_property = 'children'),
    Input(component_id = 'upload_idf', component_property = 'filename'),
    State(component_id = 'upload_idf', component_property = 'contents'),
    prevent_initial_call = False)
def EPGen_Upload_IDF_Interaction(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file(filename, content, UPLOAD_DIRECTORY)
        message = 'File Uploaded'

    else:
        message = 'Upload IDF file'

    return message

@app.callback(
    Output(component_id = 'upload_epw', component_property = 'children'),
    Input(component_id = 'upload_epw', component_property = 'filename'),
    State(component_id = 'upload_epw', component_property = 'contents'),
    prevent_initial_call = False)
def EPGen_Upload_EPW_Interaction(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file(filename, content, UPLOAD_DIRECTORY)
        message = 'File Uploaded'

    else:
        message = 'Upload EPW file'

    return message

@app.callback(
    Output(component_id = 'simulation_details', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'version_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_EPVersion_Interaction(version_selection):
    if version_selection != None :
        simulation_details = False
    else:
        simulation_details = True
    return simulation_details

@app.callback(
    Output(component_id = 'simulation_details', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'location_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_Location_Interaction(location_selection):
    if location_selection is None :
        simulation_details = True
    else:
        simulation_details = False
    return simulation_details

@app.callback(
    Output(component_id = 'generate_variables', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'simReportFreq_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_SimReportFreq_Interaction(simReportFreq_selection):
    if simReportFreq_selection is not None:
        generate_variables = False
    else:
        generate_variables = True
    return generate_variables

# Variable selection radio button interaction
@app.callback(
    Output(component_id = 'schedules', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'people_schedules', component_property = 'options'),
    Output(component_id = 'equip_schedules', component_property = 'options'),
    Output(component_id = 'light_schedules', component_property = 'options'),
    Output(component_id = 'heating_schedules', component_property = 'options'),
    Output(component_id = 'cooling_schedules', component_property = 'options'),
    Output(component_id = 'temperature_schedules', component_property = 'options'),
    Input(component_id = 'EPGen_Radiobutton_EditSchedules', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_RadioButton_EditSchedule_Interaction(EPGen_Radiobutton_VariableSelection):
    initial_run_folder_path = os.path.join(SIMULATION_FOLDERPATH, 'Initial_run_folder')
    if EPGen_Radiobutton_VariableSelection == 1:
        schedules = False
        eio_FilePath = os.path.join(initial_run_folder_path, "eplusout.eio")
        Eio_OutputFile_Dict = AppFuncs.EPGen_eio_dict_generator(eio_FilePath)

        People_Schedules = Eio_OutputFile_Dict['People Internal Gains Nominal']['Schedule Name'].tolist()
        People_Schedules = list(set(People_Schedules))

        Equip_Schedules = Eio_OutputFile_Dict['ElectricEquipment Internal Gains Nominal']['Schedule Name'].tolist()
        Equip_Schedules = list(set(Equip_Schedules))

        Light_Schedules = Eio_OutputFile_Dict['Lights Internal Gains Nominal']['Schedule Name'].tolist()
        Light_Schedules = list(set(Light_Schedules))

        # Finding directory of .idf and .epw files
        for file in os.listdir(initial_run_folder_path):
            if file.endswith(".idf"):
                IDF_FilePath = os.path.join(initial_run_folder_path, file)
        
        # Load IDF File
        Current_IDFFile = op.Epm.load(IDF_FilePath)

        # Getting ThermalSetpoint items
        filtered_items = [item for item in dir(Current_IDFFile) if "ThermostatSetpoint" in item]
        ThermostatSetpoint_List = []
        for attr in filtered_items:
            if not attr.startswith('__'):
                value = getattr(Current_IDFFile, attr)
                ThermostatSetpoint_List.append(value)

        counter  = -1
        ThermostatSetpoint_attribute_nameList = ['heating_setpoint_temperature_schedule_name', 'cooling_setpoint_temperature_schedule_name', 'setpoint_temperature_schedule_name']
        HeatingSetpoint_List = []
        CoolingSetpoint_List = []
        TemperatureSetpoint_List = []

        for item in filtered_items:
            counter = counter + 1
            if not item:
                continue
            else:
                Current_ThermostatSetpoint_dict = ThermostatSetpoint_List[counter]._records

                for Current_key in Current_ThermostatSetpoint_dict:
                    Current_ThermostatSetpoint_element = Current_ThermostatSetpoint_dict[Current_key]

                    for attr in ThermostatSetpoint_attribute_nameList:
                        try:
                            Current_ThermostatSetpoint_element_value = getattr(Current_ThermostatSetpoint_element, attr)

                        except:
                            continue

                        else:
                            if attr == 'heating_setpoint_temperature_schedule_name':
                                HeatingSetpoint_List.append(Current_ThermostatSetpoint_element_value.name)

                            if attr == 'cooling_setpoint_temperature_schedule_name':
                                CoolingSetpoint_List.append(Current_ThermostatSetpoint_element_value.name)

                            if attr == 'setpoint_temperature_schedule_name':
                                TemperatureSetpoint_List.append(Current_ThermostatSetpoint_element_value.name)

        HeatingSetpoint_Schedules = list(set(HeatingSetpoint_List))
        CoolingSetpoint_Schedules = list(set(CoolingSetpoint_List))
        TemperatureSetpoint_Schedules = list(set(TemperatureSetpoint_List))
    elif EPGen_Radiobutton_VariableSelection == 2:
        schedules = True
        People_Schedules = []
        Equip_Schedules = []
        Light_Schedules = []
        HeatingSetpoint_Schedules = []
        CoolingSetpoint_Schedules = []
        TemperatureSetpoint_Schedules = []
    else:
        schedules = True
        People_Schedules = []
        Equip_Schedules = []
        Light_Schedules = []
        HeatingSetpoint_Schedules = []
        CoolingSetpoint_Schedules = []
        TemperatureSetpoint_Schedules = []

    edited_idf_folder_path = os.path.join(SIMULATION_FOLDERPATH,'Edited_idf_folder')

    if os.path.isdir(edited_idf_folder_path):
        z = 0
    else:
        os.mkdir(edited_idf_folder_path)
        for item in os.listdir(initial_run_folder_path):
            if (item.endswith(".idf") or item.endswith(".epw")) and (not item.startswith("opyplus")):
                shutil.copy(os.path.join(initial_run_folder_path,item), edited_idf_folder_path)

    #Current_IDFFile.ThermostatSetpoint_DualSetpoint._records['core_zn dualspsched'].heating_setpoint_temperature_schedule_name.name

    return schedules, People_Schedules, Equip_Schedules, Light_Schedules, HeatingSetpoint_Schedules, CoolingSetpoint_Schedules, TemperatureSetpoint_Schedules

@app.callback(
    Output(component_id = 'final_download', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'download_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_DownloadSelection_Interaction(download_selection):
    if download_selection != '' :
        final_download = False
    else:
        final_download = True
    return final_download


# Level 1 list
@app.callback(
    Output(component_id = 'level_1', component_property = 'options'),
    Output(component_id = 'level_2', component_property = 'options', allow_duplicate = True),
    Output(component_id = 'level_3', component_property = 'options', allow_duplicate = True),
    Output(component_id = 'location_selection', component_property = 'options'),
    Output(component_id = 'level_1', component_property = 'value'),
    Output(component_id = 'level_2', component_property = 'value', allow_duplicate = True),
    Output(component_id = 'level_3', component_property = 'value', allow_duplicate = True),
    Output(component_id = 'location_selection', component_property = 'value'),
    Input(component_id = 'buildingType_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_BuildingType_Interaction(buildingType_selection):
    # Listing next sub level of folders
    if buildingType_selection is not None:
        FilePath = os.path.join(os.getcwd(), "../../Data/", buildingType_selection)
        level_1_list = AppFuncs.list_contents(FilePath)
        level_2_list = []
        level_3_list = []

        if buildingType_selection == 'Commercial_Prototypes':
            Weather_FilePath = os.path.join(DATA_DIRECTORY, "TMY3_WeatherFiles_Commercial")
            Weather_list = AppFuncs.list_contents(Weather_FilePath)
        elif buildingType_selection == 'Manufactured_Prototypes':
            Weather_FilePath = os.path.join(DATA_DIRECTORY, "TMY3_WeatherFiles_Manufactured")
            Weather_list = AppFuncs.list_contents(Weather_FilePath)
        elif buildingType_selection == 'Residential_Prototypes':
            Weather_FilePath = os.path.join(DATA_DIRECTORY, "TMY3_WeatherFiles_Residential")
            Weather_list = AppFuncs.list_contents(Weather_FilePath)

    else:
        level_1_list = []
        level_2_list = []
        level_3_list = []
        Weather_list = []

    level_1_value = None
    level_2_value = None
    level_3_value = None
    Weather_value = None

    return level_1_list, level_2_list, level_3_list, Weather_list, level_1_value, level_2_value, level_3_value, Weather_value


# Level 2 list
@app.callback(
    Output(component_id = 'level_2', component_property = 'options', allow_duplicate = True),
    Output(component_id = 'level_3', component_property = 'options', allow_duplicate = True),
    Output(component_id = 'level_2', component_property = 'value', allow_duplicate = True),
    Output(component_id = 'level_3', component_property = 'value', allow_duplicate = True),
    State(component_id = 'buildingType_selection', component_property = 'value'),
    Input(component_id = 'level_1', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_SubLevel1_Interaction(buildingType_selection, level_1):
    # Listing next sub level of folders
    if level_1 is not None:
        FilePath = os.path.join(os.getcwd(), "../../Data/", buildingType_selection, level_1)
        level_2_list = AppFuncs.list_contents(FilePath)
        level_3_list = []

    else:
        level_2_list = []
        level_3_list = []

    level_2_value = None
    level_3_value = None

    return level_2_list, level_3_list, level_2_value, level_3_value

# Level 3 list
@app.callback(
    Output(component_id = 'level_3', component_property = 'options', allow_duplicate = True),
    Output(component_id = 'level_3', component_property = 'value', allow_duplicate = True),
    State(component_id = 'buildingType_selection', component_property = 'value'),
    State(component_id = 'level_1', component_property = 'value'),
    Input(component_id = 'level_2', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_SubLevel2_Interaction(buildingType_selection, level_1, level_2):
    # Listing next sub level of folders
    if level_2 is not None:
        FilePath = os.path.join(os.getcwd(), "../../Data/", buildingType_selection, level_1, level_2)
        level_3_list = AppFuncs.list_contents(FilePath)
        level_3_list = [file for file in level_3_list if file.endswith('.idf')]

    else:
        level_3_list = []

    level_3_value = None

    return level_3_list, level_3_value

# Generate Variable List Button (Initial Run)
@app.callback(
    Output(component_id = 'your_variable_selection', component_property = 'options'),
    Output(component_id = 'our_variable_selection', component_property = 'options'),
    State(component_id = 'database_selection', component_property = 'value'),
    State(component_id = 'buildingType_selection', component_property = 'value'),
    State(component_id = 'level_1', component_property = 'value'),
    State(component_id = 'level_2', component_property = 'value'),
    State(component_id = 'level_3', component_property = 'value'),
    State(component_id = 'location_selection', component_property = 'value'),
    Input(component_id = 'EPGen_Button_GenerateVariables', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_GenerateVariables_Interaction(database_selection, buildingType_selection, level_1, level_2, level_3, location_selection, n_clicks):

    # Creating idf_weather_folder
    idf_weather_folder_path = os.path.join(SIMULATION_FOLDERPATH, "idf_weather_folder")
    if os.path.isdir(idf_weather_folder_path):
        z = 0
    else:
        os.mkdir(idf_weather_folder_path)

    # Copying files to idf_weather_folder
    if database_selection == 1:
        idf_original_path = os.path.join(DATA_DIRECTORY, buildingType_selection, level_1, level_2, level_3)
        shutil.copy(idf_original_path, idf_weather_folder_path)
        if buildingType_selection == 'Commercial_Prototypes':
            Weather_original_path = os.path.join(DATA_DIRECTORY, "TMY3_WeatherFiles_Commercial", location_selection)
        elif buildingType_selection == 'Manufactured_Prototypes':
            Weather_original_path = os.path.join(DATA_DIRECTORY, "TMY3_WeatherFiles_Manufactured", location_selection)
        elif buildingType_selection == 'Residential_Prototypes':
            Weather_original_path = os.path.join(DATA_DIRECTORY, "TMY3_WeatherFiles_Residential", location_selection)
        shutil.copy(Weather_original_path, idf_weather_folder_path)

    elif database_selection == 2:
        for item in os.listdir(UPLOAD_DIRECTORY):
            if os.path.isfile(os.path.join(UPLOAD_DIRECTORY,item)):
                shutil.copy(os.path.join(UPLOAD_DIRECTORY,item), idf_weather_folder_path)

    # Appending Special.idf to selected idf file
    for file in os.listdir(idf_weather_folder_path):
        if file.endswith(".idf"):
            file1_path = os.path.join(idf_weather_folder_path, file)
            file2_path = os.path.join(DATA_DIRECTORY, "Special.idf")
            with open(file2_path, 'r') as file2:
                with open(file1_path, 'a') as file1:
                    shutil.copyfileobj(file2, file1)

    # Creating inirial_run_folder
    initial_run_folder_path = os.path.join(SIMULATION_FOLDERPATH, 'Initial_run_folder')
    if os.path.isdir(initial_run_folder_path):
        z = 0
    else:
        os.mkdir(initial_run_folder_path)

    # Copying updated idf and epw to initial run folder
    for item in os.listdir(idf_weather_folder_path):
        shutil.copy(os.path.join(idf_weather_folder_path,item), initial_run_folder_path)

    # Finding directory of .idf and .epw files
    for file in os.listdir(initial_run_folder_path):
        if file.endswith(".idf"):
            Temporary_IDF_FilePath = os.path.join(initial_run_folder_path, file)

    for file in os.listdir(initial_run_folder_path):
        if file.endswith(".epw"):
            Temporary_Weather_FilePath = os.path.join(initial_run_folder_path, file)

    # This section is for initial run to get .eio file and variables
    Initial_IDF_Run = op.simulate(Temporary_IDF_FilePath, Temporary_Weather_FilePath, base_dir_path = initial_run_folder_path)

    # Collecting Simulation Variable List
    with open(os.path.join(initial_run_folder_path, 'eplusout.rdd')) as f:
        lines = f.readlines()

    Simulation_VariableNames = []

    Counter_Lines = 0

    for line in lines:
        if (Counter_Lines > 1):
            split_line = line.split(',')
            Simulation_VariableNames.append(split_line[2].split('[')[0])

        Counter_Lines = Counter_Lines + 1
        # Simulation_VariableNames.append(split_line[2])
        # split_line_unit = split_line[3].split('[')[1]
        # split_line_unit = split_line_unit[0].split(']')[0]
        # Simulation_VariableNames.append(split_line_unit)

    Simulation_VariableNames.sort()

    modified_OUR_VARIABLE_LIST = []
    for item in OUR_VARIABLE_LIST:
        # Remove the last underscore
        item = item.rstrip('_')
        # Replace remaining underscores with spaces
        item = item.replace('_', ' ')
        modified_OUR_VARIABLE_LIST.append(item)

    modified_OUR_VARIABLE_LIST.sort()

    your_variable_selection = Simulation_VariableNames
    our_variable_selection = modified_OUR_VARIABLE_LIST
    return your_variable_selection, our_variable_selection

@app.callback(
    Output(component_id = 'update_selected_schedule', component_property = 'children', allow_duplicate = True),
    Input(component_id = 'people_schedules', component_property = 'value'),
    Input(component_id = 'equip_schedules', component_property = 'value'),
    Input(component_id = 'light_schedules', component_property = 'value'),
    Input(component_id = 'heating_schedules', component_property = 'value'),
    Input(component_id = 'cooling_schedules', component_property = 'value'),
    Input(component_id = 'temperature_schedules', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_EditSchedule_Interaction(people_schedules, equip_schedules, light_schedules, heating_schedules, cooling_schedules, temperature_schedules):
    if (not (people_schedules is None)) or (not (equip_schedules is None)) or (not (light_schedules is None)) or (not (heating_schedules is None)) or (not (cooling_schedules is None)) or (not (temperature_schedules is None)):
        update_selected_schedule = "Update selected schedule"
    else:
        update_selected_schedule = "Select single schedule"
    return update_selected_schedule

@app.callback(
    Output(component_id = 'update_selected_schedule', component_property = 'children', allow_duplicate = True),
    State(component_id = 'people_schedules', component_property = 'value'),
    State(component_id = 'equip_schedules', component_property = 'value'),
    State(component_id = 'light_schedules', component_property = 'value'),
    State(component_id = 'heating_schedules', component_property = 'value'),
    State(component_id = 'cooling_schedules', component_property = 'value'),
    State(component_id = 'temperature_schedules', component_property = 'value'),
    State(component_id = 'schedule_input', component_property = 'value'),
    Input(component_id = 'update_selected_schedule', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_UpdateSelectedSchedule_Interaction(people_schedules, equip_schedules, light_schedules, heating_schedules, cooling_schedules, temperature_schedules, schedule_input, n_clicks):

    schedule_list = [people_schedules, equip_schedules, light_schedules, heating_schedules, cooling_schedules, temperature_schedules]

    edited_idf_folder_path = os.path.join(SIMULATION_FOLDERPATH,'Edited_idf_folder')

    count_none = 0

    for schedule in schedule_list:
        if schedule is None:
            count_none = count_none + 1
        else:
            desired_schedule = schedule

    if count_none != 5:
        update_selected_schedule = "Please select one"
    else:
        for item in os.listdir(edited_idf_folder_path):
            if item.endswith(".idf"):
                IDF_FilePath = os.path.join(edited_idf_folder_path, item)

        Edited_IDFFile = op.Epm.load(IDF_FilePath)

        # Step 1 Get compact schedule from edited idf
        Edited_ScheduleCompact = Edited_IDFFile.Schedule_Compact

        # Step 2 Get table from compact schedule which corresponds to desired schedule
        Current_Schedule_1 = Edited_ScheduleCompact.one(lambda x: x.name == desired_schedule.lower())

        # Step 3 change the name to something xyz@123 add user defined schedule
        Current_Schedule_1.name = 'xyz'

        lines  = schedule_input.split('\n')

        Rough_schedule_lines_list = [line.strip() for line in lines]

        new_schedule_rough = {}

        for line1 in Rough_schedule_lines_list:
            Current_line_elements = line1.split('!-')
            Current_value = Current_line_elements[0].strip()
            Current_key = Current_line_elements[1].lower().strip().replace(' ', '_')

            if Current_value[-1] == ',':
                Current_value = Current_value[:-1]

            new_schedule_rough[Current_key] = Current_value

        new_sch = Edited_ScheduleCompact.add(new_schedule_rough)

        # Step 4 Use opyplus to overwrite edited file
        Edited_IDFFile.save(IDF_FilePath)

        # Step 5 Read the file and change particular name to desired name
        with open(IDF_FilePath, 'r') as file:
            lines = file.readlines()

        for ii in range(len(lines)):

            if ii == 0:
                continue
            else:
                line_k = lines[ii-1]
                line_k_plus_1 = lines[ii]

                if not (line_k.find('Schedule:Compact') >= 0):

                    if line_k_plus_1.find('xyz') >= 0:

                        lines[ii] = line_k_plus_1.replace('xyz', desired_schedule.lower())

        # Step 6 OverWrite the file again
        with open(IDF_FilePath, 'w') as file:
            # Write each item in the list to the file
            for line in lines:
                file.write(line)

        # Step 7 update update_selected_schedule
        update_selected_schedule = "Schedule updated"

    return update_selected_schedule

@app.callback(
    Output(component_id = 'download_variables', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'EPGen_Radiobutton_EditSchedules', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_RadioButton_EditSchedules_Interaction_2(EPGen_Radiobutton_VariableSelection):

    if EPGen_Radiobutton_VariableSelection == 2:

        download_variables = False

    return download_variables


@app.callback(
    Output(component_id = 'download_variables', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'done_updating_schedule', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_DoneUpdatingSchedule_Interaction(n_clicks):

    download_variables = False

    return download_variables

@app.callback(
    Output(component_id = 'final_download', component_property = 'hidden'),
    Input(component_id = 'download_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Checkbox_DownloadSelection_Interaction(download_selection):

    if download_selection != '':

        final_download = False

    return final_download

@app.callback(
    Output(component_id = 'EPGen_Button_GenerateData', component_property = 'children'),
    State(component_id = 'download_selection', component_property = 'value'),
    State(component_id = 'sim_run_period', component_property = 'start_date'),
    State(component_id = 'sim_run_period', component_property = 'end_date'),
    State(component_id = 'sim_TimeStep', component_property = 'value'),
    State(component_id = 'simReportFreq_selection', component_property = 'value'),
    State(component_id = 'EPGen_Radiobutton_VariableSelection', component_property = 'value'),
    State(component_id = 'your_variable_selection', component_property = 'value'),
    Input(component_id = 'EPGen_Button_GenerateData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_GenerateData_Interaction(download_selection, start_date, end_date, Sim_TimeStep, Sim_OutputVariable_ReportingFrequency, Var_selection, your_vars, n_clicks):

    edited_idf_folder_path = os.path.join(SIMULATION_FOLDERPATH,"Edited_idf_folder")

    # Creating final run folder and copying files to the path
    final_run_folder_path = os.path.join(SIMULATION_FOLDERPATH, "Final_run_folder")

    if os.path.isdir(final_run_folder_path):
        z = 0
    else:
        os.mkdir(final_run_folder_path)

        for item in os.listdir(edited_idf_folder_path):
            shutil.copy(os.path.join(edited_idf_folder_path,item), final_run_folder_path)

    # Finding directory of .idf and .epw files
    for file in os.listdir(final_run_folder_path):
        if file.endswith(".idf"):
            Final_IDF_FilePath = os.path.join(final_run_folder_path, file)

        if file.endswith(".epw"):
            Final_Weather_FilePath = os.path.join(final_run_folder_path, file)

    # Loading IDF File
    Current_IDFFile = op.Epm.load(Final_IDF_FilePath)

    # Editing RunPeriod
    Current_IDF_RunPeriod = Current_IDFFile.RunPeriod.one()

    IDF_FileYear, Sim_Start_Month, Sim_Start_Day = start_date.split('-')

    _, Sim_End_Month, Sim_End_Day = end_date.split('-')

    Current_IDF_RunPeriod['begin_day_of_month'] = Sim_Start_Day

    Current_IDF_RunPeriod['begin_month'] = Sim_Start_Month

    Current_IDF_RunPeriod['end_day_of_month'] = Sim_End_Day

    Current_IDF_RunPeriod['end_month' ]= Sim_End_Month

    # Editing TimeStep
    Current_IDF_TimeStep = Current_IDFFile.TimeStep.one()

    Current_IDF_TimeStep['number_of_timesteps_per_hour'] = int(60/Sim_TimeStep)

    # Making Additional Folders
    Sim_IDFWeatherFiles_FolderName = 'Sim_IDFWeatherFiles'
    Sim_IDFWeatherFiles_FolderPath = os.path.join(final_run_folder_path, Sim_IDFWeatherFiles_FolderName)

    Sim_OutputFiles_FolderName = 'Sim_OutputFiles'
    Sim_OutputFiles_FolderPath = os.path.join(final_run_folder_path, Sim_OutputFiles_FolderName)

    Sim_IDFProcessedData_FolderName = 'Sim_ProcessedData'
    Sim_IDFProcessedData_FolderPath = os.path.join(final_run_folder_path, Sim_IDFProcessedData_FolderName)

    # Checking if Folders Exist if not create Folders
    if (os.path.isdir(Sim_IDFWeatherFiles_FolderPath)):

        z = None

    else:

        os.mkdir(Sim_IDFWeatherFiles_FolderPath)

        os.mkdir(Sim_OutputFiles_FolderPath)

        os.mkdir(Sim_IDFProcessedData_FolderPath)

    # Overwriting Edited IDF
    Current_IDFFile.save(Final_IDF_FilePath)

    # Saving IDF & EPW to Sim_IDFWeatherFiles
    shutil.move(Final_IDF_FilePath, Sim_IDFWeatherFiles_FolderPath)

    shutil.move(Final_Weather_FilePath, Sim_IDFWeatherFiles_FolderPath)

    # Finding directory of .idf and .epw files
    for file in os.listdir(Sim_IDFWeatherFiles_FolderPath):
        if file.endswith(".idf"):
            Results_IDF_FilePath = os.path.join(Sim_IDFWeatherFiles_FolderPath, file)

        if file.endswith(".epw"):
            Results_Weather_FilePath = os.path.join(Sim_IDFWeatherFiles_FolderPath, file)

    # Based on selection of download
    if download_selection == [1]:

        # Sorting variable names
        if Var_selection == 1:
            Simulation_VariableNames = [var.replace('_', ' ') for var in OUR_VARIABLE_LIST]

        elif Var_selection == 2:
            Simulation_VariableNames = your_vars

        # Loading the Edited IDF File
        epm_Edited_IDFFile = op.Epm.load(Results_IDF_FilePath)

        # Getting Output Variable from Edited IDF File
        OutputVariable_QuerySet = epm_Edited_IDFFile.Output_Variable.one()

        # FOR LOOP: For Each Variable in Simulation_VariableNames
        for OutputVariable_Name in Simulation_VariableNames:

            # Updating OutputVariable_QuerySet in the Special IDF File
            OutputVariable_QuerySet['key_value'] = '*'

            OutputVariable_QuerySet['reporting_frequency'] = Sim_OutputVariable_ReportingFrequency

            OutputVariable_QuerySet['variable_name'] = OutputVariable_Name

            # Saving Special IDF File
            epm_Edited_IDFFile.save(Results_IDF_FilePath)

            # Running Building Simulation to obtain current output variable
            op.simulate(Results_IDF_FilePath, Results_Weather_FilePath, base_dir_path = Sim_OutputFiles_FolderPath)

            # Moving Output Variable CSV file to Desired Folder
            Current_CSV_FilePath = os.path.join(Sim_OutputFiles_FolderPath, "eplusout.csv")

            New_OutputVariable_FileName = OutputVariable_Name.replace(' ','_') + '.csv'

            MoveTo_CSV_FilePath = os.path.join(Sim_IDFProcessedData_FolderPath, New_OutputVariable_FileName)

            shutil.move(Current_CSV_FilePath, MoveTo_CSV_FilePath)

        # =============================================================================
        # Convert and Save Output Variables .csv to.mat in Results Folder
        # =============================================================================

        # Getting all .csv Files paths from Sim_IDFProcessedData_FolderPath
        FileName_List = os.listdir(Sim_IDFProcessedData_FolderPath)

        # Initializing CSV_FileName_List
        CSV_FilePath_List = []

        # FOR LOOP: For each file in Sim_IDFProcessedData_FolderPath
        for file in FileName_List:

            # Check only .csv files
            if file.endswith('.csv'):

                # Appending .csv file paths to CSV_FilePath_List
                CSV_FilePath_List.append(os.path.join(Sim_IDFProcessedData_FolderPath,file))

        # Initializing IDF_OutputVariable_Dict
        IDF_OutputVariable_Dict = {}

        IDF_OutputVariable_ColumnName_List = []

        Counter_OutputVariable = 0

        # FOR LOOP: For Each .csv File in CSV_FilePath_List
        for file_path in CSV_FilePath_List:

            # Reading .csv file in dataframe
            Current_DF = pd.read_csv(file_path)

            # Getting CurrentDF_1
            if (Counter_OutputVariable == 0):

                # Keeping DateTime Column
                Current_DF_1 = Current_DF

            else:

                # Dropping DateTime Column
                Current_DF_1=Current_DF.drop(Current_DF.columns[[0]],axis=1)

            # Appending Column Names to IDF_OutputVariable_ColumnName_List
            for ColumnName in Current_DF_1.columns:

                IDF_OutputVariable_ColumnName_List.append(ColumnName)

            # Getting File Name
            FileName = file_path.split('\\')[-1].split('_.')[0]

            # Storing Current_DF in IDF_OutputVariable_Dict
            IDF_OutputVariable_Dict[FileName] = Current_DF

            # Incrementing Counter_OutputVariable
            Counter_OutputVariable = Counter_OutputVariable + 1

        # Creating and saving DateTime to IDF_OutputVariable_Dict
        DateTime_List = []

        DateTime_Column = Current_DF['Date/Time']

        for DateTime in DateTime_Column:

            DateTime_Split = DateTime.split(' ')

            Date_Split = DateTime_Split[1].split('/')

            Time_Split = DateTime_Split[3].split(':')

            # Converting all 24th hour to 0th hour as hour must be in 0..23
            if int(Time_Split[0]) == 24:
                Time_Split[0] = 00

            DateTime_List.append(datetime.datetime(int(IDF_FileYear),int(Date_Split[0]),int(Date_Split[1]),int(Time_Split[0]),int(Time_Split[1]),int(Time_Split[2])))

        IDF_OutputVariable_Dict['DateTime_List'] = DateTime_List

        pickle.dump(IDF_OutputVariable_Dict, open(os.path.join(Sim_IDFProcessedData_FolderPath,"IDF_OutputVariables_DictDF.pickle"), "wb"))

    elif download_selection == [2]:

        # =============================================================================
        # Process .eio Output File and save in Results Folder
        # =============================================================================
        #
        # Running Building Simulation to obtain current output variable
        op.simulate(Results_IDF_FilePath, Results_Weather_FilePath, base_dir_path = Sim_OutputFiles_FolderPath)

        # Reading .eio Output File
        Eio_OutputFile_Path = os.path.join(Sim_OutputFiles_FolderPath,'eplusout.eio')

        # Initializing Eio_OutputFile_Dict
        Eio_OutputFile_Dict = {}

        with open(Eio_OutputFile_Path) as f:
            Eio_OutputFile_Lines = f.readlines()

        # Removing Intro Lines
        Eio_OutputFile_Lines = Eio_OutputFile_Lines[1:]

        # FOR LOOP: For each category in .eio File
        for Line_1 in Eio_OutputFile_Lines:

            # IF ELSE LOOP: To check category
            if (Line_1.find('!') >= 0):

                print(Line_1 + '\n')

                # Get the Key for the .eio File category
                Pattern_1 = "<(.*?)>"

                Category_Key = re.search(Pattern_1, Line_1).group(1)

                # Get the Column Names for the .eio File category
                DF_ColumnName_List = Line_1.split(',')[1:]

                # Removing the '\n From the Last Name
                DF_ColumnName_List[-1] = DF_ColumnName_List[-1].split('\n')[0]

                # Removing Empty Element
                if DF_ColumnName_List[-1] == ' ':
                    DF_ColumnName_List = DF_ColumnName_List[:-1]

                # Initializing DF_Index_List
                DF_Index_List = []

                # Initializing DF_Data_List
                DF_Data_List = []

                # FOR LOOP: For all elements of current .eio File category
                for Line_2 in Eio_OutputFile_Lines:

                    # IF ELSE LOOP: To check data row belongs to current Category
                    if ((Line_2.find('!') == -1) and (Line_2.find(Category_Key) >= 0)):

                        print(Line_2 + '\n')

                        DF_ColumnName_List_Length = len(DF_ColumnName_List)

                        # Split Line_2
                        Line_2_Split = Line_2.split(',')

                        # Removing the '\n From the Last Data
                        Line_2_Split[-1] = Line_2_Split[-1].split('\n')[0]

                        # Removing Empty Element
                        if Line_2_Split[-1] == ' ':
                            Line_2_Split = Line_2_Split[:-1]

                        # Getting DF_Index_List element
                        DF_Index_List.append(Line_2_Split[0])

                        Length_Line2 = len(Line_2_Split[1:])

                        Line_2_Split_1 = Line_2_Split[1:]

                        # Filling up Empty Column
                        if Length_Line2 < DF_ColumnName_List_Length:
                            Len_Difference = DF_ColumnName_List_Length - Length_Line2

                            for ii in range(Len_Difference):
                                Line_2_Split_1.append('NA')

                            # Getting DF_Data_List element
                            DF_Data_List.append(Line_2_Split_1)

                        else:
                            # Getting DF_Data_List element
                            DF_Data_List.append(Line_2_Split[1:])

                    else:

                        continue

                # Creating DF_Table
                DF_Table = pd.DataFrame(DF_Data_List, index=DF_Index_List, columns=DF_ColumnName_List)

                # Adding DF_Table to the Eio_OutputFile_Dict
                Eio_OutputFile_Dict[Category_Key] = DF_Table

            else:

                continue

        # Saving Eio_OutputFile_Dict as a .pickle File in Results Folder
        pickle.dump(Eio_OutputFile_Dict, open(os.path.join(Sim_IDFProcessedData_FolderPath,"Eio_OutputFile.pickle"), "wb"))

    elif download_selection == [1,2]:

        # Sorting variable names
        if Var_selection == 1:
            Simulation_VariableNames = [var.replace('_', ' ') for var in OUR_VARIABLE_LIST]

        elif Var_selection == 2:
            Simulation_VariableNames = your_vars

        # Loading the Edited IDF File
        epm_Edited_IDFFile = op.Epm.load(Results_IDF_FilePath)

        # Getting Output Variable from Edited IDF File
        OutputVariable_QuerySet = epm_Edited_IDFFile.Output_Variable.one()

        # FOR LOOP: For Each Variable in Simulation_VariableNames
        for OutputVariable_Name in Simulation_VariableNames:

            # Updating OutputVariable_QuerySet in the Special IDF File
            OutputVariable_QuerySet['key_value'] = '*'

            OutputVariable_QuerySet['reporting_frequency'] = Sim_OutputVariable_ReportingFrequency

            OutputVariable_QuerySet['variable_name'] = OutputVariable_Name

            # Saving Special IDF File
            epm_Edited_IDFFile.save(Results_IDF_FilePath)

            # Running Building Simulation to obtain current output variable
            op.simulate(Results_IDF_FilePath, Results_Weather_FilePath, base_dir_path = Sim_OutputFiles_FolderPath)

            # Moving Output Variable CSV file to Desired Folder
            Current_CSV_FilePath = os.path.join(Sim_OutputFiles_FolderPath, "eplusout.csv")

            New_OutputVariable_FileName = OutputVariable_Name.replace(' ','_') + '.csv'

            MoveTo_CSV_FilePath = os.path.join(Sim_IDFProcessedData_FolderPath, New_OutputVariable_FileName)

            try:

                shutil.move(Current_CSV_FilePath, MoveTo_CSV_FilePath)

            except:

                print("An exception occured")

            else:

                continue

        # =============================================================================
        # Convert and Save Output Variables .csv to.mat in Results Folder
        # =============================================================================

        # Getting all .csv Files paths from Sim_IDFProcessedData_FolderPath
        FileName_List = os.listdir(Sim_IDFProcessedData_FolderPath)

        # Initializing CSV_FileName_List
        CSV_FilePath_List = []

        # FOR LOOP: For each file in Sim_IDFProcessedData_FolderPath
        for file in FileName_List:

            # Check only .csv files
            if file.endswith('.csv'):

                # Appending .csv file paths to CSV_FilePath_List
                CSV_FilePath_List.append(os.path.join(Sim_IDFProcessedData_FolderPath,file))

        # Initializing IDF_OutputVariable_Dict
        IDF_OutputVariable_Dict = {}

        IDF_OutputVariable_ColumnName_List = []

        Counter_OutputVariable = 0

        # FOR LOOP: For Each .csv File in CSV_FilePath_List
        for file_path in CSV_FilePath_List:

            # Reading .csv file in dataframe
            Current_DF = pd.read_csv(file_path)

            # Getting CurrentDF_1
            if (Counter_OutputVariable == 0):

                # Keeping DateTime Column
                Current_DF_1 = Current_DF

            else:

                # Dropping DateTime Column
                Current_DF_1=Current_DF.drop(Current_DF.columns[[0]],axis=1)

            # Appending Column Names to IDF_OutputVariable_ColumnName_List
            for ColumnName in Current_DF_1.columns:

                IDF_OutputVariable_ColumnName_List.append(ColumnName)

            # Getting File Name
            FileName = file_path.split('\\')[-1].split('_.')[0]

            # Storing Current_DF in IDF_OutputVariable_Dict
            IDF_OutputVariable_Dict[FileName] = Current_DF

            # Incrementing Counter_OutputVariable
            Counter_OutputVariable = Counter_OutputVariable + 1

        # Creating and saving DateTime to IDF_OutputVariable_Dict
        DateTime_List = []

        DateTime_Column = Current_DF['Date/Time']

        for DateTime in DateTime_Column:

            DateTime_Split = DateTime.split(' ')

            Date_Split = DateTime_Split[1].split('/')

            Time_Split = DateTime_Split[3].split(':')

            # Converting all 24th hour to 0th hour as hour must be in 0..23
            if int(Time_Split[0]) == 24:
                Time_Split[0] = 00

            DateTime_List.append(datetime.datetime(int(IDF_FileYear),int(Date_Split[0]),int(Date_Split[1]),int(Time_Split[0]),int(Time_Split[1]),int(Time_Split[2])))

        IDF_OutputVariable_Dict['DateTime_List'] = DateTime_List

        pickle.dump(IDF_OutputVariable_Dict, open(os.path.join(Sim_IDFProcessedData_FolderPath,"IDF_OutputVariables_DictDF.pickle"), "wb"))

        # =============================================================================
        # Process .eio Output File and save in Results Folder
        # =============================================================================

        # Reading .eio Output File
        Eio_OutputFile_Path = os.path.join(Sim_OutputFiles_FolderPath,'eplusout.eio')

        # Initializing Eio_OutputFile_Dict
        Eio_OutputFile_Dict = {}

        with open(Eio_OutputFile_Path) as f:
            Eio_OutputFile_Lines = f.readlines()

        # Removing Intro Lines
        Eio_OutputFile_Lines = Eio_OutputFile_Lines[1:]

        # FOR LOOP: For each category in .eio File
        for Line_1 in Eio_OutputFile_Lines:

            # IF ELSE LOOP: To check category
            if (Line_1.find('!') >= 0):

                print(Line_1 + '\n')

                # Get the Key for the .eio File category
                Pattern_1 = "<(.*?)>"

                Category_Key = re.search(Pattern_1, Line_1).group(1)

                # Get the Column Names for the .eio File category
                DF_ColumnName_List = Line_1.split(',')[1:]

                # Removing the '\n From the Last Name
                DF_ColumnName_List[-1] = DF_ColumnName_List[-1].split('\n')[0]

                # Removing Empty Element
                if DF_ColumnName_List[-1] == ' ':
                    DF_ColumnName_List = DF_ColumnName_List[:-1]

                # Initializing DF_Index_List
                DF_Index_List = []

                # Initializing DF_Data_List
                DF_Data_List = []

                # FOR LOOP: For all elements of current .eio File category
                for Line_2 in Eio_OutputFile_Lines:

                    # IF ELSE LOOP: To check data row belongs to current Category
                    if ((Line_2.find('!') == -1) and (Line_2.find(Category_Key) >= 0)):

                        print(Line_2 + '\n')

                        DF_ColumnName_List_Length = len(DF_ColumnName_List)

                        # Split Line_2
                        Line_2_Split = Line_2.split(',')

                        # Removing the '\n From the Last Data
                        Line_2_Split[-1] = Line_2_Split[-1].split('\n')[0]

                        # Removing Empty Element
                        if Line_2_Split[-1] == ' ':
                            Line_2_Split = Line_2_Split[:-1]

                        # Getting DF_Index_List element
                        DF_Index_List.append(Line_2_Split[0])

                        Length_Line2 = len(Line_2_Split[1:])

                        Line_2_Split_1 = Line_2_Split[1:]

                        # Filling up Empty Column
                        if Length_Line2 < DF_ColumnName_List_Length:
                            Len_Difference = DF_ColumnName_List_Length - Length_Line2

                            for ii in range(Len_Difference):
                                Line_2_Split_1.append('NA')

                            # Getting DF_Data_List element
                            DF_Data_List.append(Line_2_Split_1)

                        else:
                            # Getting DF_Data_List element
                            DF_Data_List.append(Line_2_Split[1:])

                    else:

                        continue

                # Creating DF_Table
                DF_Table = pd.DataFrame(DF_Data_List, index=DF_Index_List, columns=DF_ColumnName_List)

                # Adding DF_Table to the Eio_OutputFile_Dict
                Eio_OutputFile_Dict[Category_Key] = DF_Table

            else:

                continue

        # Saving Eio_OutputFile_Dict as a .pickle File in Results Folder
        pickle.dump(Eio_OutputFile_Dict, open(os.path.join(Sim_IDFProcessedData_FolderPath,"Eio_OutputFile.pickle"), "wb"))

        pickle_list = [os.path.join(Sim_IDFProcessedData_FolderPath,"IDF_OutputVariables_DictDF.pickle"), os.path.join(Sim_IDFProcessedData_FolderPath,"Eio_OutputFile.pickle")]
        AppFuncs.compress(pickle_list, Sim_IDFProcessedData_FolderPath)

    button_text = "Data Generated"

    return button_text

@app.callback(
    Output(component_id = 'EPGen_Download_DownloadFiles', component_property = 'data'),
    State(component_id = 'download_selection', component_property = 'value'),
    Input(component_id = 'EPGen_Button_DownloadFiles', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_DownloadFiles_Interaction(download_selection, n_clicks):

    Sim_IDFProcessedData_FolderName = 'Sim_ProcessedData'
    Sim_IDFProcessedData_FolderPath = os.path.join(SIMULATION_FOLDERPATH, "Final_run_folder", Sim_IDFProcessedData_FolderName)

    for item in os.listdir(Sim_IDFProcessedData_FolderPath):
        if download_selection == [1] or download_selection == [2]:
            if item.endswith(".pickle"):
                download_path = os.path.join(Sim_IDFProcessedData_FolderPath,item)
        elif download_selection == [1,2]:
            if item.endswith(".zip"):
                download_path = os.path.join(Sim_IDFProcessedData_FolderPath,item)
    return dcc.send_file(download_path)

@app.callback(
    Output(component_id = 'EPGen_Button_EndSession', component_property = 'children'),
    Input(component_id = 'EPGen_Button_EndSession', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_EndSession_Interaction(n_clicks):

    for directory in os.listdir(WORKSPACE_DIRECTORY):

        shutil.rmtree(os.path.join(WORKSPACE_DIRECTORY, directory))

    return "Session Completed"

@app.callback(
    Output(component_id = 'EPAgg_Div_UploadFiles', component_property = 'hidden'),
    Output(component_id = 'EPAgg_Div_AggregationVariables', component_property = 'hidden'),
    Input(component_id = 'EPAgg_RadioButton_InputSelection', component_property = 'value'),
    prevent_initial_call = True)
def EPAgg_RadioButton_InputSelection_Interaction(value):

    if value == 1:

        upload_div = True
        variable_div = False

    elif value == 2:

        upload_div = False
        variable_div = False

    else:

        upload_div = True
        variable_div = True

    return upload_div, variable_div

@app.callback(
    Output(component_id = 'EPAgg_Upload_Pickle', component_property = 'children'),
    Input(component_id = 'EPAgg_Upload_Pickle', component_property = 'filename'),
    State(component_id = 'EPAgg_Upload_Pickle', component_property = 'contents'),
    prevent_initial_call = False)
def EPAgg_Upload_Pickle_Interaction(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file(filename, content, UPLOAD_DIRECTORY_AGG_PICKLE)
        message = filename + ' uploaded successfully'

    else:
        message = 'Upload Pickled Variable file'

    return message

@app.callback(
    Output(component_id = 'EPAgg_Upload_EIO', component_property = 'children'),
    Input(component_id = 'EPAgg_Upload_EIO', component_property = 'filename'),
    State(component_id = 'EPAgg_Upload_EIO', component_property = 'contents'),
    prevent_initial_call = False)
def EPAgg_Upload_EIO_Interaction(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file(filename, content, UPLOAD_DIRECTORY_AGG_EIO)
        message = filename + ' uploaded successfully'

    else:
        message = 'Upload EIO file'

    return message

@app.callback(
    Output(component_id = 'EPAgg_Div_AggregationDetails', component_property = 'hidden'),
    Input(component_id = 'EPAgg_RadioButton_AggregationVariables', component_property = 'value'),
    Input(component_id = 'EPAgg_DropDown_CustomVariables', component_property = 'value'),
    prevent_initial_call = True)
def EPAgg_DropDown_AggregationVariables_Interaction(selection, value):

    if selection == 1:

        div = False

    elif selection == 2:

        div = True

        if value != None:

            div = False

    else:

        div = True

    return div

@app.callback(
    Output(component_id = 'EPAgg_DropDown_PreselectedVariables', component_property = 'options'),
    Output(component_id = 'EPAgg_DropDown_CustomVariables', component_property = 'options'),
    Output(component_id = 'EPAgg_DropDown_ZoneList', component_property = 'options'),
    State(component_id = 'EPAgg_RadioButton_InputSelection', component_property = 'value'),
    Input(component_id = 'EPAgg_RadioButton_AggregationVariables', component_property = 'value'),
    prevent_initial_call = True)
def EPAgg_RadioButton_AggregationVariables_Interaction(InputSelection, VariableSelection):

    # Creating Aggregation FolderPath
    Aggregation_FolderPath = os.path.join(WORKSPACE_DIRECTORY, 'Aggregation')

    if os.path.isdir(Aggregation_FolderPath):

        z = 0

    else:

        os.mkdir(Aggregation_FolderPath)

    # Continue session -> copying files from previous session
    if InputSelection == 1:

        # For testing purposes
        SIMULATION_FOLDERPATH = os.path.join(WORKSPACE_DIRECTORY, 'sim1')

        # Copying pickle file & eio file from previous session
        Sim_IDFProcessedData_FolderName = 'Sim_ProcessedData'
        Sim_IDFProcessedData_FolderPath = os.path.join(SIMULATION_FOLDERPATH, "Final_run_folder", Sim_IDFProcessedData_FolderName)

        for item in os.listdir(Sim_IDFProcessedData_FolderPath):

            if item.endswith(".pickle"):

                shutil.copy(os.path.join(Sim_IDFProcessedData_FolderPath,item), Aggregation_FolderPath)

    # Upload files -> copying uploaded files and renaming
    elif InputSelection == 2:

        for item in os.listdir(UPLOAD_DIRECTORY_AGG_PICKLE):

            shutil.copy(os.path.join(UPLOAD_DIRECTORY_AGG_PICKLE,item), os.path.join(Aggregation_FolderPath,'IDF_OutputVariables_DictDF.pickle'))

        for item in os.listdir(UPLOAD_DIRECTORY_AGG_EIO):

            shutil.copy(os.path.join(UPLOAD_DIRECTORY_AGG_EIO,item), os.path.join(Aggregation_FolderPath,'Eio_OutputFile.pickle'))

    if VariableSelection == 1:

        modified_OUR_VARIABLE_LIST = []

        for item in OUR_VARIABLE_LIST:
            # Remove the last underscore
            item = item.rstrip('_')
            # Replace remaining underscores with spaces
            item = item.replace('_', ' ')
            modified_OUR_VARIABLE_LIST.append(item)

        modified_OUR_VARIABLE_LIST.sort()

        pre_list = modified_OUR_VARIABLE_LIST

        custom_list = []

    elif VariableSelection == 2:

        # Get Required Files from Sim_ProcessedData_FolderPath
        IDF_OutputVariable_Dict_file = open(os.path.join(Aggregation_FolderPath,'IDF_OutputVariables_DictDF.pickle'),"rb")

        IDF_OutputVariable_Dict = pickle.load(IDF_OutputVariable_Dict_file)

        custom_list = list(IDF_OutputVariable_Dict.keys())

        custom_list.remove('DateTime_List')

        pre_list = []

    Eio_OutputFile_Dict_file = open(os.path.join(Aggregation_FolderPath,'Eio_OutputFile.pickle'),"rb")

    Eio_OutputFile_Dict = pickle.load(Eio_OutputFile_Dict_file)

    zone_list = list(Eio_OutputFile_Dict['Zone Information'][Eio_OutputFile_Dict['Zone Information']['  Part of Total Building Area']  == 'Yes']['Zone Name'])

    return pre_list, custom_list, zone_list

@app.callback(
    Output(component_id = 'EPAgg_Div_FinalDownload', component_property = 'hidden'),
    Input(component_id = 'EPAgg_DropDown_TypeOfAggregation', component_property = 'value'),
    prevent_initial_call = True)
def EPAgg_DropDown_TypeOfAggregation_Interaction(value):

    if value != None:

        div = False

    else:

        div = True

    return div

@app.callback(
    Output(component_id = 'EPAgg_Button_Aggregate', component_property = 'children'),
    State(component_id = 'EPAgg_RadioButton_AggregationVariables', component_property = 'value'),
    State(component_id = 'EPAgg_DropDown_CustomVariables', component_property = 'value'),
    State(component_id = 'EPAgg_RadioButton_AggregateTo', component_property = 'value'),
    State(component_id = 'EPAgg_DropDown_CustomAggregationZoneList', component_property = 'value'),
    State(component_id = 'EPAgg_DropDown_TypeOfAggregation', component_property = 'value'),
    Input(component_id = 'EPAgg_Button_Aggregate', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPAgg_Button_Aggregate_Interaction(variable_selection, custom_variables, aggregate_to, custom_zone_list, Type_Aggregation, n_clicks):

    # Retrieing Aggregation Folder Path
    Aggregation_FolderPath = os.path.join(WORKSPACE_DIRECTORY, 'Aggregation')

    # Get Required Files from Sim_ProcessedData_FolderPath
    IDF_OutputVariable_Dict_file = open(os.path.join(Aggregation_FolderPath,'IDF_OutputVariables_DictDF.pickle'),"rb")

    IDF_OutputVariable_Dict = pickle.load(IDF_OutputVariable_Dict_file)

    Eio_OutputFile_Dict_file = open(os.path.join(Aggregation_FolderPath,'Eio_OutputFile.pickle'),"rb")

    Eio_OutputFile_Dict = pickle.load(Eio_OutputFile_Dict_file)

    # Getting variable selection for aggregation
    if variable_selection == 1:  # Pre selected variables

        selected_variable_list = OUR_VARIABLE_LIST

    elif variable_selection == 2:  # Custom variables

        selected_variable_list = custom_variables

    # Getting Aggregation Zone list
    if aggregate_to == 1:  # Aggregate to one

        Aggregation_Zone_List_1 = list(Eio_OutputFile_Dict['Zone Information'][Eio_OutputFile_Dict['Zone Information']['  Part of Total Building Area']  == 'Yes']['Zone Name'])

        Aggregation_Zone_List_2 = [x.strip(" ") for x in Aggregation_Zone_List_1]

        Aggregation_Zone_List = [Aggregation_Zone_List_2]

    elif aggregate_to == 2:   # Custom Aggregation

        Aggregation_Zone_List = []

        custom_zone_list_semicolon = custom_zone_list.split(';')

        Aggregation_Zones_len = len(custom_zone_list_semicolon)

        for Current_Zone_List in custom_zone_list_semicolon:  # For each zone list to be aggregated

            Aggregation_Zone_List.append(Current_Zone_List.split(','))

    Aggregation_VariableNames_List = selected_variable_list

    Aggregation_Zone_NameStem = 'Aggregation_Zone'

    SystemNode_Name = 'DIRECT AIR INLET NODE'

    # Implementing Aggregation Code


    # Getting DateTime_List
    DateTime_List = IDF_OutputVariable_Dict['DateTime_List']


    # =============================================================================
    # Creating Unique Zone Name List and Associated Areas and Volume Dicts
    # =============================================================================

    # Creating Unique List of Zones
    Total_Zone_List = []

    # FOR LOOP: For each element of Aggregation_Zone_List
    for CurrentZone_List in Aggregation_Zone_List:

        # FOR LOOP: For each element of CurrentZone_List
        for CurrentZone in CurrentZone_List:

            # Appending CurrentZone to Total_Zone_List
            Total_Zone_List.append(CurrentZone)

    # Creating Unique Zone List
    Unique_Zone_List = list(set(Total_Zone_List))

    # IF ELSE LOOP: For cheking Type_Aggregation
    if (Type_Aggregation == 1): # Normal Aggregation

        # Do nothing
        Do_Nothing = 0

    elif (Type_Aggregation == 2): # Weighted Area Aggregation

        # Initializing Unique_Zone_Area_Dict and Unique_Zone_Volume_Dict
        Unique_Zone_Area_Dict = {}

        # Getiing Zone Area and Volumes from Eio_OutputFile_Dict

        # FOR LOOP: For each element of Unique_Zone_List
        for Unique_Zone in Unique_Zone_List:

            Unique_Zone_Area_Dict[Unique_Zone] = float(Eio_OutputFile_Dict['Zone Information'].query('`Zone Name` == Unique_Zone')['Floor Area {m2}'])

        # Creating Zone_TotalArea_List
        Zone_TotalArea_List = []

        # FOR LOOP: For each Element in Aggregation_Zone_List
        for Aggregation_Zone_List1 in Aggregation_Zone_List:

            # Initializing TotalArea
            TotalArea = 0

            # FOR LOOP: For each Element in Aggregation_Zone_List1
            for element in Aggregation_Zone_List1:

                # Summing Up Zone Area
                TotalArea = TotalArea + Unique_Zone_Area_Dict[element]

            # Appending Zone_TotalArea_List
            Zone_TotalArea_List.append(TotalArea)

    elif (Type_Aggregation == 3): # Weighted Volume Aggregation

        # Initializing Unique_Zone_Area_Dict and Unique_Zone_Volume_Dict
        Unique_Zone_Volume_Dict = {}

        # Getiing Zone Area and Volumes from Eio_OutputFile_Dict

        # FOR LOOP: For each element of Unique_Zone_List
        for Unique_Zone in Unique_Zone_List:

            Unique_Zone_Volume_Dict[Unique_Zone] = float(Eio_OutputFile_Dict['Zone Information'].query('`Zone Name` == Unique_Zone')['Volume {m3}'])

        # Creating Zone_TotalVolume_List
        Zone_TotalVolume_List = []

        # FOR LOOP: For each Element in Aggregation_Zone_List
        for Aggregation_Zone_List1 in Aggregation_Zone_List:

            # Initializing TotalArea
            TotalVolume = 0

            # FOR LOOP: For each Element in Aggregation_Zone_List1
            for element in Aggregation_Zone_List1:

                # Summing Up Zone Area
                TotalVolume = TotalVolume + Unique_Zone_Volume_Dict[element]

            # Appending Zone_TotalArea_List
            Zone_TotalVolume_List.append(TotalVolume)


    # =============================================================================
    # Creating Aggregation_DF with relevant Columns to hold Aggregated Data
    # =============================================================================

    # Creating Equipment List
    Equipment_List = ['People', 'Lights', 'ElectricEquipment', 'GasEquipment', 'OtherEquipment', 'HotWaterEquipment', 'SteamEquipment']

    # Initializing Aggregation_DF
    Aggregation_DF = pd.DataFrame()

    # FOR LOOP: For each Variable Name in Aggregation_VariableNames_List
    for key in Aggregation_VariableNames_List:

        # IF LOOP: For the Variable Name Schedule_Value_
        if (key == 'Schedule_Value_'): # Create Schedule Columns which are needed

            # FOR LOOP: For each element in Equipment_List
            for element in Equipment_List:

                # Creating Current_EIO_Dict_Key
                Current_EIO_Dict_Key = element + ' ' + 'Internal Gains Nominal'

                # IF LOOP: To check if Current_EIO_Dict_Key is present in Eio_OutputFile_Dict
                if (Current_EIO_Dict_Key in Eio_OutputFile_Dict): # Key present in Eio_OutputFile_Dict

                    # Creating key1 for column Name
                    key1 = key + element

                    # Initializing Aggregation_Dict with None
                    Aggregation_DF[key1] = None

        else: # For all other Columns

            # Initializing Aggregation_Dict with None
            Aggregation_DF[key] = None

    # Initializing Aggregation_DF_Equipment
    Aggregation_DF_Equipment = pd.DataFrame()

    # FOR LOOP: For each element in Equipment_List
    for element in Equipment_List:

        # Creating Current_EIO_Dict_Key
        Current_EIO_Dict_Key = element + ' ' + 'Internal Gains Nominal'

        # IF LOOP: To check if Current_EIO_Dict_Key is present in Eio_OutputFile_Dict
        if (Current_EIO_Dict_Key in Eio_OutputFile_Dict): # Key present in Eio_OutputFile_Dict

            # Creating key1 for column Name
            key1 =  element + '_Level'

            # Initializing Aggregation_Dict with None
            Aggregation_DF_Equipment[key1] = None


    # =============================================================================
    # Creating Aggregation_Dict to hold Aggregated Data
    # =============================================================================

    # Initializing Aggregation_Dict
    Aggregation_Dict = {'DateTime_List': DateTime_List}

    # Initializing Counter
    Counter = 0

    # FOR LOOP: For each element in Aggregation_Zone_List
    for element in Aggregation_Zone_List:

        # Incrementing Counter
        Counter = Counter + 1

        # Creating Aggregated Zone name 1 : For the Aggregated Time Series
        Aggregated_Zone_Name_1 = Aggregation_Zone_NameStem + "_" + str(Counter)

        # Creating Aggregated Zone name 2 : For the Aggregated Equipment
        Aggregated_Zone_Name_2 = Aggregation_Zone_NameStem + "_Equipment_" + str(Counter)

        # Appending empty Aggregation_DF to Aggregation_Dict
        Aggregation_Dict[Aggregated_Zone_Name_1] = copy.deepcopy(Aggregation_DF)

        Aggregation_Dict[Aggregated_Zone_Name_2] = copy.deepcopy(Aggregation_DF_Equipment)


    # =============================================================================
    # Creating Aggregated Data
    # =============================================================================

    # Initializing Counter
    Counter = 0

    # FOR LOOP: For each Aggregated Zone in Aggregation_Zone_List
    for Current_Aggregated_Zone_List in Aggregation_Zone_List:

        # Incrementing Counter
        Counter = Counter + 1

        # Creating Aggregated Zone name
        Aggregated_Zone_Name_1 = Aggregation_Zone_NameStem + "_" + str(Counter)

        Aggregated_Zone_Name_2 = Aggregation_Zone_NameStem + "_Equipment_" + str(Counter)

        # FOR LOOP: For each Aggregation_VariableName in Aggregation_VariableNames_List
        for Current_Aggregation_VariableName in Aggregation_Dict[Aggregated_Zone_Name_1].columns:

            # Getting Current_Aggregation_Variable Type
            Current_Aggregation_Variable_Type = Current_Aggregation_VariableName.split('_')[0]

            # Aggregation Based on Current_Aggregation_Variable_Type
            if (Current_Aggregation_Variable_Type == 'Site' or Current_Aggregation_Variable_Type == 'Facility'): # Site

                # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                Current_Aggregation_Variable = IDF_OutputVariable_Dict[Current_Aggregation_VariableName[:-1]]

                # Filling Aggregation_Dict with Current_Aggregation_Variable
                Aggregation_Dict[Aggregated_Zone_Name_1][Current_Aggregation_VariableName] = Current_Aggregation_Variable.iloc[:, [1]]

            elif (Current_Aggregation_Variable_Type == 'Zone'): # Zone

                if Current_Aggregation_VariableName[:-1] in IDF_OutputVariable_Dict.keys():
                    # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                    Current_Aggregation_Variable = IDF_OutputVariable_Dict[Current_Aggregation_VariableName[:-1]]

                    # Getting Dataframe subset based on Current_Aggregated_Zone_List
                    Current_DF_Cols_Desired = []

                    #  Getting Current_Aggregation_Variable_ColName_List
                    Current_Aggregation_Variable_ColName_List = Current_Aggregation_Variable.columns

                    # FOR LOOP: For each element in Current_Aggregated_Zone_List
                    for ColName1 in Current_Aggregated_Zone_List:

                        # FOR LOOP: For each element in Current_Aggregation_Variable_ColName_List
                        for ColName2 in Current_Aggregation_Variable_ColName_List:

                            # IF LOOP: For checking presence of ColName1 in ColName2
                            if (ColName2.find(ColName1) >= 0): # ColName1 present in ColName2

                                # Appending ColName2 to Current_DF_Cols_Desired
                                Current_DF_Cols_Desired.append(ColName2)

                                # IF ELSE LOOP: For Type_Aggregation
                                if (Type_Aggregation == 1): # Normal Aggregation

                                    # Do Nothing
                                    Do_Nothing = 0

                                elif (Type_Aggregation == 2): # Weighted Area Aggregation

                                    # Aggregate by Area
                                    Current_Aggregation_Variable[ColName2] = Unique_Zone_Area_Dict[ColName1] * Current_Aggregation_Variable[ColName2]

                                elif (Type_Aggregation == 3): # Weighted Volume Aggregation

                                    # Aggregate by Volume
                                    Current_Aggregation_Variable[ColName2] = Unique_Zone_Volume_Dict[ColName1] * Current_Aggregation_Variable[ColName2]

                    # IF ELSE LOOP: For aggregating according to Type_Aggregation and storing in Aggregation_Dict
                    if (Type_Aggregation == 1): # Normal Aggregation

                        # Filling Aggregation_Dict with Current_Aggregation_Variable
                        Aggregation_Dict[Aggregated_Zone_Name_1][Current_Aggregation_VariableName] = Current_Aggregation_Variable[Current_DF_Cols_Desired].mean(1)

                    elif (Type_Aggregation == 2): # Weighted Area Aggregation

                        # Filling Aggregation_Dict with Current_Aggregation_Variable
                        Aggregation_Dict[Aggregated_Zone_Name_1][Current_Aggregation_VariableName]  = (Current_Aggregation_Variable[Current_DF_Cols_Desired].sum(1))/(Zone_TotalArea_List[Counter])

                    elif (Type_Aggregation == 3): # Weighted Volume Aggregation

                        # Filling Aggregation_Dict with Current_Aggregation_Variable
                        Aggregation_Dict[Aggregated_Zone_Name_1][Current_Aggregation_VariableName]  = (Current_Aggregation_Variable[Current_DF_Cols_Desired].sum(1))/(Zone_TotalVolume_List[Counter])

            elif (Current_Aggregation_Variable_Type == 'Surface'): # Surface

                # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                Current_Aggregation_Variable = IDF_OutputVariable_Dict[Current_Aggregation_VariableName[:-1]]

                # Getting Dataframe subset based on Current_Aggregated_Zone_List
                Current_DF_Cols_Desired = []

                # Initializing Current_DF
                Current_DF = pd.DataFrame()

                #  Getting Current_Aggregation_Variable_ColName_List
                Current_Aggregation_Variable_ColName_List = Current_Aggregation_Variable.columns

                # FOR LOOP: For each element in Current_Aggregated_Zone_List
                for ColName1 in Current_Aggregated_Zone_List:

                    # FOR LOOP: For each element in Current_Aggregation_Variable_ColName_List
                    for ColName2 in Current_Aggregation_Variable_ColName_List:

                        # IF LOOP: For checking presence of ColName1 in ColName2
                        if (ColName2.find(ColName1) >= 0): # ColName1 present in ColName2

                            # Appending ColName2 to Current_DF_Cols_Desired
                            Current_DF_Cols_Desired.append(ColName2)

                            # IF ELSE LOOP: For Type_Aggregation
                            if (Type_Aggregation == 1): # Normal Aggregation

                                # Do Nothing
                                Do_Nothing = 0

                            elif (Type_Aggregation == 2): # Weighted Area Aggregation

                                # Aggregate by Area
                                Current_Aggregation_Variable[ColName2] = Unique_Zone_Area_Dict[ColName1] * Current_Aggregation_Variable[ColName2]

                            elif (Type_Aggregation == 3): # Weighted Volume Aggregation

                                # Aggregate by Volume
                                Current_Aggregation_Variable[ColName2] = Unique_Zone_Volume_Dict[ColName1] * Current_Aggregation_Variable[ColName2]

                    # IF ELSE LOOP: For filling Up Current_DF according to Current_Aggregation_VariableName
                    if ((Current_Aggregation_VariableName.find('Heat') >= 0) or (Current_Aggregation_VariableName.find('Gain') >= 0) or (Current_Aggregation_VariableName.find('Rate') >= 0) or (Current_Aggregation_VariableName.find('Power') >= 0) or (Current_Aggregation_VariableName.find('Energy') >= 0)): # Its an additive Variable

                        # Adding Column to Current_DF
                        Current_DF[ColName1] = Current_Aggregation_Variable[Current_DF_Cols_Desired].sum(1)

                    else: # It's a mean Variable

                        # Addding Column to Current_DF
                        Current_DF[ColName1] = Current_Aggregation_Variable[Current_DF_Cols_Desired].mean(1)

                # IF ELSE LOOP: For aggregating according to Type_Aggregation and storing in Aggregation_Dict
                if (Type_Aggregation == 1): # Normal Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][Current_Aggregation_VariableName]  = Current_DF[Current_Aggregated_Zone_List].mean(1)

                elif (Type_Aggregation == 2): # Weighted Area Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][Current_Aggregation_VariableName]  = (Current_DF[Current_Aggregated_Zone_List].sum(1))/(Zone_TotalArea_List[Counter])

                elif (Type_Aggregation == 3): # Weighted Volume Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][Current_Aggregation_VariableName]  = (Current_DF[Current_Aggregated_Zone_List].sum(1))/(Zone_TotalVolume_List[Counter])


            elif (Current_Aggregation_Variable_Type == 'System'): # System Node

                # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                Current_Aggregation_Variable = IDF_OutputVariable_Dict[Current_Aggregation_VariableName[:-1]]

                # Getting Dataframe subset based on Current_Aggregated_Zone_List
                Current_DF_Cols_Desired = []

                #  Getting Current_Aggregation_Variable_ColName_List
                Current_Aggregation_Variable_ColName_List = Current_Aggregation_Variable.columns

                # FOR LOOP: For each element in Current_Aggregated_Zone_List
                for ColName1 in Current_Aggregated_Zone_List:

                    # FOR LOOP: For each element in Current_Aggregation_Variable_ColName_List
                    for ColName2 in Current_Aggregation_Variable_ColName_List:

                        # IF LOOP: For checking presence of ColName1 in ColName2
                        if ((ColName2.find(ColName1) >= 0) and (ColName2.find(SystemNode_Name) >= 0)): # ColName1 present in ColName2

                            # Appending ColName2 to Current_DF_Cols_Desired
                            Current_DF_Cols_Desired.append(ColName2)

                            # IF ELSE LOOP: For Type_Aggregation
                            if (Type_Aggregation == 1): # Normal Aggregation

                                # Do Nothing
                                Do_Nothing = 0

                            elif (Type_Aggregation == 2): # Weighted Area Aggregation

                                # Aggregate by Area
                                Current_Aggregation_Variable[ColName2] = Unique_Zone_Area_Dict[ColName1] * Current_Aggregation_Variable[ColName2]

                            elif (Type_Aggregation == 3): # Weighted Volume Aggregation

                                # Aggregate by Volume
                                Current_Aggregation_Variable[ColName2] = Unique_Zone_Volume_Dict[ColName1] * Current_Aggregation_Variable[ColName2]

                # IF ELSE LOOP: For aggregating according to Type_Aggregation and storing in Aggregation_Dict
                if (Type_Aggregation == 1): # Normal Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][Current_Aggregation_VariableName]  = Current_Aggregation_Variable[Current_DF_Cols_Desired].mean(1)

                elif (Type_Aggregation == 2): # Weighted Area Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][Current_Aggregation_VariableName]  = (Current_Aggregation_Variable[Current_DF_Cols_Desired].sum(1))/(Zone_TotalArea_List[Counter])

                elif (Type_Aggregation == 3): # Weighted Volume Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][Current_Aggregation_VariableName]  = (Current_Aggregation_Variable[Current_DF_Cols_Desired].sum(1))/(Zone_TotalVolume_List[Counter])

            elif (Current_Aggregation_Variable_Type == 'Schedule'): # Schedule

                # Getting Dataframe subset based on Current_Aggregated_Zone_List
                Current_DF_Cols_Desired = []

                # Create a CurrentLevel_List
                CurrentLevel_List = []

                # Creating Current_VariableName_1
                Current_Aggregation_VariableName_1 = Current_Aggregation_VariableName.split('_')[0] + '_' + Current_Aggregation_VariableName.split('_')[1]

                # Get Current_Element
                Current_Element = Current_Aggregation_VariableName.split('_')[2]

                # Creating Current_EIO_Dict_Key
                Current_EIO_Dict_Key = Current_Element + ' ' + 'Internal Gains Nominal'

                # Creating Current_EIO_Dict_Key
                Current_EIO_Dict_Key_Level = Current_Element + '_' + 'Level'

                # IF ELSE LOOP: For creating Current_EIO_Dict_Key_Level_ColName based on Current_Element
                if (Current_Element == 'People'): # People

                    Current_EIO_Dict_Key_Level_ColName = 'Number of People {}'

                elif (Current_Element == 'Lights'): # Lights

                    Current_EIO_Dict_Key_Level_ColName = 'Lighting Level {W}'

                else: # ElectricEquipment, OtherEquipment, HotWaterEquipment, SteamEquipment

                    Current_EIO_Dict_Key_Level_ColName = 'Equipment Level {W}'

                # Getting Current_EIO_Dict_DF
                Current_EIO_Dict_DF = Eio_OutputFile_Dict[Current_EIO_Dict_Key]

                # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                Current_Aggregation_Variable = IDF_OutputVariable_Dict[Current_Aggregation_VariableName_1]

                #  Getting Current_Aggregation_Variable_ColName_List
                Current_Aggregation_Variable_ColName_List = Current_Aggregation_Variable.columns

                # FOR LOOP: For each element in Current_Aggregated_Zone_List
                for ColName1 in Current_Aggregated_Zone_List:

                    # Getting ColName2 from the 'Schedule Name' Column of Current_EIO_Dict_DF
                    ColName2 = str(Current_EIO_Dict_DF[Current_EIO_Dict_DF['Zone Name'] == ColName1]['Schedule Name'].iloc[0])

                    # Appending ColName2 to Current_DF_Cols_Desired
                    Current_DF_Cols_Desired.append(ColName2)

                    # Getting Equipment Level
                    Current_EquipmentLevel = float(Current_EIO_Dict_DF[Current_EIO_Dict_DF['Zone Name'] == ColName1][Current_EIO_Dict_Key_Level_ColName].iloc[0])

                    # Appending Current_EquipmentLevel to CurrentLevel_List
                    CurrentLevel_List.append(Current_EquipmentLevel)

                # FOR LOOP: Getting Corrected Current_DF_Cols_Desired
                Current_DF_Cols_Desired_Corrected = []

                for ColName3 in Current_DF_Cols_Desired:
                    for ColName4 in Current_Aggregation_Variable.columns:
                        if (ColName4.find(ColName3) >= 0):
                            Current_DF_Cols_Desired_Corrected.append(ColName4)

                # Filling Aggregation_Dict with Current_Aggregation_Variable and Current_EIO_Dict_Key_Level
                Aggregation_Dict[Aggregated_Zone_Name_1][Current_Aggregation_VariableName] = Current_Aggregation_Variable[Current_DF_Cols_Desired_Corrected].mean(1)

                Aggregation_Dict[Aggregated_Zone_Name_2][Current_EIO_Dict_Key_Level] = pd.DataFrame(np.array([sum(CurrentLevel_List)/len(CurrentLevel_List)]))
            # else: # Any other Variable

    # Creating Results Folder
    results_path = os.path.join(Aggregation_FolderPath, "Results")

    if os.path.isdir(results_path):
        z = 0
    else:
        os.mkdir(results_path)

    pickle.dump(Aggregation_Dict, open(os.path.join(results_path,'Aggregation_Dictionary.pickle'), "wb"))

    return "Aggregation Completed"

@app.callback(
    Output(component_id = 'EPAgg_Download_DownloadFiles', component_property = 'data'),
    Input(component_id = 'EPAgg_Button_Download', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPAgg_Button_Download_Interaction(n_clicks):

    results_path = os.path.join(WORKSPACE_DIRECTORY, "Aggregation", "Results")

    for item in os.listdir(results_path):
        if item.endswith(".pickle"):
            download_path = os.path.join(results_path,item)
    return dcc.send_file(download_path)

@app.callback(
    Output(component_id = 'EPVis_Div_Datatobeselected', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'EPVis_Div_UploadData', component_property = 'hidden'),
    Input(component_id = 'EPVis_RadioButton_DataSource', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_RadioButton_DataSource_Interaction(data_source):

    if data_source == 1:
        data_selection = False
        upload_data = True

    elif data_source == 2:
        data_selection = True
        upload_data = False

    else:
        data_selection = True
        upload_data = True

    return data_selection, upload_data

@app.callback(
    Output(component_id = 'EPVis_Upload_GeneratedData', component_property = 'children'),
    Input(component_id = 'EPVis_Upload_GeneratedData', component_property = 'filename'),
    State(component_id = 'EPVis_Upload_GeneratedData', component_property = 'contents'),
    prevent_initial_call = False)
def EPVis_Upload_GeneratedData_Interaction(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file('Generated.pickle', content, UPLOAD_DIRECTORY_VIS)
        message = filename + ' uploaded successfully'

    else:
        message = 'Drag and Drop or Select Files for Generated Data'

    return message

@app.callback(
    Output(component_id = 'EPVis_Upload_AggregatedData', component_property = 'children'),
    Output(component_id = 'EPVis_Div_Datatobeselected', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'EPVis_Upload_AggregatedData', component_property = 'filename'),
    State(component_id = 'EPVis_Upload_AggregatedData', component_property = 'contents'),
    prevent_initial_call = True)
def EPVis_Upload_AggregatedData_Interaction(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file('Aggregated.pickle', content, UPLOAD_DIRECTORY_VIS)
        message = filename + ' uploaded successfully'
        data_selection = False
    else:
        message = 'Drag and Drop or Select Files for Aggregated Data'
        data_selection = True

    return message, data_selection

@app.callback(
    Output(component_id = 'EPVis_Div_DateRangeUploadedFile', component_property = 'hidden'),
    Output(component_id = 'EPVis_Div_DateRangeVis', component_property = 'hidden'),
    Output(component_id = 'EPVis_Div_SelectVariableGenerateData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Div_SelectVariableAggregateData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_DistGeneratedData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_DistAggregatedData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_DistBothData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Row_GeneratedDataDetails', component_property = 'hidden'),
    Output(component_id = 'EPVis_Row_AggregatedDataDetails', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_ScatterGeneratedData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_ScatterAggregatedData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_ScatterBothData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_TimeGeneratedData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_TimeAggregatedData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_TimeBothData', component_property = 'hidden'),
    Output(component_id = 'EPVis_DatePickerRange_UploadedFile', component_property = 'min_date_allowed'),
    Output(component_id = 'EPVis_DatePickerRange_UploadedFile', component_property = 'max_date_allowed'),
    Output(component_id = 'EPVis_DatePickerRange_Visualization', component_property = 'min_date_allowed'),
    Output(component_id = 'EPVis_DatePickerRange_Visualization', component_property = 'max_date_allowed'),
    Output(component_id = 'EPVis_DatePickerRange_UploadedFile', component_property = 'start_date'),
    Output(component_id = 'EPVis_DatePickerRange_UploadedFile', component_property = 'end_date'),
    Output(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'options'),
    Output(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'options'),

    State(component_id = 'EPVis_RadioButton_DataSource', component_property = 'value'),
    Input(component_id = 'EPVis_RadioButton_DataToBeSelected', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_Radio_DataToBeSelected_Interaction(InputSelection, selection):
    if selection == 1: # Generate Data
        date_range1 = False
        date_range2 = False
        var_gendata = False
        var_aggrdata = True
        button_dist_gen = False
        button_dist_agg = True
        button_dist_both = True
        mean_gen = False
        mean_agg = True
        button_scat_gen = False
        button_scat_agg = True
        button_scat_both = True
        button_time_gen = False
        button_time_agg = True
        button_time_both = True
    elif selection == 2: # Aggregated Data
        date_range1 = False
        date_range2 = False
        var_gendata = True
        var_aggrdata = False
        button_dist_gen = True
        button_dist_agg = False
        button_dist_both = True
        mean_gen = True
        mean_agg = False
        button_scat_gen = True
        button_scat_agg = False
        button_scat_both = True
        button_time_gen = True
        button_time_agg = False
        button_time_both = True
    elif selection == 3: # Both
        date_range1 = False
        date_range2 = False
        var_gendata = False
        var_aggrdata = False
        button_dist_gen = False
        button_dist_agg = False
        button_dist_both = False
        mean_gen = False
        mean_agg = False
        button_scat_gen = False
        button_scat_agg = False
        button_scat_both = False
        button_time_gen = False
        button_time_agg = False
        button_time_both = False
    else:
        date_range1 = True
        date_range2 = True
        var_gendata = True
        var_aggrdata = True
        button_dist_gen = True
        button_dist_agg = True
        button_dist_both = True
        mean_gen = True
        mean_agg = True
        button_scat_gen = True
        button_scat_agg = True
        button_scat_both = True
        button_time_gen = True
        button_time_agg = True
        button_time_both = True

    # Creating Visualization FolderPath
    Visualization_FolderPath = os.path.join(WORKSPACE_DIRECTORY, 'Visualization')

    if os.path.isdir(Visualization_FolderPath):

        z = 0

    else:

        os.mkdir(Visualization_FolderPath)

    # Continue session -> copying files from previous session
    if InputSelection == 1:

        # For testing purposes
        SIMULATION_FOLDERPATH = os.path.join(WORKSPACE_DIRECTORY, 'sim1')

        # Copying generated file from previous session
        Sim_IDFProcessedData_FolderName = 'Sim_ProcessedData'
        Sim_IDFProcessedData_FolderPath = os.path.join(SIMULATION_FOLDERPATH, "Final_run_folder", Sim_IDFProcessedData_FolderName)
        shutil.copy(os.path.join(Sim_IDFProcessedData_FolderPath,'IDF_OutputVariables_DictDF.pickle'), os.path.join(Visualization_FolderPath,'Generated.pickle'))

        # Copying aggregated file from previous session
        results_path = os.path.join(WORKSPACE_DIRECTORY, "Aggregation", "Results")
        shutil.copy(os.path.join(results_path,'Aggregation_Dictionary.pickle'), os.path.join(Visualization_FolderPath,'Aggregated.pickle'))

    # Upload files -> copying uploaded files and renaming
    elif InputSelection == 2:

        for item in os.listdir(UPLOAD_DIRECTORY_VIS):
            shutil.copy(os.path.join(UPLOAD_DIRECTORY_VIS,item), Visualization_FolderPath)

    if selection == 1:
        # Finding min and max dates from generated data
        Generated_Dict_file = open(os.path.join(Visualization_FolderPath,'Generated.pickle'),"rb")
        Generated_OutputVariable_Dict = pickle.load(Generated_Dict_file)
        Generated_DateTime_List = Generated_OutputVariable_Dict['DateTime_List']
        min_date_upload = min(Generated_DateTime_List)
        max_date_upload = max(Generated_DateTime_List)

        # Getting generated data variables
        Generated_Variables = list(Generated_OutputVariable_Dict.keys())
        Generated_Variables.remove('DateTime_List')

        Aggregated_Variables = []

    elif selection == 2:
        # Finding min and max dates from generated data
        Aggregated_Dict_file = open(os.path.join(Visualization_FolderPath,'Aggregated.pickle'),"rb")
        Aggregated_OutputVariable_Dict = pickle.load(Aggregated_Dict_file)
        Aggregated_DateTime_List = Aggregated_OutputVariable_Dict['DateTime_List']
        min_date_upload = min(Aggregated_DateTime_List)
        max_date_upload = max(Aggregated_DateTime_List)

        Generated_Variables = []

        # Getting aggregated date variables
        Aggregated_Variables = list(Aggregated_OutputVariable_Dict['Aggregation_Zone_1'].columns)

    elif selection == 3:
        # Finding min and max dates from generated data
        Generated_Dict_file = open(os.path.join(Visualization_FolderPath,'Generated.pickle'),"rb")
        Generated_OutputVariable_Dict = pickle.load(Generated_Dict_file)
        Generated_DateTime_List = Generated_OutputVariable_Dict['DateTime_List']
        min_date_upload_gen = min(Generated_DateTime_List)
        max_date_upload_gen = max(Generated_DateTime_List)

        # Finding min and max dates from generated data
        Aggregated_Dict_file = open(os.path.join(Visualization_FolderPath,'Aggregated.pickle'),"rb")
        Aggregated_OutputVariable_Dict = pickle.load(Aggregated_Dict_file)
        Aggregated_DateTime_List = Aggregated_OutputVariable_Dict['DateTime_List']
        min_date_upload_agg = min(Aggregated_DateTime_List)
        max_date_upload_agg = max(Aggregated_DateTime_List)

        min_date_upload = max(min_date_upload_gen, min_date_upload_agg)
        max_date_upload = min(max_date_upload_gen, max_date_upload_agg)

        # Getting generated data variables
        Generated_Variables = list(Generated_OutputVariable_Dict.keys())
        Generated_Variables.remove('DateTime_List')

        # Getting aggregated date variables
        Aggregated_Variables = list(Aggregated_OutputVariable_Dict['Aggregation_Zone_1'].columns)

    min_date_upload = min_date_upload.replace(hour = 0, minute = 0)
    max_date_upload = max_date_upload.replace(hour = 0, minute = 0)

    return date_range1, date_range2, var_gendata, var_aggrdata, button_dist_gen, button_dist_agg, button_dist_both, mean_gen, mean_agg, button_scat_gen, button_scat_agg, button_scat_both, button_time_gen, button_time_agg, button_time_both, min_date_upload, max_date_upload, min_date_upload, max_date_upload, min_date_upload, max_date_upload, Generated_Variables, Aggregated_Variables

@app.callback(
    Output(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'options'),
    Input(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_DropDown_GeneratedDataTables_Interaction(variable):
    columns = []
    if variable is not None:
        Generated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Generated.pickle'),"rb")
        Generated_OutputVariable_Dict = pickle.load(Generated_Dict_file)
        columns = list(Generated_OutputVariable_Dict[variable].columns)
        columns.remove('Date/Time')
    return columns

@app.callback(
    Output(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'options'),
    Input(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_DropDown_AggregatedDataTables_Interaction(variable):
    columns = []
    if variable is not None:
        Aggregated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Aggregated.pickle'),"rb")
        Aggregated_OutputVariable_Dict = pickle.load(Aggregated_Dict_file)
        columns = [x for x in Aggregated_OutputVariable_Dict if (x.find('Aggregation_Zone_')>=0) and not (x.find('Aggregation_Zone_Equipment_')>=0)]
    return columns

@app.callback(
    Output(component_id = 'EPVis_Graph_Distribution', component_property = 'figure', allow_duplicate = True),
    Output(component_id = 'EPVis_Table_GeneratedData', component_property = 'data', allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_DistGeneratedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_DistGeneratedData_Interaction(table, column, n_clicks):
    Generated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Generated.pickle'),"rb")
    Generated_OutputVariable_Dict = pickle.load(Generated_Dict_file)
    
    # Creating DF for plotting
    Data_DF = pd.DataFrame()
    for item in column:
        Current_DF = Generated_OutputVariable_Dict[table][item].to_frame()
        Current_DF = Current_DF.rename(columns={item: 'ColName'})
        Current_DF['dataset'] = item
        Data_DF = pd.concat([Data_DF, Current_DF])

    # Plotting the combined DF
    figure = px.histogram(Data_DF, x='ColName', color='dataset', histnorm='probability')
    figure.update_layout(xaxis_title='Support')
    figure.update_layout(yaxis_title='Probability')

    data = []

    return figure,data

@app.callback(
    Output(component_id = 'EPVis_Graph_Distribution', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_DistAggregatedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_DistAggregatedData_Interaction(table, column, n_clicks):
    Aggregated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Aggregated.pickle'),"rb")
    Aggregated_OutputVariable_Dict = pickle.load(Aggregated_Dict_file)
    
    # Creating DF for plotting
    Data_DF = pd.DataFrame()
    for item in column:
        Current_DF = Aggregated_OutputVariable_Dict[item][table].to_frame()
        Current_DF = Current_DF.rename(columns={table: 'ColName'})
        Current_DF['dataset'] = item
        Data_DF = pd.concat([Data_DF, Current_DF])

    # Plotting the combined DF
    figure = px.histogram(Data_DF, x='ColName', color='dataset', histnorm='probability')
    figure.update_layout(xaxis_title='Support')
    figure.update_layout(yaxis_title='Probability')
    return figure

@app.callback(
    Output(component_id = 'EPVis_Graph_Distribution', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_DistBothData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_DistBothData_Interaction(table_gen, column_gen, table_agg, column_agg, n_clicks):
    # Generated Data 
    Generated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Generated.pickle'),"rb")
    Generated_OutputVariable_Dict = pickle.load(Generated_Dict_file)
    
    # Creating DF for plotting
    Data_DF = pd.DataFrame()
    for item in column_gen:
        Current_DF = Generated_OutputVariable_Dict[table_gen][item].to_frame()
        Current_DF = Current_DF.rename(columns={item: 'ColName'})
        Current_DF['dataset'] = item
        Data_DF = pd.concat([Data_DF, Current_DF])

    # Aggregated Data
    Aggregated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Aggregated.pickle'),"rb")
    Aggregated_OutputVariable_Dict = pickle.load(Aggregated_Dict_file)
    
    # Creating DF for plotting
    for item in column_agg:
        Current_DF = Aggregated_OutputVariable_Dict[item][table_agg].to_frame()
        Current_DF = Current_DF.rename(columns={table_agg: 'ColName'})
        Current_DF['dataset'] = item
        Data_DF = pd.concat([Data_DF, Current_DF])

    # Plotting the combined DF
    figure = px.histogram(Data_DF, x='ColName', color='dataset', histnorm='probability')
    figure.update_layout(xaxis_title='Support')
    figure.update_layout(yaxis_title='Probability')
    return figure

@app.callback(
    Output(component_id = 'EPVis_H5_ScatterPlotComment', component_property = 'hidden'),
    Input(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_H5_ScatterPlotComment_Interaction(gen_column, agg_column):
    if gen_column is None:
        gen_column = []
    if agg_column is None:
        agg_column = []

    total_elements = len(gen_column) + len(agg_column)
    if total_elements == 2:
        comment = True
    else:
        comment = False
    return comment

@app.callback(
    Output(component_id = 'EPVis_Graph_Scatter', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_ScatterGeneratedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_ScatGeneratedData_Interaction(table_gen, column_gen, table_agg, column_agg, n_clicks):
    # Generated Data
    Generated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Generated.pickle'),"rb")
    Generated_OutputVariable_Dict = pickle.load(Generated_Dict_file)

    # Aggregated Data
    Aggregated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Aggregated.pickle'),"rb")
    Aggregated_OutputVariable_Dict = pickle.load(Aggregated_Dict_file)

    # Creating DF for plotting
    if len(column_gen) == 2:
        df = pd.DataFrame({
            column_gen[0]:Generated_OutputVariable_Dict[table_gen][column_gen[0]],
            column_gen[1]:Generated_OutputVariable_Dict[table_gen][column_gen[1]]
        })

    elif len(column_agg) == 2:
        df = pd.DataFrame({
            column_agg[0]:Aggregated_OutputVariable_Dict[column_agg[0]][table_agg],
            column_agg[1]:Aggregated_OutputVariable_Dict[column_agg[1]][table_agg]
        })

    else:
        df = pd.DataFrame({
            column_gen[0]:Generated_OutputVariable_Dict[table_gen][column_gen[0]],
            column_agg[0]:Aggregated_OutputVariable_Dict[column_agg[0]][table_agg]
        })

    # Plotting the combined DF
    figure = px.scatter(df, x = df[df.columns[0]], y = df[df.columns[1]],
                        labels = {'x': df[df.columns[0]], 'y': df[df.columns[1]]})

    return figure

@app.callback(
    Output(component_id = 'EPVis_Graph_TimeSeries', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_TimeGeneratedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_TimeGeneratedData_Interaction(table_gen, column_gen, table_agg, column_agg, n_clicks):
    # Generated Data
    Generated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Generated.pickle'),"rb")
    Generated_OutputVariable_Dict = pickle.load(Generated_Dict_file)

    # Aggregated Data
    Aggregated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Aggregated.pickle'),"rb")
    Aggregated_OutputVariable_Dict = pickle.load(Aggregated_Dict_file)

    if table_gen is not None and column_gen is not None:
        Data_DF = Generated_OutputVariable_Dict[table_gen][column_gen]
    else:
        Data_DF = pd.DataFrame()

    # Creating DF for plotting
    column_agg_new = []
    for item in column_agg:
        Current_DF = Aggregated_OutputVariable_Dict[item][table_agg].to_frame()
        column_name = "".join([item, table_agg])
        column_agg_new.append(column_name)
        Current_DF = Current_DF.rename(columns={table_agg: column_name})
        Data_DF = pd.concat([Data_DF, Current_DF], axis=1)

    if column_gen is not None:
        time_list = pd.DataFrame(Generated_OutputVariable_Dict['DateTime_List'], columns=['Date'])
    elif column_agg is not None:
        time_list = pd.DataFrame(Aggregated_OutputVariable_Dict['DateTime_List'], columns=['Date'])

    # Merging the dataframes
    merged_df = pd.concat([time_list, Data_DF], axis=1)

    # Melting the dataframe for Plotly Express
    if column_gen is not None:
        variable_list = column_gen+column_agg_new
    else:
        variable_list = column_agg_new
    melted_df = merged_df.melt(id_vars='Date', value_vars=variable_list, var_name='Variable', value_name='Value')

    # Plotting the time series using Plotly Express
    figure = px.line(melted_df, x='Date', y='Value', color='Variable', labels={'Date': 'Date', 'Value': 'Variable', 'Variable': 'Data Series'})

    return figure
'''
@app.callback(
    Output(component_id = 'EPVis_Graph_TimeSeries', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_TimeGeneratedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_TimeGeneratedData_Interaction(table_gen, column_gen, table_agg, column_agg, n_clicks):
    # Generated Data
    Generated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Generated.pickle'),"rb")
    Generated_OutputVariable_Dict = pickle.load(Generated_Dict_file)

    # Aggregated Data
    Aggregated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Aggregated.pickle'),"rb")
    Aggregated_OutputVariable_Dict = pickle.load(Aggregated_Dict_file)

    if table_gen is not None and column_gen is not None:
        Data_DF = Generated_OutputVariable_Dict[table_gen][column_gen]
    else:
        Data_DF = pd.DataFrame()

    # Creating DF for plotting
    column_agg_new = []
    for item in column_agg:
        Current_DF = Aggregated_OutputVariable_Dict[item][table_agg].to_frame()
        column_name = "".join([item, table_agg])
        column_agg_new.append(column_name)
        Current_DF = Current_DF.rename(columns={table_agg: column_name})
        Data_DF = pd.concat([Data_DF, Current_DF], axis=1)

    if column_gen is not None:
        time_list = pd.DataFrame(Generated_OutputVariable_Dict['DateTime_List'], columns=['Date'])
    elif column_agg is not None:
        time_list = pd.DataFrame(Aggregated_OutputVariable_Dict['DateTime_List'], columns=['Date'])

    # Merging the dataframes
    merged_df = pd.concat([time_list, Data_DF], axis=1)

    # Melting the dataframe for Plotly Express
    if column_gen is not None:
        variable_list = column_gen+column_agg_new
    else:
        variable_list = column_agg_new
    melted_df = merged_df.melt(id_vars='Date', value_vars=variable_list, var_name='Variable', value_name='Value')

    # Plotting the time series using Plotly Express
    figure = px.line(melted_df, x='Date', y='Value', color='Variable', labels={'Date': 'Date', 'Value': 'Variable', 'Variable': 'Data Series'})

    return figure
'''

# Running the App
if __name__ == '__main__':
    app.run(port=4050)
