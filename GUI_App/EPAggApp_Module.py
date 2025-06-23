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

tab_layout =[
    
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
                            multi = True,
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

                        html.Button('Upload to Database',
                            id = 'EPAgg_Button_UploadtoDb',
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
            
]

def EPAgg_RadioButton_InputSelection_Interaction_Function(value):

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

def EPAgg_Upload_Pickle_Interaction_Function(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file(filename, content, UPLOAD_DIRECTORY_AGG_PICKLE)
        message = filename + ' uploaded successfully'

    else:
        message = 'Upload Pickled Variable file'

    variables_pickle_filepath = os.path.join(UPLOAD_DIRECTORY_AGG_PICKLE, filename)
    return message, variables_pickle_filepath

def EPAgg_Upload_EIO_Interaction_Function(filename, content):
    if filename is not None and content is not None:
        AppFuncs.save_file(filename, content, UPLOAD_DIRECTORY_AGG_EIO)
        message = filename + ' uploaded successfully'

    else:
        message = 'Upload EIO file'

    eio_pickle_filepath = os.path.join(UPLOAD_DIRECTORY_AGG_EIO, filename)
    return message, eio_pickle_filepath

def EPAgg_DropDown_AggregationVariables_Interaction_Function(selection, value):

    if selection == 1:

        div = False

    elif selection == 2:

        div = True

        if value != None:

            div = False

    else:

        div = True

    return div

def EPAgg_RadioButton_AggregationVariables_Interaction_Function(InputSelection, VariableSelection):

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

    pre_list = []

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

def EPAgg_DropDown_TypeOfAggregation_Interaction_Function(value):

    if value != None:

        div = False

    else:

        div = True

    return div

def EPAgg_Button_Aggregate_Interaction_Function(variable_selection, custom_variables, aggregate_to, custom_zone_list, Type_Aggregation, n_clicks):

    # Retrieing Aggregation Folder Path
    Aggregation_FolderPath = os.path.join(WORKSPACE_DIRECTORY, 'Aggregation')

    # Get Required Files from Sim_ProcessedData_FolderPath
    IDF_OutputVariable_Dict_file = open(os.path.join(Aggregation_FolderPath,'IDF_OutputVariables_DictDF.pickle'),"rb")

    IDF_OutputVariable_Dict = pickle.load(IDF_OutputVariable_Dict_file)

    Eio_OutputFile_Dict_file = open(os.path.join(Aggregation_FolderPath,'Eio_OutputFile.pickle'),"rb")

    Eio_OutputFile_Dict = pickle.load(Eio_OutputFile_Dict_file)

    # Getting variable selection for aggregation
    selected_variable_list = []

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

def EPAgg_Button_Download_Interaction_Function(n_clicks):
    download_path = []
    results_path = os.path.join(WORKSPACE_DIRECTORY, "Aggregation", "Results")

    for item in os.listdir(results_path):
        if item.endswith(".pickle"):
            download_path = os.path.join(results_path,item)
    return dcc.send_file(download_path)
