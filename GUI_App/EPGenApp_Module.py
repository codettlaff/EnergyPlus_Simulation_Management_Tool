"""
Created on Tue Jan 30 15:32:25 2024

@author: Athul Jose P
"""

# Importing Required Modules
import shutil
import sys
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

database_creator_script_dir = os.path.join(os.path.dirname(__file__), '..', 'Data_Generation')
sys.path.append(database_creator_script_dir)
import EP_DataGenerator_Script_v2_20250512 as EP_Gen

UPLOAD_DIRECTORY = os.path.join(os.getcwd(), "EP_APP_Uploads")
UPLOAD_DIRECTORY_AGG_PICKLE = os.path.join(UPLOAD_DIRECTORY, "Pickle_Upload")
UPLOAD_DIRECTORY_AGG_EIO = os.path.join(UPLOAD_DIRECTORY, "EIO_Upload")
UPLOAD_DIRECTORY_VIS = os.path.join(UPLOAD_DIRECTORY, "Visualization")
WORKSPACE_DIRECTORY = os.path.join(os.getcwd(), "EP_APP_Workspace")
SIMULATION_FOLDERPATH = 'abc123'
SIMULATION_FOLDERNAME = 'abc123'
DATA_DIRECTORY =  os.path.join(os.getcwd(), "..", "..", "Data")

DATA_IDF_FILEPATH = None
DATA_WEATHER_FILEPATH = None

YOUR_VARIABLE_LIST = []
OUR_VARIABLE_LIST = ['Schedule Value',
                                  'Facility Total HVAC Electric Demand Power',
                                  'Site Diffuse Solar Radiation Rate per Area',
                                  'Site Direct Solar Radiation Rate per Area',
                                  'Site Outdoor Air Drybulb Temperature',
                                  'Site Solar Altitude Angle',
                                  'Surface Inside Face Internal Gains Radiation Heat Gain Rate',
                                  'Surface Inside Face Lights Radiation Heat Gain Rate',
                                  'Surface Inside Face Solar Radiation Heat Gain Rate',
                                  'Surface Inside Face Temperature',
                                  'Zone Windows Total Transmitted Solar Radiation Rate',
                                  'Zone Air Temperature',
                                  'Zone People Convective Heating Rate',
                                  'Zone Lights Convective Heating Rate',
                                  'Zone Electric Equipment Convective Heating Rate',
                                  'Zone Gas Equipment Convective Heating Rate',
                                  'Zone Other Equipment Convective Heating Rate',
                                  'Zone Hot Water Equipment Convective Heating Rate',
                                  'Zone Steam Equipment Convective Heating Rate',
                                  'Zone People Radiant Heating Rate',
                                  'Zone Lights Radiant Heating Rate',
                                  'Zone Electric Equipment Radiant Heating Rate',
                                  'Zone Gas Equipment Radiant Heating Rate',
                                  'Zone Other Equipment Radiant Heating Rate',
                                  'Zone Hot Water Equipment Radiant Heating Rate',
                                  'Zone Steam Equipment Radiant Heating Rate',
                                  'Zone Lights Visible Radiation Heating Rate',
                                  'Zone Total Internal Convective Heating Rate',
                                  'Zone Total Internal Radiant Heating Rate',
                                  'Zone Total Internal Total Heating Rate',
                                  'Zone Total Internal Visible Radiation Heating Rate',
                                  'Zone Air System Sensible Cooling Rate',
                                  'Zone Air System Sensible Heating Rate',
                                  'System Node Temperature',
                                  'System Node Mass Flow Rate']
SIMULATION_VARIABLE_LIST = []

SIMULATION_RESULTS_FOLDERPATH = None

# Tab Layout
tab_layout=[
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
                            value = [],
                            id = 'your_variable_selection',
                            multi = True,
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        html.Label("Preselected variables",
                            className = 'text-left ms-4 mt-0'),
                        dcc.Dropdown(options = OUR_VARIABLE_LIST,
                            multi = True,
                            value = [],
                            id = 'our_variable_selection',
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        dcc.RadioItems(
                            id = 'EPGen_Radiobutton_VariableSelection',
                            labelStyle = {'display': 'block'},
                            value = 0,
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

                        html.Button('Upload to Database',
                            id = 'EPGen_Button_UploadtoDb',
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

]

def EPGen_Radiobutton_DatabaseSelection_Interaction_Function(folder_name, database_selection):
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

def EPGen_Upload_IDF_Interaction_Function(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file(filename, content, UPLOAD_DIRECTORY)
        message = 'File Uploaded'

    else:
        message = 'Upload IDF file'

    return message

def EPGen_Upload_EPW_Interaction_Function(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file(filename, content, UPLOAD_DIRECTORY)
        message = 'File Uploaded'

    else:
        message = 'Upload EPW file'

    return message

def EPGen_Dropdown_EPVersion_Interaction_Function(version_selection):
    if version_selection != None :
        simulation_details = False
    else:
        simulation_details = True
    return simulation_details

def EPGen_Dropdown_Location_Interaction_Function(location_selection):
    if location_selection is None :
        simulation_details = True
    else:
        simulation_details = False
    return simulation_details

def EPGen_Dropdown_SimReportFreq_Interaction_Function(simReportFreq_selection):
    if simReportFreq_selection is not None:
        generate_variables = False
    else:
        generate_variables = True
    return generate_variables

# An error is occuring in this function near the bottom
def EPGen_RadioButton_EditSchedule_Interaction_Function(EPGen_Radiobutton_VariableSelection):

    initial_run_folder_path = os.path.join(SIMULATION_FOLDERPATH, 'Initial_run_folder')

    if not os.path.exists(initial_run_folder_path):
        os.mkdir(initial_run_folder_path)
        shutil.copy(DATA_IDF_FILEPATH, os.path.join(initial_run_folder_path, os.path.basename(DATA_IDF_FILEPATH)))
        shutil.copy(DATA_WEATHER_FILEPATH, os.path.join(initial_run_folder_path, os.path.basename(DATA_WEATHER_FILEPATH)))

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

def EPGen_Dropdown_DownloadSelection_Interaction_Function(download_selection):
    if download_selection != '' :
        final_download = False
    else:
        final_download = True
    return final_download

def EPGen_Dropdown_BuildingType_Interaction_Function(buildingType_selection):
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

def EPGen_Dropdown_SubLevel1_Interaction_Function(buildingType_selection, level_1):
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

def EPGen_Dropdown_SubLevel2_Interaction_Function(buildingType_selection, level_1, level_2):
    # Listing next sub level of folders
    if level_2 is not None:
        FilePath = os.path.join(os.getcwd(), "../../Data/", buildingType_selection, level_1, level_2)
        level_3_list = AppFuncs.list_contents(FilePath)
        level_3_list = [file for file in level_3_list if file.endswith('.idf')]

    else:
        level_3_list = []

    level_3_value = None

    return level_3_list, level_3_value

def Update_IDF_Weather_Files(buildingType, level1, level2, level3, location):

    global DATA_IDF_FILEPATH
    global DATA_WEATHER_FILEPATH

    if None in [buildingType, level1, level2, level3, location]:
     return None, None  # Wait until all inputs are present and selected

    idf_filepath = os.path.join(DATA_DIRECTORY, buildingType, level1, level2, level3)
    weather_subfolder = "TMY3_WeatherFiles_" + buildingType.split('_')[0]
    weather_filepath = os.path.join(DATA_DIRECTORY, weather_subfolder, location)

    if os.path.exists(idf_filepath):
        DATA_IDF_FILEPATH = idf_filepath
    if os.path.exists(weather_filepath):
        DATA_WEATHER_FILEPATH = weather_filepath

    return DATA_IDF_FILEPATH, DATA_WEATHER_FILEPATH

def EPGen_Button_GenerateVariables_Interaction_Function(database_selection, buildingType_selection, level_1, level_2, level_3, location_selection, n_clicks):

    global YOUR_VARIABLE_FILEPATH

    # Selecting IDF and Weather Files from Provided Dataset of PNNL Prototypes
    if database_selection == 1: # Our Database
        idf_filepath = os.path.join(DATA_DIRECTORY, buildingType_selection, level_1, level_2, level_3)
        weather_filepath = os.path.join(DATA_DIRECTORY, "TMY3_WeatherFiles_" + buildingType_selection.split('_')[0], location_selection)

    # Selecting Own IDF and Weather Files
    elif database_selection == 2:
        for item in os.listdir(UPLOAD_DIRECTORY):
            item_filepath = os.path.join(UPLOAD_DIRECTORY, item)
            if os.path.isfile(item_filepath):
                if item.endswith('.idf'): idf_filepath = item_filepath
                if item.endswith('.epw'): weather_filepath = item_filepath

    your_variable_selection = EP_Gen.generate_variables(idf_filepath, weather_filepath)
    YOUR_VARIABLE_LIST = your_variable_selection

    return your_variable_selection, OUR_VARIABLE_LIST

def update_simulation_variables_list(your_variable_selection, our_variable_selection, variable_selection_button):

    global SIMULATION_VARIABLE_LIST

    if variable_selection_button == 1: # Preselected Variables
        sim_variables_list = our_variable_selection
    elif variable_selection_button == 2: # Preselected Variables
        sim_variables_list = your_variable_selection
    else: sim_variables_list = []

    SIMULATION_VARIABLE_LIST = sim_variables_list


def EPGen_Dropdown_EditSchedule_Interaction_Function(people_schedules, equip_schedules, light_schedules, heating_schedules, cooling_schedules, temperature_schedules):
    if (not (people_schedules is None)) or (not (equip_schedules is None)) or (not (light_schedules is None)) or (not (heating_schedules is None)) or (not (cooling_schedules is None)) or (not (temperature_schedules is None)):
        update_selected_schedule = "Update selected schedule"
    else:
        update_selected_schedule = "Select single schedule"
    return update_selected_schedule

def EPGen_Button_UpdateSelectedSchedule_Interaction_Function(people_schedules, equip_schedules, light_schedules, heating_schedules, cooling_schedules, temperature_schedules, schedule_input, n_clicks):

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

def EPGen_RadioButton_EditSchedules_Interaction_2_Function(EPGen_Radiobutton_VariableSelection):

    if EPGen_Radiobutton_VariableSelection == 2:

        download_variables = False

    return download_variables

def EPGen_Button_DoneUpdatingSchedule_Interaction_Function(n_clicks):

    download_variables = False

    return download_variables

def EPGen_Checkbox_DownloadSelection_Interaction_Function(download_selection):

    if download_selection != '':

        final_download = False

    return final_download

def EPGen_Button_GenerateData_Interaction_Function(download_selection, start_date, end_date, Sim_TimeStep, Sim_OutputVariable_ReportingFrequency, n_clicks):

    global SIMULATION_RESULTS_FOLDERPATH

    print("generating_data")
    simulation_settings = {
        "name": SIMULATION_FOLDERNAME,
        "idf_year": 2013,
        "start_month": int(start_date.split("-")[1]),
        "start_day": int(start_date.split("-")[2]),
        "end_month": int(end_date.split("-")[1]),
        "end_day": int(end_date.split("-")[2]),
        "reporting_frequency": Sim_OutputVariable_ReportingFrequency,
        "timestep_minutes": Sim_TimeStep,
    }

    idf_filepath = DATA_IDF_FILEPATH
    weather_filepath = DATA_WEATHER_FILEPATH
    results_folderpath = EP_Gen.simulate_variables(DATA_IDF_FILEPATH, DATA_WEATHER_FILEPATH, variable_names=SIMULATION_VARIABLE_LIST, simulation_settings=simulation_settings)

    SIMULATION_RESULTS_FOLDERPATH = results_folderpath

    button_text = "Data Generated"
    return button_text

"""
def EPGen_Button_GenerateData_Interaction_Function(download_selection, start_date, end_date, Sim_TimeStep, Sim_OutputVariable_ReportingFrequency, Var_selection, your_vars, n_clicks):

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
"""

def EPGen_Button_DownloadFiles_Interaction_Function(download_selection, n_clicks):

    variables_pickle_filepath = os.path.join(SIMULATION_RESULTS_FOLDERPATH, "Sim_ProcessedData", "Output_Variables.pickle")
    eio_pickle_filepath = os.path.join(SIMULATION_RESULTS_FOLDERPATH, "Sim_ProcessedData", "eio.pickle")
    if download_selection == [1]:
        return dcc.send_file(variables_pickle_filepath)
    elif download_selection == [2]:
        return dcc.send_file(eio_pickle_filepath)

"""
def EPGen_Button_DownloadFiles_Interaction_Function(download_selection, n_clicks):

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
"""

def EPGen_Button_EndSession_Interaction_Function(n_clicks):

    for directory in os.listdir(WORKSPACE_DIRECTORY):

        shutil.rmtree(os.path.join(WORKSPACE_DIRECTORY, directory))

    return "Session Completed"
