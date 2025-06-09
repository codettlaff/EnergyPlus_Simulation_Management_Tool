"""
Created on Tue Jan 30 15:32:25 2024

@author: Athul Jose P
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
import EPGenApp_Module as EPGen
import EPAggApp_Module as EPAgg
import EPVisApp_Module as EPVis

UPLOAD_DIRECTORY = os.path.join(os.getcwd(), "EP_APP_Uploads")
UPLOAD_DIRECTORY_AGG_PICKLE = os.path.join(UPLOAD_DIRECTORY, "Pickle_Upload")
UPLOAD_DIRECTORY_AGG_EIO = os.path.join(UPLOAD_DIRECTORY, "EIO_Upload")
UPLOAD_DIRECTORY_VIS = os.path.join(UPLOAD_DIRECTORY, "Visualization")
WORKSPACE_DIRECTORY = os.path.join(os.getcwd(), "EP_APP_Workspace")
SIMULATION_FOLDERPATH = 'abc123'
SIMULATION_FOLDERNAME = 'abc123'
DATA_DIRECTORY =  os.path.join(os.getcwd(), "..", "..", "Data")

if not os.path.exists(UPLOAD_DIRECTORY): os.makedirs(UPLOAD_DIRECTORY)
if not os.path.exists(WORKSPACE_DIRECTORY): os.makedirs(WORKSPACE_DIRECTORY)

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
                            className = 'text-left mb-2',
                            id = 'EPVis_H5_ScatterPlotComment',
                            style={'color': 'red'},
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
    building_details, upload_files, simulation_details , schedules, generate_variables, download_variables, final_download = EPGen.EPGen_Radiobutton_DatabaseSelection_Interaction_Function(folder_name, database_selection)
    return building_details, upload_files, simulation_details , schedules, generate_variables, download_variables, final_download

@app.callback(
    Output(component_id = 'upload_idf', component_property = 'children'),
    Input(component_id = 'upload_idf', component_property = 'filename'),
    State(component_id = 'upload_idf', component_property = 'contents'),
    prevent_initial_call = False)
def EPGen_Upload_IDF_Interaction(filename, content):
    message = EPGen.EPGen_Upload_IDF_Interaction_Function(filename, content)
    return message

@app.callback(
    Output(component_id = 'upload_epw', component_property = 'children'),
    Input(component_id = 'upload_epw', component_property = 'filename'),
    State(component_id = 'upload_epw', component_property = 'contents'),
    prevent_initial_call = False)
def EPGen_Upload_EPW_Interaction(filename, content):
    message = EPGen.EPGen_Upload_EPW_Interaction_Function(filename, content)
    return message

@app.callback(
    Output(component_id = 'simulation_details', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'version_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_EPVersion_Interaction(version_selection):
    simulation_details = EPGen.EPGen_Dropdown_EPVersion_Interaction_Function(version_selection)
    return simulation_details

@app.callback(
    Output(component_id = 'simulation_details', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'location_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_Location_Interaction(location_selection):
    simulation_details = EPGen.EPGen_Dropdown_Location_Interaction_Function(location_selection)
    return simulation_details

@app.callback(
    Output(component_id = 'generate_variables', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'simReportFreq_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_SimReportFreq_Interaction(simReportFreq_selection):
    generate_variables = EPGen.EPGen_Dropdown_SimReportFreq_Interaction_Function(simReportFreq_selection)
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
    schedules, People_Schedules, Equip_Schedules, Light_Schedules, HeatingSetpoint_Schedules, CoolingSetpoint_Schedules, TemperatureSetpoint_Schedules = EPGen.EPGen_RadioButton_EditSchedule_Interaction_Function(EPGen_Radiobutton_VariableSelection)
    return schedules, People_Schedules, Equip_Schedules, Light_Schedules, HeatingSetpoint_Schedules, CoolingSetpoint_Schedules, TemperatureSetpoint_Schedules

@app.callback(
    Output(component_id = 'final_download', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'download_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_DownloadSelection_Interaction(download_selection):
    final_download = EPGen.EPGen_Dropdown_DownloadSelection_Interaction_Function(download_selection)
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
    level_1_list, level_2_list, level_3_list, Weather_list, level_1_value, level_2_value, level_3_value, Weather_value = EPGen.EPGen_Dropdown_BuildingType_Interaction_Function(buildingType_selection)
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
    level_2_list, level_3_list, level_2_value, level_3_value = EPGen.EPGen_Dropdown_SubLevel1_Interaction_Function(buildingType_selection, level_1)
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
    level_3_list, level_3_value = EPGen.EPGen_Dropdown_SubLevel2_Interaction_Function(buildingType_selection, level_1, level_2)
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
    your_variable_selection, our_variable_selection = EPGen.EPGen_Button_GenerateVariables_Interaction_Function(database_selection, buildingType_selection, level_1, level_2, level_3, location_selection, n_clicks)
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
    update_selected_schedule = EPGen.EPGen_Dropdown_EditSchedule_Interaction_Function(people_schedules, equip_schedules, light_schedules, heating_schedules, cooling_schedules, temperature_schedules)
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
    update_selected_schedule = EPGen.EPGen_Button_UpdateSelectedSchedule_Interaction_Function(people_schedules, equip_schedules, light_schedules, heating_schedules, cooling_schedules, temperature_schedules, schedule_input, n_clicks)
    return update_selected_schedule

@app.callback(
    Output(component_id = 'download_variables', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'EPGen_Radiobutton_EditSchedules', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_RadioButton_EditSchedules_Interaction_2(EPGen_Radiobutton_VariableSelection):
    download_variables = EPGen.EPGen_RadioButton_EditSchedules_Interaction_2_Function(EPGen_Radiobutton_VariableSelection)
    return download_variables


@app.callback(
    Output(component_id = 'download_variables', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'done_updating_schedule', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_DoneUpdatingSchedule_Interaction(n_clicks):
    download_variables = EPGen.EPGen_Button_DoneUpdatingSchedule_Interaction_Function(n_clicks)
    return download_variables

@app.callback(
    Output(component_id = 'final_download', component_property = 'hidden'),
    Input(component_id = 'download_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Checkbox_DownloadSelection_Interaction(download_selection):
    final_download = EPGen.EPGen_Checkbox_DownloadSelection_Interaction_Function(download_selection)
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
    button_text = EPGen.EPGen_Button_GenerateData_Interaction_Function(download_selection, start_date, end_date, Sim_TimeStep, Sim_OutputVariable_ReportingFrequency, Var_selection, your_vars, n_clicks)
    return button_text

@app.callback(
    Output(component_id = 'EPGen_Download_DownloadFiles', component_property = 'data'),
    State(component_id = 'download_selection', component_property = 'value'),
    Input(component_id = 'EPGen_Button_DownloadFiles', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_DownloadFiles_Interaction(download_selection, n_clicks):
    download_path = EPGen.EPGen_Button_DownloadFiles_Interaction_Function(download_selection, n_clicks)
    return download_path

@app.callback(
    Output(component_id = 'EPGen_Button_EndSession', component_property = 'children'),
    Input(component_id = 'EPGen_Button_EndSession', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_EndSession_Interaction(n_clicks):
    message = EPGen.EPGen_Button_EndSession_Interaction_Function(n_clicks)
    return message

##########################################################################################################

#################### Aggregation #########################################################################

##########################################################################################################


@app.callback(
    Output(component_id = 'EPAgg_Div_UploadFiles', component_property = 'hidden'),
    Output(component_id = 'EPAgg_Div_AggregationVariables', component_property = 'hidden'),
    Input(component_id = 'EPAgg_RadioButton_InputSelection', component_property = 'value'),
    prevent_initial_call = True)
def EPAgg_RadioButton_InputSelection_Interaction(value):
    upload_div, variable_div = EPAgg.EPAgg_RadioButton_InputSelection_Interaction_Function(value)
    return upload_div, variable_div

@app.callback(
    Output(component_id = 'EPAgg_Upload_Pickle', component_property = 'children'),
    Input(component_id = 'EPAgg_Upload_Pickle', component_property = 'filename'),
    State(component_id = 'EPAgg_Upload_Pickle', component_property = 'contents'),
    prevent_initial_call = False)
def EPAgg_Upload_Pickle_Interaction(filename, content):
    message = EPAgg.EPAgg_Upload_Pickle_Interaction_Function(filename, content)
    return message

@app.callback(
    Output(component_id = 'EPAgg_Upload_EIO', component_property = 'children'),
    Input(component_id = 'EPAgg_Upload_EIO', component_property = 'filename'),
    State(component_id = 'EPAgg_Upload_EIO', component_property = 'contents'),
    prevent_initial_call = False)
def EPAgg_Upload_EIO_Interaction(filename, content):
    message = EPAgg.EPAgg_Upload_EIO_Interaction_Function(filename, content)
    return message

@app.callback(
    Output(component_id = 'EPAgg_Div_AggregationDetails', component_property = 'hidden'),
    Input(component_id = 'EPAgg_RadioButton_AggregationVariables', component_property = 'value'),
    Input(component_id = 'EPAgg_DropDown_CustomVariables', component_property = 'value'),
    prevent_initial_call = True)
def EPAgg_DropDown_AggregationVariables_Interaction(selection, value):
    div = EPAgg.EPAgg_DropDown_AggregationVariables_Interaction_Function(selection, value)
    return div

@app.callback(
    Output(component_id = 'EPAgg_DropDown_PreselectedVariables', component_property = 'options'),
    Output(component_id = 'EPAgg_DropDown_CustomVariables', component_property = 'options'),
    Output(component_id = 'EPAgg_DropDown_ZoneList', component_property = 'options'),
    State(component_id = 'EPAgg_RadioButton_InputSelection', component_property = 'value'),
    Input(component_id = 'EPAgg_RadioButton_AggregationVariables', component_property = 'value'),
    prevent_initial_call = True)
def EPAgg_RadioButton_AggregationVariables_Interaction(InputSelection, VariableSelection):
    pre_list, custom_list, zone_list = EPAgg.EPAgg_RadioButton_AggregationVariables_Interaction_Function(InputSelection, VariableSelection)
    return pre_list, custom_list, zone_list

@app.callback(
    Output(component_id = 'EPAgg_Div_FinalDownload', component_property = 'hidden'),
    Input(component_id = 'EPAgg_DropDown_TypeOfAggregation', component_property = 'value'),
    prevent_initial_call = True)
def EPAgg_DropDown_TypeOfAggregation_Interaction(value):
    div = EPAgg.EPAgg_DropDown_TypeOfAggregation_Interaction_Function(value)
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
    message = EPAgg.EPAgg_Button_Aggregate_Interaction_Function(variable_selection, custom_variables, aggregate_to, custom_zone_list, Type_Aggregation, n_clicks)
    return "Aggregation Completed"

@app.callback(
    Output(component_id = 'EPAgg_Download_DownloadFiles', component_property = 'data'),
    Input(component_id = 'EPAgg_Button_Download', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPAgg_Button_Download_Interaction(n_clicks):
    download_path = EPAgg.EPAgg_Button_Download_Interaction_Function(n_clicks)
    return download_path

##########################################################################################################

#################### Visualization #######################################################################

##########################################################################################################

@app.callback(
    Output(component_id = 'EPVis_Div_Datatobeselected', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'EPVis_Div_UploadData', component_property = 'hidden'),
    Input(component_id = 'EPVis_RadioButton_DataSource', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_RadioButton_DataSource_Interaction(data_source):
    data_selection, upload_data = EPVis.EPVis_RadioButton_DataSource_Interaction_Function(data_source)
    return data_selection, upload_data

@app.callback(
    Output(component_id = 'EPVis_Upload_GeneratedData', component_property = 'children'),
    Input(component_id = 'EPVis_Upload_GeneratedData', component_property = 'filename'),
    State(component_id = 'EPVis_Upload_GeneratedData', component_property = 'contents'),
    prevent_initial_call = False)
def EPVis_Upload_GeneratedData_Interaction(filename, content):
    message = EPVis.EPVis_Upload_GeneratedData_Interaction_Function(filename, content)
    return message

@app.callback(
    Output(component_id = 'EPVis_Upload_AggregatedData', component_property = 'children'),
    Output(component_id = 'EPVis_Div_Datatobeselected', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'EPVis_Upload_AggregatedData', component_property = 'filename'),
    State(component_id = 'EPVis_Upload_AggregatedData', component_property = 'contents'),
    prevent_initial_call = True)
def EPVis_Upload_AggregatedData_Interaction(filename, content):
    message, data_selection = EPVis.EPVis_Upload_AggregatedData_Interaction_Function(filename, content)
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
    date_range1, date_range2, var_gendata, var_aggrdata, button_dist_gen, button_dist_agg, button_dist_both, mean_gen, mean_agg, button_scat_gen, button_scat_agg, button_scat_both, button_time_gen, button_time_agg, button_time_both, min_date_upload, max_date_upload, min_date_upload, max_date_upload, min_date_upload, max_date_upload, Generated_Variables, Aggregated_Variables = EPVis.EPVis_Radio_DataToBeSelected_Interaction_Function(InputSelection, selection)
    return date_range1, date_range2, var_gendata, var_aggrdata, button_dist_gen, button_dist_agg, button_dist_both, mean_gen, mean_agg, button_scat_gen, button_scat_agg, button_scat_both, button_time_gen, button_time_agg, button_time_both, min_date_upload, max_date_upload, min_date_upload, max_date_upload, min_date_upload, max_date_upload, Generated_Variables, Aggregated_Variables

@app.callback(
    Output(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'options'),
    Input(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_DropDown_GeneratedDataTables_Interaction(variable):
    columns = EPVis.EPVis_DropDown_GeneratedDataTables_Interaction_Function(variable)
    return columns

@app.callback(
    Output(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'options'),
    Input(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_DropDown_AggregatedDataTables_Interaction(variable):
    columns = EPVis.EPVis_DropDown_AggregatedDataTables_Interaction_Function(variable)
    return columns

@app.callback(
    Output(component_id = 'EPVis_Graph_Distribution', component_property = 'figure', allow_duplicate = True),
    Output(component_id = 'EPVis_Table_GeneratedData', component_property = 'data', allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_DistGeneratedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_DistGeneratedData_Interaction(table, column, n_clicks):
    figure,data = EPVis.EPVis_Button_DistGeneratedData_Interaction_Function(table, column, n_clicks)
    return figure,data

@app.callback(
    Output(component_id = 'EPVis_Graph_Distribution', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_DistAggregatedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_DistAggregatedData_Interaction(table, column, n_clicks):
    figure = EPVis.EPVis_Button_DistAggregatedData_Interaction_Function(table, column, n_clicks)
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
    figure = EPVis.EPVis_Button_DistBothData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, n_clicks)
    return figure

@app.callback(
    Output(component_id = 'EPVis_H5_ScatterPlotComment', component_property = 'hidden'),
    Input(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_H5_ScatterPlotComment_Interaction(gen_column, agg_column):
    comment = EPVis.EPVis_H5_ScatterPlotComment_Interaction_Function(gen_column, agg_column)
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
    figure = EPVis.EPVis_Button_ScatGeneratedData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, n_clicks)
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
    figure = EPVis.EPVis_Button_TimeGeneratedData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, n_clicks)
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
