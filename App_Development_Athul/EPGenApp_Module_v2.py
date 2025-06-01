"""
Created on Tue Jan 30 15:32:25 2024

@author: Athul Jose P
"""

# Importing Required Modules
import shutil
import os
import sys
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
from Data_Generation.EP_DataGenerator_Script_v2_20250512 import TEMPORARY_FOLDERPATH

THIS_SCRIPT_DIR = os.path.dirname(__file__)
EP_GEN_DIR = os.path.abspath(os.path.join(THIS_SCRIPT_DIR, '..', 'Data_Generation'))
sys.path.append(EP_GEN_DIR)
import EP_DataGenerator_Script_v2_20250512 as EP_Gen

UPLOAD_DIRECTORY = os.path.join(os.getcwd(), "EP_APP_Uploads")
UPLOAD_DIRECTORY_AGG_PICKLE = os.path.join(UPLOAD_DIRECTORY, "Pickle_Upload")
UPLOAD_DIRECTORY_AGG_EIO = os.path.join(UPLOAD_DIRECTORY, "EIO_Upload")
UPLOAD_DIRECTORY_VIS = os.path.join(UPLOAD_DIRECTORY, "Visualization")
WORKSPACE_DIRECTORY = os.path.join(os.getcwd(), "EP_APP_Workspace")

TEMPORARY_FOLDERPATH = os.path.join(THIS_SCRIPT_DIR, "..", 'Data_Generation', 'Temporary Folder')

SIMULATION_FOLDERNAME = 'abc123'

#DATA_DIRECTORY =  os.path.join(THIS_SCRIPT_DIR, "..", "Data")
DATA_DIRECTORY =  r"D:\Building_Modeling_Code\Data"

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
# Passed

def EPGen_Upload_EPW_Interaction_Function(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file(filename, content, UPLOAD_DIRECTORY)
        message = 'File Uploaded'

    else:
        message = 'Upload EPW file'

    return message
# Passed

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

def EPGen_RadioButton_EditSchedule_Interaction_Function(EPGen_Radiobutton_VariableSelection):

    initial_run_folder_path = os.path.join(TEMPORARY_FOLDERPATH, 'initial_run')

    if EPGen_Radiobutton_VariableSelection == 1:
        schedules = False
        eio_FilePath = os.path.join(initial_run_folder_path, "eplusout.eio")

        Eio_OutputFile_Dict = EP_Gen.parse_eio_file(eio_FilePath)

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

"""
def EPGen_RadioButton_EditSchedule_Interaction_Function(EPGen_Radiobutton_VariableSelection):
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
"""

def EPGen_Dropdown_DownloadSelection_Interaction_Function(download_selection):
    if download_selection != '' :
        final_download = False
    else:
        final_download = True
    return final_download

def EPGen_Dropdown_BuildingType_Interaction_Function(buildingType_selection):
    # Listing next sub level of folders
    if buildingType_selection is not None:
        FilePath = os.path.join(DATA_DIRECTORY, buildingType_selection)
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
        FilePath = os.path.join(DATA_DIRECTORY, buildingType_selection, level_1)
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
        FilePath = os.path.join(DATA_DIRECTORY, buildingType_selection, level_1, level_2)
        level_3_list = AppFuncs.list_contents(FilePath)
        level_3_list = [file for file in level_3_list if file.endswith('.idf')]

    else:
        level_3_list = []

    level_3_value = None

    return level_3_list, level_3_value

def EPGen_Button_GenerateVariables_Interaction_Function(database_selection, buildingType_selection, level_1, level_2, level_3, location_selection, n_clicks):

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

    return your_variable_selection, OUR_VARIABLE_LIST

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

def EPGen_Button_EndSession_Interaction_Function(n_clicks):

    for directory in os.listdir(WORKSPACE_DIRECTORY):

        shutil.rmtree(os.path.join(WORKSPACE_DIRECTORY, directory))

    return "Session Completed"
