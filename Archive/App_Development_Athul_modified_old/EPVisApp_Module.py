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

def EPVis_RadioButton_DataSource_Interaction_Function(data_source):

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

def EPVis_Upload_GeneratedData_Interaction_Function(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file('Generated.pickle', content, UPLOAD_DIRECTORY_VIS)
        message = filename + ' uploaded successfully'

    else:
        message = 'Drag and Drop or Select Files for Generated Data'

    return message

def EPVis_Upload_AggregatedData_Interaction_Function(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file('Aggregated.pickle', content, UPLOAD_DIRECTORY_VIS)
        message = filename + ' uploaded successfully'
        data_selection = False
    else:
        message = 'Drag and Drop or Select Files for Aggregated Data'
        data_selection = True

    return message, data_selection

def EPVis_Radio_DataToBeSelected_Interaction_Function(InputSelection, selection):
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

def EPVis_Button_DistGeneratedData_Interaction_Function(table, column, n_clicks):
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

def EPVis_Button_DistAggregatedData_Interaction_Function(table, column, n_clicks):
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

def EPVis_Button_DistBothData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, n_clicks):
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

def EPVis_Button_ScatGeneratedData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, n_clicks):
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

def EPVis_Button_TimeGeneratedData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, n_clicks):
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


