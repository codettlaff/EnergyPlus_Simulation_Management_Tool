"""
Created on Tue Jan 30 15:32:25 2024

@author: Athul Jose P

main function of web app
"""

# Importing Required Modules
import os
import re
import shutil
import pickle
import copy
import datetime
from datetime import date

import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import opyplus as op

# Importing User-Defined Modules
import MyDashApp_Module as AppFuncs
import EPGenApp_Module as EPGen
import EPAggApp_Module as EPAgg
import EPVisApp_Module as EPVis
import PSQLApp_Module as PSQL

# Directory Paths
UPLOAD_DIRECTORY = os.path.join(os.getcwd(), "EP_APP_Uploads")
UPLOAD_DIRECTORY_AGG_PICKLE = os.path.join(UPLOAD_DIRECTORY, "Pickle_Upload")
UPLOAD_DIRECTORY_AGG_EIO = os.path.join(UPLOAD_DIRECTORY, "EIO_Upload")
UPLOAD_DIRECTORY_VIS = os.path.join(UPLOAD_DIRECTORY, "Visualization")
WORKSPACE_DIRECTORY = os.path.join(os.getcwd(), "EP_APP_Workspace")

# Simulation Configuration
SIMULATION_FOLDERPATH = 'abc123'
SIMULATION_FOLDERNAME = 'abc123'

# Data Directory
DATA_DIRECTORY = os.path.join(os.getcwd(), "..", "..", "Data")

# Pre Selected Variables
OUR_VARIABLE_LIST = [
    'Schedule_Value_',
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
    'System_Node_Mass_Flow_Rate_'
]

# Instantiate our App and incorporate BOOTSTRAP theme Stylesheet
# Themes - https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/#available-themes
# Themes - https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/
# hackerthemes.com/bootstrap-cheatsheet/
app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])

# App Layout using Dash Bootstrap
app.layout = dbc.Container([

    dbc.Row([
        html.H1(
            "EnergyPlus Simulation Management Tool",
            className = 'text-center text-primary mb-4'
        )
    ]),

    dcc.Tabs([
        # postgreSQL Tab
        dcc.Tab(
            label='PostgreSQL',
            className='text-center text-primary mb-4',
            children=PSQL.tab_layout
        ),

        # EP Generation Tab
        dcc.Tab(
            label='EP Generation',
            className = 'text-center text-primary mb-4',
            children=EPGen.tab_layout
        ),

        # EP Aggregation Tab
        dcc.Tab(
            label = 'Aggregation',
            className = 'text-center text-primary mb-4',
            children = EPAgg.tab_layout
        ),

        # EP Visualization Tab
        dcc.Tab(
            label = 'Visualization & Analysis',
            className = 'text-center text-primary mb-4',
            children = EPVis.tab_layout
        )
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
    date_range1, date_range2, var_gendata, var_aggrdata, button_dist_gen, button_dist_agg, button_dist_both, mean_gen, mean_agg, button_scat_both, button_time_gen, button_time_agg, button_time_both, min_date_upload, max_date_upload, min_date_upload, max_date_upload, min_date_upload, max_date_upload, Generated_Variables, Aggregated_Variables = EPVis.EPVis_Radio_DataToBeSelected_Interaction_Function(InputSelection, selection)
    return date_range1, date_range2, var_gendata, var_aggrdata, button_dist_gen, button_dist_agg, button_dist_both, mean_gen, mean_agg, button_scat_both, button_time_gen, button_time_agg, button_time_both, min_date_upload, max_date_upload, min_date_upload, max_date_upload, min_date_upload, max_date_upload, Generated_Variables, Aggregated_Variables

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
    Input(component_id = 'EPVis_Button_ScatterBothData', component_property = 'n_clicks'),
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

@app.callback(
    Output(component_id = 'EPVis_Graph_TimeSeries', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_TimeAggregatedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_TimeAggregatedData_Interaction(table_gen, column_gen, table_agg, column_agg, n_clicks):
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
@app.callback(
    Output(component_id = 'PSQL_Div_CreateSelectDatabase', component_property = 'hidden'),
    Input(component_id = 'PSQL_RadioButton_UsingDatabase', component_property = 'value'),
    prevent_initial_call = True)
def PSQL_Radiobutton_UsingDatabase_Interaction(selection):
    database_selection = PSQL.PSQL_Radiobutton_UsingDatabase_Interaction_Function(selection)
    return database_selection

@app.callback(
    Output(component_id = 'PSQL_Div_EnterInfo', component_property = 'hidden'),
    Output(component_id = 'PSQL_Div_SelectDbfromExist', component_property = 'hidden'),
    Input(component_id = 'PSQL_RadioButton_CreateSelectDatabase', component_property = 'value'),
    prevent_initial_call = True)
def PSQL_Radiobutton_CreateSelectDatabase_Interaction(selection):
    enterinfo_hidden, existdblist_hidden = PSQL.PSQL_Radiobutton_CreateSelectDatabase_Interaction_Function(selection)
    return enterinfo_hidden, existdblist_hidden

### Casey's Code ###

@app.callback(
    Output('PSQL_Div_EnterInfo', 'children'),  # You can also use a different feedback div
    Input('PSQL_Button_CreateDatabase', 'n_clicks'),
    State('PSQL_Textarea_Username', 'value'),
    State('PSQL_Textarea_Password', 'value'),
    State('PSQL_Textarea_PortNumber', 'value'),
    State('PSQL_Textarea_DbName', 'value'),
    prevent_initial_call=True
)
def on_create_database(n_clicks, username, password, port, dbname):
    print(f"Creating database {dbname}\n Username: {username}\n Password: {password}\n Port: {port}")
    conn = PSQL.create_database(username, password, port, dbname)

@app.callback(
    Output('PSQL_Dropdown_ExistDbList', 'options'),
    Input('PSQL_RadioButton_CreateSelectDatabase', 'value'),
    prevent_initial_call=True
)
def populate_existing_db_dropdown(selection):
    dropdown_options = PSQL.populate_existing_db_dropdown(selection)
    return dropdown_options

# Running the App
if __name__ == '__main__':
    app.run(port=4050)


