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
from datetime import date, timedelta
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
import PSQLApp_Module as psql

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Data_Generation'))
import EP_DataGenerator_Script_v2_20250512 as data_generator
import EP_DataAggregation_v2_20250619 as data_aggregator

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Database'))
import Database_Creator as db_creator
import Data_Uploader as db_uploader

PRESELECTED_VARIABLES = data_generator.preselected_variables()
def preselected_variables(): return PRESELECTED_VARIABLES

########## Tab Layout ##########



tab_layout=[
    # Row 1
            dbc.Row([

                # Column 1
                dbc.Col([

                    html.Br(),

                    # Box 11 C1
                    html.Div([
                        dcc.Input(
                            id='generation_simulation_name',
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
                        id = 'data_source_selection',
                        labelStyle = {'display': 'block'},
                        value = '1',
                        options = [
                            {'label' : " PNNL Prototypical Buildings", 'value' : 1},
                            {'label' : " Upload Files", 'value' : 2},
                            {'label': " Default IDF and EPW", 'value': 3},
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
                            end_date=date(2020, 1, 2),
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
                                value='timestep',
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
                            id = 'custom_variable_selection',
                            multi = True,
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        html.Label("Preselected variables",
                            className = 'text-left ms-4 mt-0'),
                        dcc.Dropdown(options = PRESELECTED_VARIABLES,
                            multi = True,
                            value = [],
                            id = 'preselected_variable_selection',
                            style = {
                                'width':'95%',
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }),

                        dcc.RadioItems(
                            id = 'EPGen_Radiobutton_VariableSelection',
                            labelStyle = {'display': 'block'},
                            value = 1,
                            options = [
                                {'label' : " All Preselected Variables", 'value' : 1},
                                {'label' : " Select Variables", 'value' : 2}
                                ]  ,
                            className = 'ps-4 p-3',
                            style = {
                                'margin-left':'2.5%',
                                'margin-bottom':'5%'
                                }
                            ),

                        html.Div(
                            dcc.RadioItems(
                                id='edit_or_keep_schedules_button',
                                labelStyle={'display': 'block'},
                                value=2,
                                options=[
                                    {'label': " Edit Schedules", 'value': 1},
                                    {'label': " Keep Original Schedules", 'value': 2}
                                ],
                                className='ps-4 p-3',
                                style={
                                    'margin-left': '2.5%',
                                    'margin-bottom': '5%'
                                }
                            ),
                            id='EPGen_Div_EditSchedules',
                            hidden=False
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

                            html.Button('Load Selected Schedule',
                            id = 'load_schedule_button',
                            className = "btn btn-secondary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin':'5%'
                                },),

                        html.Button('Update Selected Schedule',
                            id = 'update_schedule_button',
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
                        dcc.Dropdown(['Commercial','Manufactured','Residential'], '',
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
                            id = 'upload_to_db_button',
                            hidden = True,
                            className = "btn btn-secondary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin':'5%'
                                },),

                        html.Button('Download Variables Pickle File',
                            id = 'download_variables_pickle_button',
                            hidden = True,
                            className = "btn btn-primary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin-left':'5%',
                                'margin-bottom':'5%'
                                },),
                        dcc.Download(id = 'download_variables_pickle'),

                        html.Button('Download Eio Pickle File',
                            id = 'download_eio_pickle_button',
                            hidden = True,
                            className = "btn btn-primary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin-left':'5%',
                                'margin-bottom':'5%'
                                },),
                        dcc.Download(id = 'download_eio_pickle'),

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

def pnnl_prototypes_dropdown(building_type, level1, level2, level3, location, data_folderpath, upload_folderpath):

    folderpath1 = os.path.join(data_folderpath, building_type + '_Prototypes')
    options1 = os.listdir(folderpath1)
    options2 = []
    options3 = []

    idf_filepath = None
    epw_filepath = None

    if os.path.exists(folderpath1) and level1:
        folderpath2 = os.path.join(folderpath1, level1)
        options2 = os.listdir(folderpath2)
        if os.path.exists(folderpath2) and level2:
            folderpath3 = os.path.join(folderpath2, level2)
            options3 = os.listdir(folderpath3)
            if os.path.exists(folderpath3) and level3:
                idf_filepath = os.path.join(folderpath3, level3)
                if os.path.exists(idf_filepath):
                    to_idf_filepath = os.path.join(upload_folderpath, os.path.basename(idf_filepath))
                    shutil.copy(idf_filepath, to_idf_filepath)

    weather_foldername = 'TMY3_WeatherFiles_' + building_type
    weather_folderpath = os.path.join(data_folderpath, weather_foldername)
    location_options = os.listdir(weather_folderpath)

    if location:
        epw_filepath = os.path.join(weather_folderpath, location)
        if os.path.exists(epw_filepath):
            to_epw_filepath = os.path.join(upload_folderpath, os.path.basename(epw_filepath))
            shutil.copy(epw_filepath, to_epw_filepath)

    return options1, options2, options3, location_options, idf_filepath, epw_filepath

def initial_run(idf_filepath, epw_filepath):
    rdd_filepath, eio_filepath = data_generator.initial_run(idf_filepath, epw_filepath)
    return rdd_filepath, eio_filepath

def generate_variables(idf_filepath, epw_filepath):
    rdd_filepath, eio_filepath = data_generator.initial_run(idf_filepath, epw_filepath)
    variables_list = data_generator.get_variable_list(rdd_filepath)
    return eio_filepath, rdd_filepath, variables_list

def get_schedules(eio_filepath, idf_filepath):

    Eio_OutputFile_Dict = AppFuncs.EPGen_eio_dict_generator(eio_filepath)

    People_Schedules = Eio_OutputFile_Dict['People Internal Gains Nominal']['Schedule Name'].tolist()
    People_Schedules = list(set(People_Schedules))

    Equip_Schedules = Eio_OutputFile_Dict['ElectricEquipment Internal Gains Nominal']['Schedule Name'].tolist()
    Equip_Schedules = list(set(Equip_Schedules))

    Light_Schedules = Eio_OutputFile_Dict['Lights Internal Gains Nominal']['Schedule Name'].tolist()
    Light_Schedules = list(set(Light_Schedules))

    # Load IDF File
    Current_IDFFile = op.Epm.load(idf_filepath)

    # Getting ThermalSetpoint items
    filtered_items = [item for item in dir(Current_IDFFile) if "ThermostatSetpoint" in item]
    ThermostatSetpoint_List = []
    for attr in filtered_items:
        if not attr.startswith('__'):
            value = getattr(Current_IDFFile, attr)
            ThermostatSetpoint_List.append(value)

    counter = -1
    ThermostatSetpoint_attribute_nameList = ['heating_setpoint_temperature_schedule_name',
                                             'cooling_setpoint_temperature_schedule_name',
                                             'setpoint_temperature_schedule_name']
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

    schedules = {
        "people_schedules": People_Schedules,
        "equipment_schedules": Equip_Schedules,
        "light_schedules": Light_Schedules,
        "heating_schedules": HeatingSetpoint_Schedules,
        "cooling_schedules": CoolingSetpoint_Schedules,
        "temperature_schedules": TemperatureSetpoint_Schedules,
    }

    return schedules

def schedule_compact_to_text(idf_filepath, schedule_name):

    idf = op.Epm.load(idf_filepath)
    schedule_compact = idf.Schedule_Compact
    current_schedule = schedule_compact.one(lambda x: x.name == schedule_name.lower())
    return str(current_schedule)

def text_to_schedule(text):

    lines = text.splitlines()
    lines = lines[1:] # Removes first line 'Schedule:Compact'
    clean_lines = [line.strip() for line in lines]

    new_schedule = {}

    for line in clean_lines:

        current_line_elements = line.split('!')
        current_value = current_line_elements[0].strip()
        if current_value[-1] == ',':
            current_value = current_value[:-1]

        current_key = current_line_elements[1].lower().strip().replace(' ', '_')
        new_schedule[current_key] = current_value

    return new_schedule

def delete_schedule(schedule_name, idf_filepath):

    with open(idf_filepath, 'r') as file:
        lines = file.readlines()

    new_lines = []
    skip_block = False
    found_target = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not skip_block and stripped.lower().startswith('schedule:compact'):
            # Peek ahead to see if the next line is the one we're deleting
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if schedule_name.lower() in next_line.lower().split(',')[0]:
                    # This is the block to delete — keep 'Schedule:Compact,' but skip lines until ;
                    found_target = True
                    skip_block = True
                    i += 2  # Skip schedule name line too
                    while i < len(lines):
                        if ';' in lines[i]:
                            i += 1
                            break
                        i += 1
                    continue  # Skip to next outer iteration without appending
        # If not skipping, add line
        new_lines.append(line)
        i += 1

    if found_target:
        with open(idf_filepath, 'w') as file:
            file.writelines(new_lines)

def replace_in_file(filepath, string1, string2):

    with open(filepath, 'r') as file:
        content = file.read()

    content = content.replace(string1, string2)

    with open(filepath, 'w') as file:
        file.write(content)

# Error: RecordDoesNotExistError('Queryset set contains no value.')
def update_schedule(idf_filepath, schedule_name, schedule_content):

    temporary_name = 'temporary_schedule_name'

    edited_idf = op.Epm.load(idf_filepath)
    schedule_compact = edited_idf.Schedule_Compact  # Contains All Schedule Tables
    new_schedule = text_to_schedule(schedule_content)

    new_name = new_schedule['name'].lower()
    new_schedule['name'] = temporary_name

    schedule_compact.add(new_schedule)
    edited_idf.save(idf_filepath)

    # Delete old Schedules
    delete_schedule(schedule_name, idf_filepath)
    replace_in_file(idf_filepath, schedule_name, new_name)
    replace_in_file(idf_filepath, temporary_name, new_name)

    # Make sure idf file still works
    edited_idf = op.Epm.load(idf_filepath)

def generate_data(idf_filepath, epw_filepath, simulation_settings, variable_names, results_folderpath):

    simulation_results_folderpath = data_generator.simulate_variables(idf_filepath, epw_filepath, simulation_settings, variable_names, results_folderpath)
    variables_pickle_filepath = os.path.join(simulation_results_folderpath, "Sim_ProcessedData", "Output_Variables.pickle")
    eio_pickle_filepath = os.path.join(simulation_results_folderpath, "Sim_ProcessedData", "eio.pickle")

    return variables_pickle_filepath, eio_pickle_filepath

def get_location_from_epw(epw_filepath):
    epw_filename = os.path.basename(epw_filepath).replace('.idf', '')
    location = epw_filename.split('_')[2].split('.')[0].split('-')[0]
    if location == 'San': location = 'SanDiego'
    if location == 'International': location = 'InternationalFalls'
    if location == 'Great': location = 'GreatFalls'
    if location == 'New': location = 'NewYork'
    if location == 'El': location = 'ElPaso'
    if location == 'Port': location = 'PortAngeles'
    return location


def upload_to_db(simulation_name, simulation_settings, variable_list, building_information, db_settings, variable_pickle_filepath, eio_pickle_filepath):

    all_zone_aggregation_pickle_filepath = data_aggregator.aggregate_data(variable_pickle_filepath, eio_pickle_filepath, variable_list)

    conn = psql.connect(db_settings)

    start_datetime = simulation_settings['start_datetime']
    start_datetime = start_datetime + timedelta(minutes=simulation_settings["timestep_minutes"])
    end_datetime = simulation_settings['end_datetime']
    end_datetime = end_datetime + timedelta(days=1)

    simulation_settings['start_datetime'] = start_datetime
    simulation_settings['end_datetime'] = end_datetime

    db_uploader.populate_datetimes_table(conn, base_time_resolution=1, start_datetime=start_datetime, end_datetime=end_datetime)

    if building_information['building_type'] == 'Custom':
        building_id = db_uploader.upload_custom_building(conn)
    else: building_id = db_uploader.get_building_id(conn, building_information)

    with open(all_zone_aggregation_pickle_filepath, "rb") as f: data_dict = pickle.load(f)
    epw_climate_zone = db_uploader.get_climate_zone(location=simulation_settings['epw_location'])
    time_resolution = simulation_settings["timestep_minutes"]
    zones_df = db_uploader.upload_time_series_data(conn, data_dict, simulation_name, simulation_settings, building_id, epw_climate_zone, time_resolution, aggregation_zones=None)

    return building_id, zones_df
