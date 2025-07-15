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
from dash import Dash, dcc, html, Input, Output, State, dash_table, ctx
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

tab_layout = [
    
    # Row 1, data source, data to be selected
    dbc.Row([

        dbc.Col([

            html.Div([

                html.H5("Data Source", className = 'section-title'),

                dcc.RadioItems(
                    id = 'visualization_data_source',
                    labelStyle = {'display': 'block'},
                    options = [
                        {'label': " Continue Session", 'value': 1},
                        {'label': " Upload Files", 'value': 2},
                        {'label': " Database", 'value': 3}
                        ],
                    value = 1,
                    className='radiobutton-box',
                ),
            ],className='div-box'
            
            ),], xs = 12, sm = 12, md = 6, lg = 6, xl = 6), # width = 12

        dbc.Col([
            # Upload Section Container
            html.Div([
                # Upload Generated Data
                html.Div([
                    html.Label("Generated Data", className='section-label'),
                    dcc.Upload(
                        id='visualization_upload_generated_data_box',
                        children=html.Div("Drag and Drop or Select Files for Generated Data"),
                        className='upload-box'
                    )
                ]),

                # Spacer
                html.Br(),

                # Upload Aggregated Data
                html.Div([
                    html.Label("Aggregated Data", className='section-label'),
                    dcc.Upload(
                        id='visualization_upload_aggregated_data_box',
                        children=html.Div("Drag and Drop or Select Files for Aggregated Data"),
                        className="upload-box"
                    )
                ])
            ],
            id='visualization_upload_data_menu',
            hidden=True,
            className='div-box'
            ),

            # Placeholder for Database Data (currently just a break)
            html.Div([

                html.Label("Select Simulation", className='section-label'),
                dcc.Dropdown(
                    options=[],
                    value=None,
                    id='visualization_database_simulation_dropdown',
                    className='dropdown-box'
                ),

            ],
            id='visualization_select_from_database_menu',
            hidden=True,
            className='div-box'
            )


        ], xs=12, sm=12, md=6, lg=6, xl=6)

        ], justify = "center", align = "center"),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Row 2, Data to be selected
    html.Div([

        html.H5("Data to be selected", className = 'section-title'),

        dcc.RadioItems(
            id = 'visualization_generated_or_aggregated_data_selection',
            labelStyle = {'display': 'block'},
            options = [
                {'label' : " Generated Data", 'value' : 1},
                {'label' : " Aggregated Data", 'value' : 2},
                {'label' : " Both", 'value' : 3}
                ]  ,
            value = 1,
            className = 'radiobutton-box',
        ),
        ],
        id = 'visualization_generated_or_aggregated_data_selection_menu',
        hidden = True,
        className='div-box'
        ),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Row 3, available date range
    dbc.Row([

        dbc.Col([

            html.Div([

                html.H5("Date Range from Uploaded File:",
                    className = 'text-left text-secondary mb-2'),

                dcc.DatePickerRange(
                    id='visualization_date_picker_calendar',
                    min_date_allowed=None,
                    max_date_allowed=None,
                    start_date=None,
                    end_date=None
                ),

            ],
            id = 'visualization_date_picker',
            hidden = True
            ),

            ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

        ], justify = "left", align = "center"),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Row 5, select variable title
    dbc.Row([

        dbc.Col([

            html.H3("Select Variable:",
                    className = 'text-left text-secondary mb-2'),

            ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

        ], justify = "left", align = "center"),

    # Row 6, select variable dropdowns
    dbc.Row([

        dbc.Col([

            html.Div([

                html.H5("Generated Data",
                    className = 'text-left text-secondary mb-2 ms-4 mt-2'),

                html.Label("Select Variable:",
                style={'margin-left': '2.5%', 'font-weight': 'bold'}),

                dcc.Dropdown([], '',
                    id='visualization_generated_data_variable_dropdown',
                    style = {
                        'width': '95%',
                        'margin-left': '2.5%', 
                        'margin-bottom': '2.5%'  
                        }),

                html.Label("Select Variable Column:",
                style={'margin-left': '2.5%', 'font-weight': 'bold'}),

                dcc.Dropdown([], '',
                    id='visualization_generated_data_variable_column_dropdown',
                    style = {
                        'width': '95%',
                        'margin-left': '2.5%', 
                        'margin-bottom': '2.5%'  
                        }),

                html.Label("Enter Custom Label:",
                        style={'margin-left': '2.5%', 'font-weight': 'bold'}),

                    dcc.Input(
                        id='visualization_generated_data_custom_label_input',
                        type='text',
                        placeholder='Enter label...',
                        style={
                            'width': '95%',
                            'margin-left': '2.5%',
                            'margin-bottom': '2.5%',
                        })

            ],
            id = 'visualization_generated_data_variable_selection_menu',
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

                html.H5("Select Zones",
                    className = 'text-left text-secondary mb-2 ms-4 mt-2'),

                html.Label("Generation Zones:",
                style={'margin-left': '2.5%', 'font-weight': 'bold'}),

                dcc.Dropdown([], '',
                    id='visualization_generation_zones_dropdown',
                    style = {
                        'width': '95%',
                        'margin-left': '2.5%', 
                        'margin-bottom': '2.5%'  
                        }),

                html.Label("Aggregation Zones",
                style={'margin-left': '2.5%', 'font-weight': 'bold'}),

                dcc.Dropdown([], '',
                    id='visualization_aggregated_zones_dropdown',
                    style = {
                        'width': '95%',
                        'margin-left': '2.5%', 
                        'margin-bottom': '2.5%'  
                        }),

            ],
            id = 'visualization_aggregated_data_zone_selection_menu',
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

    # Row 7, distribution plot title
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

    # Row 8, distribution plot buttons
    dbc.Row([

        dbc.Col([

            html.Button(
                'Generated Data',
                # id = 'EPVis_Button_DistGeneratedData',
                id = 'visualization_distribution_plot_button',
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

    # Row 9, distribution plot
    dbc.Row([

        dbc.Col([

            dcc.Graph(id = 'EPVis_Graph_Distribution', figure ={}),

            ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

    ], justify = "center", align = "center"),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Row 10, generated distribution details
    html.Div([
        dbc.Row([
            dash_table.DataTable(
                id='EPVis_Table_GeneratedData',
                columns=[
                    {"name": "Variable", "id": "Variable"},
                    {"name": "Mean", "id": "Mean"},
                    {"name": "Variance", "id": "Variance"},
                    {"name": "Standard Deviation", "id": "Standard_Deviation"},
                    {"name": "Range", "id": "Range"},
                ],
                data=[],
                style_table={'margin': '0 auto'},  # center the table
                style_cell={'textAlign': 'center'},  # center text in cells
                style_header={'fontWeight': 'bold', 'textAlign': 'center'},  # bold headers
            ),
        ]),
        ],id = 'EPVis_Div_Statistics',
        style = {
            'borderWidth': '1px',
            'borderStyle': 'solid',
            'borderRadius': '5px',
            },
    ),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Row 12, scatter plot title
    dbc.Row([

        dbc.Col([

            html.H3("Scatter Plot:",
                    className = 'text-left text-secondary mb-2')

            ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

        ], justify = "left", align = "center"),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Row 13, scatter plot warning
    dbc.Row([

        dbc.Col([

            html.H5("Please select two variables",
                    className = 'text-left mb-2',
                    id = 'EPVis_H5_ScatterPlotComment',
                    style={'color': 'red'},
                    hidden = False)

            ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

        ], justify = "left", align = "center"),

    # Row 14, scatter plot button
    dbc.Row([

        dbc.Col([

            html.Button('Plot',
                        id = 'EPVis_Button_ScatterBothData',
                        hidden = True,
                        className = "btn btn-primary btn-lg col-12"),

            ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12


        ], justify = "center", align = "center"),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Row 15, scatter plot
    dbc.Row([

        dbc.Col([

            dcc.Graph(id = 'EPVis_Graph_Scatter', figure ={}),

            ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

        ], justify = "center", align = "center"),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Row 16, time series plot title
    dbc.Row([

        dbc.Col([

            html.H3("Time Series Plot:",
                    className = 'text-left text-secondary mb-2')

            ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

        ], justify = "left", align = "center"),

    # Break Row
    dbc.Row([dbc.Col([html.Br()], width = 12),]),

    # Row 17, time series buttons
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

    # Row 18, time series graph
    dbc.Row([

        dbc.Col([

            dcc.Graph(id = 'EPVis_Graph_TimeSeries', figure ={}),

            ], xs = 12, sm = 12, md = 12, lg = 12, xl = 12), # width = 12

        ], justify = "center", align = "center"),

    # Row 19, end session
    dbc.Row([

        dbc.Col([

            html.Br(),
            html.Button('End Session',
            id = 'Button_es_visualization',
            className = "btn btn-primary btn-lg col-12",
            ),

            ], width = 12),

        ]),

]

'''

def EPVis_Upload_GeneratedData_Interaction_Function(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file('Generated.pickle', content, UPLOAD_DIRECTORY_VIS)
        message = filename + ' uploaded successfully'
    else:
        message = '📁 Drag and Drop or Select Files for Generated Data'
    return message

def EPVis_Upload_AggregatedData_Interaction_Function(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file('Aggregated.pickle', content, UPLOAD_DIRECTORY_VIS)
        message = filename + ' uploaded successfully'
        data_selection = False
    else:
        message = '📁 Drag and Drop or Select Files for Aggregated Data'
        data_selection = True

    return message, data_selection

def EPVis_RadioButton_DataToBeSelected_Interaction_Function(value):
    if value is not None:
        return False
    else:
        return True

def EPVis_Button_Proceed_Interaction_Function(InputSelection, selection, n_clicks):
    if selection == 1: # Generate Data
        date_range1 = False
        date_range2 = False
        var_gendata = False
        var_aggrdata = True
        button_dist_gen = False
        button_dist_agg = True
        button_dist_both = True
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

    # Database -> select files from database
    elif InputSelection ==3:
        z=1


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

    return date_range1, date_range2, var_gendata, var_aggrdata, button_dist_gen, button_dist_agg, button_dist_both, button_time_gen, button_time_agg, button_time_both, min_date_upload, max_date_upload, min_date_upload, max_date_upload, min_date_upload, max_date_upload, Generated_Variables, Aggregated_Variables

def EPVis_DropDown_GeneratedDataTables_Interaction_Function(variable):
    columns = []
    if variable is not None:
        Generated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Generated.pickle'),"rb")
        Generated_OutputVariable_Dict = pickle.load(Generated_Dict_file)
        columns = list(Generated_OutputVariable_Dict[variable].columns)
        columns.remove('Date/Time')
    return columns

def EPVis_DropDown_AggregatedDataTables_Interaction_Function(variable):
    columns = []
    if variable is not None:
        Aggregated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Aggregated.pickle'),"rb")
        Aggregated_OutputVariable_Dict = pickle.load(Aggregated_Dict_file)
        columns = [x for x in Aggregated_OutputVariable_Dict if (x.find('Aggregation_Zone_')>=0) and not (x.find('Aggregation_Zone_Equipment_')>=0)]
    return columns

def EPVis_Button_DistGeneratedData_Interaction_Function(table, column, start_date, end_date, n_clicks):
    # === Load Generated Data ===
    with open(os.path.join(WORKSPACE_DIRECTORY, 'Visualization', 'Generated.pickle'), "rb") as f:
        Generated_OutputVariable_Dict = pickle.load(f)

    # === Prepare date filter ===
    start, end = pd.to_datetime(start_date), pd.to_datetime(end_date)

    # === Get and process the DataFrame ===
    df_gen = Generated_OutputVariable_Dict[table].copy()

    # --- Handle 'Date/Time' column with 24:00:00 fix ---
    split_dt = df_gen['Date/Time'].str.strip().str.split(" ", expand=True)
    df_gen['MM/DD'] = split_dt[0]
    df_gen['HH:MM:SS'] = split_dt[1]

    mask_24 = df_gen['HH:MM:SS'] == '24:00:00'
    df_gen.loc[mask_24, 'HH:MM:SS'] = '00:00:00'
    df_gen['MM/DD'] = pd.to_datetime('2020 ' + df_gen['MM/DD'], format='%Y %m/%d')
    df_gen.loc[mask_24, 'MM/DD'] += pd.Timedelta(days=1)

    df_gen['DateTime'] = pd.to_datetime(df_gen['MM/DD'].astype(str) + ' ' + df_gen['HH:MM:SS'])
    df_gen.drop(columns=['MM/DD', 'HH:MM:SS'], inplace=True)

    # === Filter by date range ===
    df_gen = df_gen[(df_gen['DateTime'] >= start) & (df_gen['DateTime'] <= end)]

    # === Build final plotting DataFrame ===
    Data_DF = pd.DataFrame()
    for item in column:
        if item not in df_gen.columns:
            print(f"[Warning] '{item}' not found in Generated_OutputVariable_Dict['{table}'].")
            continue

        Current_DF = df_gen[['DateTime', item]].copy()
        Current_DF = Current_DF.rename(columns={item: 'ColName'})
        Current_DF['dataset'] = item
        Data_DF = pd.concat([Data_DF, Current_DF])

    # === Plotting ===
    figure = px.histogram(Data_DF, x='ColName', color='dataset', histnorm='probability')
    figure.update_layout(xaxis_title='Frequency', yaxis_title='Value')

    # === Get statistics ===
    data = EPVis_DF2stat(Data_DF)

    return figure, data

def EPVis_DF2stat(Data_DF):
    summary_df = Data_DF.groupby('dataset')['ColName'].agg(
        Mean='mean',
        Variance='var',
        Standard_Deviation='std',
        Min='min',
        Max='max'
    ).reset_index()

    summary_df['Mean'] = summary_df['Mean'].round(2)
    summary_df['Variance'] = summary_df['Variance'].round(2)
    summary_df['Standard_Deviation'] = summary_df['Standard_Deviation'].round(2)

    # Format range as "min to max"
    summary_df['Range'] = summary_df['Min'].round(2).astype(str) + ' to ' + summary_df['Max'].round(2).astype(str)

    summary_df = summary_df.rename(columns={'dataset': 'Variable'})

    # Drop Min and Max columns if not needed for table display
    summary_df = summary_df[['Variable', 'Mean', 'Variance', 'Standard_Deviation', 'Range']]
    
    return summary_df.to_dict('records')

def EPVis_Button_DistAggregatedData_Interaction_Function(table, column, start_date, end_date, n_clicks):
    # === Load Aggregated Data ===
    with open(os.path.join(WORKSPACE_DIRECTORY, 'Visualization', 'Aggregated.pickle'), "rb") as f:
        Aggregated_OutputVariable_Dict = pickle.load(f)

    # === Prepare datetime and filter range ===
    datetime_series = pd.to_datetime(Aggregated_OutputVariable_Dict['DateTime_List'])
    start, end = pd.to_datetime(start_date), pd.to_datetime(end_date)

    # === Build DataFrame for plotting ===
    Data_DF = pd.DataFrame()

    for item in column:
        if item not in Aggregated_OutputVariable_Dict:
            print(f"[Warning] '{item}' not found in Aggregated_OutputVariable_Dict.")
            continue

        df = Aggregated_OutputVariable_Dict[item]
        
        if table not in df.columns:
            print(f"[Warning] '{table}' not found in Aggregated_OutputVariable_Dict['{item}'].")
            continue

        df = df.copy()
        df['DateTime'] = datetime_series

        # Filter by date
        df = df[(df['DateTime'] >= start) & (df['DateTime'] <= end)]

        # Prepare formatted DataFrame
        Current_DF = df[['DateTime', table]].rename(columns={table: 'ColName'})
        Current_DF['dataset'] = item

        # Append to main DF
        Data_DF = pd.concat([Data_DF, Current_DF])

    # === Plotting ===
    figure = px.histogram(Data_DF, x='ColName', color='dataset', histnorm='probability')
    figure.update_layout(xaxis_title='Frequency', yaxis_title='Value')

    # === Get statistics ===
    data = EPVis_DF2stat(Data_DF)


    return figure, data

def EPVis_Button_DistBothData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, start_date, end_date, n_clicks):
    # === Load Data ===
    with open(os.path.join(WORKSPACE_DIRECTORY, 'Visualization', 'Generated.pickle'), "rb") as f:
        Generated_OutputVariable_Dict = pickle.load(f)

    with open(os.path.join(WORKSPACE_DIRECTORY, 'Visualization', 'Aggregated.pickle'), "rb") as f:
        Aggregated_OutputVariable_Dict = pickle.load(f)

    # === Prepare Date Filter ===
    start, end = pd.to_datetime(start_date), pd.to_datetime(end_date)
    Data_DF = pd.DataFrame()

    # === Process Generated Data ===
    df_gen = Generated_OutputVariable_Dict[table_gen].copy()

    # Clean and combine date and time
    split_dt = df_gen['Date/Time'].str.strip().str.split(" ", expand=True)
    df_gen['MM/DD'] = split_dt[0]
    df_gen['HH:MM:SS'] = split_dt[1]

    # Handle 24:00:00 by advancing date
    mask_24 = df_gen['HH:MM:SS'] == '24:00:00'
    df_gen.loc[mask_24, 'HH:MM:SS'] = '00:00:00'
    df_gen['MM/DD'] = pd.to_datetime('2020 ' + df_gen['MM/DD'], format='%Y %m/%d')
    df_gen.loc[mask_24, 'MM/DD'] += pd.Timedelta(days=1)

    df_gen['DateTime'] = pd.to_datetime(df_gen['MM/DD'].astype(str) + ' ' + df_gen['HH:MM:SS'])
    df_gen.drop(columns=['MM/DD', 'HH:MM:SS'], inplace=True)

    # Filter and append selected variables
    df_gen = df_gen[(df_gen['DateTime'] >= start) & (df_gen['DateTime'] <= end)]
    for item in column_gen:
        if item in df_gen.columns:
            Data_DF = pd.concat([Data_DF, pd.DataFrame({
                'DateTime': df_gen['DateTime'],
                'ColName': df_gen[item],
                'dataset': item
            })])

    # === Process Aggregated Data ===
    datetime_series = pd.to_datetime(Aggregated_OutputVariable_Dict['DateTime_List'])
    df_agg_all = Aggregated_OutputVariable_Dict[column_agg[0]].copy()

    if table_agg in df_agg_all.columns:
        df_agg_all['DateTime'] = datetime_series
        df_agg_all = df_agg_all[(df_agg_all['DateTime'] >= start) & (df_agg_all['DateTime'] <= end)]
        Data_DF = pd.concat([Data_DF, pd.DataFrame({
            'DateTime': df_agg_all['DateTime'],
            'ColName': df_agg_all[table_agg],
            'dataset': table_agg
        })])
    else:
        print(f"[Warning] Variable '{table_agg}' not found in Aggregated_OutputVariable_Dict['{column_agg[0]}'].")

    # === Plotting ===
    figure = px.histogram(Data_DF, x='ColName', color='dataset', histnorm='probability')
    figure.update_layout(xaxis_title='Frequency', yaxis_title='Value')

    # === Generate statistics ===
    data = EPVis_DF2stat(Data_DF)

    return figure, data

def EPVis_Button_DistValues_Interaction_Function(n_clicks):
    
    data = np.random.normal(0, 1, 100)

    mean = round(np.mean(data), 2)
    var = round(np.var(data), 2)
    std = round(np.std(data), 2)
    rng = f"{round(np.min(data), 2)} to {round(np.max(data), 2)}"
    return mean, var, std, rng


def EPVis_H5_ScatterPlotComment_Interaction_Function(gen_column, agg_column):
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

def EPVis_Button_ScatGeneratedData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, start_date, end_date, n_clicks):
    # === Load Data ===
    with open(os.path.join(WORKSPACE_DIRECTORY, 'Visualization', 'Generated.pickle'), "rb") as f:
        Generated_OutputVariable_Dict = pickle.load(f)
    with open(os.path.join(WORKSPACE_DIRECTORY, 'Visualization', 'Aggregated.pickle'), "rb") as f:
        Aggregated_OutputVariable_Dict = pickle.load(f)

    # === Convert date range ===
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    # === Get DateTime lists ===
    datetime_gen = pd.to_datetime(Generated_OutputVariable_Dict['DateTime_List'])
    datetime_agg = pd.to_datetime(Aggregated_OutputVariable_Dict['DateTime_List'])

    # === Prepare df based on source ===
    df = pd.DataFrame()

    # Case 1: both from generated
    if len(column_gen) == 2:
        df_gen = Generated_OutputVariable_Dict[table_gen][column_gen].copy()
        df_gen['Date'] = datetime_gen
        df_gen = df_gen[(df_gen['Date'] >= start) & (df_gen['Date'] <= end)]
        df = df_gen[[column_gen[0], column_gen[1]]].copy()

    # Case 2: both from aggregated
    elif len(column_agg) == 2:
        df_agg = pd.DataFrame()
        for item in column_agg:
            if table_agg not in Aggregated_OutputVariable_Dict[item].columns:
                continue
            df_agg[item] = Aggregated_OutputVariable_Dict[item][table_agg]
        df_agg['Date'] = datetime_agg
        df_agg = df_agg[(df_agg['Date'] >= start) & (df_agg['Date'] <= end)]
        df = df_agg[[column_agg[0], column_agg[1]]].copy()

    # Case 3: one from each
    elif len(column_gen) == 1 and len(column_agg) == 1:
        gen_series = Generated_OutputVariable_Dict[table_gen][column_gen[0]]
        agg_series = Aggregated_OutputVariable_Dict[column_agg[0]][table_agg]

        df = pd.DataFrame({
            column_gen[0]: gen_series,
            column_agg[0]: agg_series,
            'Date_gen': datetime_gen,
            'Date_agg': datetime_agg
        })

        # Align both series by matching datetime (inner join style)
        df = df[(df['Date_gen'] >= start) & (df['Date_gen'] <= end)]
        df = df[(df['Date_agg'] >= start) & (df['Date_agg'] <= end)]
        df = df[[column_gen[0], column_agg[0]]]

    else:
        print("[Error] Unable to form a valid scatter plot — please select 2 variables.")

    # === Plotting the scatter plot ===
    if not df.empty:
        figure = px.scatter(
            df,
            x=df.columns[0],
            y=df.columns[1],
            labels={'x': df.columns[0], 'y': df.columns[1]}
        )
    else:
        figure = px.scatter(title='No data to plot (empty DataFrame)')


    return figure

def EPVis_Button_TimeGeneratedData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, start_date, end_date, n_clicks_gen, n_clicks_agg, n_clicks_both):
    triggered_id = ctx.triggered_id

    # Convert date strings to datetime
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    # === Generated Data Button ===
    if triggered_id == 'EPVis_Button_TimeGeneratedData':

        with open(os.path.join(WORKSPACE_DIRECTORY, 'Visualization', 'Generated.pickle'), "rb") as f:
            Generated_OutputVariable_Dict = pickle.load(f)

        Data_DF = pd.DataFrame()

        if table_gen is not None and column_gen is not None:
            df_gen = Generated_OutputVariable_Dict[table_gen].copy()
            datetime_series = pd.to_datetime(Generated_OutputVariable_Dict['DateTime_List'])

            # Attach Date column
            df_gen['Date'] = datetime_series

            # Filter by date
            df_gen = df_gen[(df_gen['Date'] >= start) & (df_gen['Date'] <= end)]

            # Melt for plotting
            melted_df = df_gen.melt(id_vars='Date', value_vars=column_gen,
                                    var_name='Variable', value_name='Value')

            # Plot
            figure = px.line(melted_df, x='Date', y='Value', color='Variable',
                            labels={'Date': 'Date', 'Value': 'Value', 'Variable': 'Data Series'})

    # === Aggregated Data Button ===
    elif triggered_id == 'EPVis_Button_TimeAggregatedData':

        with open(os.path.join(WORKSPACE_DIRECTORY, 'Visualization', 'Aggregated.pickle'), "rb") as f:
            Aggregated_OutputVariable_Dict = pickle.load(f)

        datetime_series = pd.to_datetime(Aggregated_OutputVariable_Dict['DateTime_List'])
        df_agg_base = Aggregated_OutputVariable_Dict[column_agg[0]].copy()
        df_agg_base['Date'] = datetime_series
        df_agg_base = df_agg_base[(df_agg_base['Date'] >= start) & (df_agg_base['Date'] <= end)]

        Data_DF = pd.DataFrame()
        column_agg_new = []

        for item in column_agg:
            if table_agg not in Aggregated_OutputVariable_Dict[item].columns:
                continue
            col_df = Aggregated_OutputVariable_Dict[item][table_agg].to_frame().copy()
            col_df.columns = [f"{item}:{table_agg}"]
            column_agg_new.append(f"{item}:{table_agg}")
            Data_DF = pd.concat([Data_DF, col_df], axis=1)

        Data_DF['Date'] = datetime_series
        Data_DF = Data_DF[(Data_DF['Date'] >= start) & (Data_DF['Date'] <= end)]

        melted_df = Data_DF.melt(id_vars='Date', value_vars=column_agg_new,
                                var_name='Variable', value_name='Value')

        figure = px.line(melted_df, x='Date', y='Value', color='Variable',
                        labels={'Date': 'Date', 'Value': 'Value', 'Variable': 'Data Series'})

    # === Both Data Button ===
    elif triggered_id == 'EPVis_Button_TimeBothData':

        # Load data
        with open(os.path.join(WORKSPACE_DIRECTORY, 'Visualization', 'Generated.pickle'), "rb") as f:
            Generated_OutputVariable_Dict = pickle.load(f)
        with open(os.path.join(WORKSPACE_DIRECTORY, 'Visualization', 'Aggregated.pickle'), "rb") as f:
            Aggregated_OutputVariable_Dict = pickle.load(f)

        # Get datetime series
        datetime_gen = pd.to_datetime(Generated_OutputVariable_Dict['DateTime_List'])
        datetime_agg = pd.to_datetime(Aggregated_OutputVariable_Dict['DateTime_List'])

        # === Prepare generated data
        df_gen = pd.DataFrame()
        if table_gen is not None and column_gen:
            df_gen = Generated_OutputVariable_Dict[table_gen][column_gen].copy()
            df_gen['Date'] = datetime_gen
            df_gen = df_gen[(df_gen['Date'] >= start) & (df_gen['Date'] <= end)]

        # === Prepare aggregated data
        df_agg_combined = pd.DataFrame()
        column_agg_new = []

        for item in column_agg:
            if table_agg not in Aggregated_OutputVariable_Dict[item].columns:
                continue
            col_name = f"{item}:{table_agg}"
            column_agg_new.append(col_name)

            series = Aggregated_OutputVariable_Dict[item][table_agg].copy()
            df_temp = pd.DataFrame({col_name: series})
            df_agg_combined = pd.concat([df_agg_combined, df_temp], axis=1)

        if not df_agg_combined.empty:
            df_agg_combined['Date'] = datetime_agg
            df_agg_combined = df_agg_combined[(df_agg_combined['Date'] >= start) & (df_agg_combined['Date'] <= end)]

        # === Merge safely
        merged_df = pd.DataFrame()
        if not df_gen.empty and not df_agg_combined.empty:
            merged_df = pd.merge(df_gen, df_agg_combined, on='Date', how='outer')
            variable_list = column_gen + column_agg_new
        elif not df_gen.empty:
            merged_df = df_gen
            variable_list = column_gen
        elif not df_agg_combined.empty:
            merged_df = df_agg_combined
            variable_list = column_agg_new

        # === Melt and plot
        melted_df = merged_df.melt(id_vars='Date', value_vars=variable_list,
                                var_name='Variable', value_name='Value')

        figure = px.line(melted_df, x='Date', y='Value', color='Variable',
                        labels={'Date': 'Date', 'Value': 'Value', 'Variable': 'Data Series'})


    return figure

'''
