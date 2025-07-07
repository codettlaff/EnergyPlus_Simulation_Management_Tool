
# External Modules
import os
import pandas as pd
import numpy as np
import pickle
import datetime
import copy

def aggregate_data(variables_pickle_filepath, eio_pickle_filepath, simulation_variable_list, aggregation_type=1, aggregation_zone_list='all_zones'):

    # Read Pickle Files
    with open(variables_pickle_filepath, "rb") as f1: IDF_OutputVariable_Dict = pickle.load(f1)
    with open(eio_pickle_filepath, "rb") as f2: Eio_OutputFile_Dict = pickle.load(f2)

    zone_list = Eio_OutputFile_Dict['Zone Information']['Zone Name'].tolist()

    if aggregation_zone_list == 'all_zones':
        Aggregation_Zone_List = [[item] for item in zone_list]
        Aggregation_File_Name = 'Aggregation_Dict_AllZones.pickle'
    elif aggregation_zone_list == 'one_zone':
        Aggregation_Zone_List = [zone_list]
        Aggregation_File_Name = 'Aggregation_Dict_OneZone.pickle'
    else:
        Aggregation_File_Name = 'Aggregation_Dict_Custom.pickle'

    Aggregation_Zone_NameStem = 'Aggregation_Zone'

    SystemNode_Name = 'DIRECT AIR INLET NODE'

    DateTime_List = IDF_OutputVariable_Dict['DateTime_List']

    # =============================================================================
    # Creating Unique Zone Name List and Associated Areas and Volume Dicts
    # =============================================================================

    # Creating Unique List of Zones
    Total_Zone_List = zone_list

    # Creating Unique Zone List
    Unique_Zone_List = list(set(Total_Zone_List))

    # IF ELSE LOOP: For cheking aggregation_type
    if (aggregation_type == 1):  # Normal Aggregation

        # Do nothing
        Do_Nothing = 0

    elif (aggregation_type == 2):  # Weighted Area Aggregation

        # Initializing Unique_Zone_Area_Dict and Unique_Zone_Volume_Dict
        Unique_Zone_Area_Dict = {}

        # Getiing Zone Area and Volumes from Eio_OutputFile_Dict

        # FOR LOOP: For each element of Unique_Zone_List
        for Unique_Zone in Unique_Zone_List:
            Unique_Zone_Area_Dict[Unique_Zone] = float(
                Eio_OutputFile_Dict['Zone Information'].query('`Zone Name` == Unique_Zone')['Floor Area {m2}'])

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

    elif (aggregation_type == 3):  # Weighted Volume Aggregation

        # Initializing Unique_Zone_Area_Dict and Unique_Zone_Volume_Dict
        Unique_Zone_Volume_Dict = {}

        # Getiing Zone Area and Volumes from Eio_OutputFile_Dict

        # FOR LOOP: For each element of Unique_Zone_List
        for Unique_Zone in Unique_Zone_List:
            Unique_Zone_Volume_Dict[Unique_Zone] = float(
                Eio_OutputFile_Dict['Zone Information'].query('`Zone Name` == Unique_Zone')['Volume {m3}'])

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
    Equipment_List = ['People', 'Lights', 'ElectricEquipment', 'GasEquipment', 'OtherEquipment',
                      'HotWaterEquipment', 'SteamEquipment']

    # Initializing Aggregation_DF
    Aggregation_DF = pd.DataFrame()

    # FOR LOOP: For each Variable Name in Aggregation_VariableNames_List
    for key in simulation_variable_list:

        # IF LOOP: For the Variable Name Schedule_Value_
        if (key == 'Schedule Value'):  # Create Schedule Columns which are needed

            # FOR LOOP: For each element in Equipment_List
            for element in Equipment_List:

                # Creating Current_EIO_Dict_Key
                Current_EIO_Dict_Key = element + ' ' + 'Internal Gains Nominal'

                # IF LOOP: To check if Current_EIO_Dict_Key is present in Eio_OutputFile_Dict
                if (Current_EIO_Dict_Key in Eio_OutputFile_Dict):  # Key present in Eio_OutputFile_Dict

                    # Creating key1 for column Name
                    key1 = key + ' ' + element

                    # Initializing Aggregation_Dict with None
                    Aggregation_DF[key1] = None

        else:  # For all other Columns

            # Initializing Aggregation_Dict with None
            Aggregation_DF[key] = None

    # Initializing Aggregation_DF_Equipment
    Aggregation_DF_Equipment = pd.DataFrame()

    # FOR LOOP: For each element in Equipment_List
    for element in Equipment_List:

        # Creating Current_EIO_Dict_Key
        Current_EIO_Dict_Key = element + ' ' + 'Internal Gains Nominal'

        # IF LOOP: To check if Current_EIO_Dict_Key is present in Eio_OutputFile_Dict
        if (Current_EIO_Dict_Key in Eio_OutputFile_Dict):  # Key present in Eio_OutputFile_Dict

            # Creating key1 for column Name
            key1 = element + '_Level'

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

        if aggregation_zone_list == 'all_zones':
            Aggregated_Zone_Name_1 = element[0].strip()
            Aggregated_Zone_Name_2 = Aggregated_Zone_Name_1 + "_Equipment"
        elif aggregation_zone_list == 'one_zone':
            Aggregated_Zone_Name_1 = 'Aggregated_Zone'
            Aggregated_Zone_Name_2 = Aggregated_Zone_Name_1 + "_Equipment"
        else:
            Aggregated_Zone_Name_1 = Aggregation_Zone_NameStem + "_" + str(Counter)
            Aggregated_Zone_Name_2 = Aggregation_Zone_NameStem + "_Equipment_" + str(Counter)

        # Appending empty Aggregation_DF to Aggregation_Dict
        Aggregation_Dict[Aggregated_Zone_Name_1] = copy.deepcopy(Aggregation_DF)
        Aggregation_Dict[Aggregated_Zone_Name_2] = copy.deepcopy(Aggregation_DF_Equipment)

        # FOR LOOP: For each Aggregation_VariableName in Aggregation_VariableNames_List
        for variable_name in Aggregation_Dict[Aggregated_Zone_Name_1].columns:

            # Getting Current_Aggregation_Variable Type
            Current_Aggregation_Variable_Type = variable_name.split(' ')[0]

            # Aggregation Based on Current_Aggregation_Variable_Type
            if (Current_Aggregation_Variable_Type == 'Site' or Current_Aggregation_Variable_Type == 'Facility'):  # Site

                # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                Current_Aggregation_Variable = IDF_OutputVariable_Dict[variable_name]

                # Filling Aggregation_Dict with Current_Aggregation_Variable
                Aggregation_Dict[Aggregated_Zone_Name_1][variable_name] = Current_Aggregation_Variable.iloc[:, [0]]

            elif (Current_Aggregation_Variable_Type == 'Zone'):  # Zone

                if variable_name[:-1] in IDF_OutputVariable_Dict.keys():
                    # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                    Current_Aggregation_Variable = IDF_OutputVariable_Dict[variable_name[:-1]]

                    # Getting Dataframe subset based on element
                    Current_DF_Cols_Desired = []

                    #  Getting Current_Aggregation_Variable_ColName_List
                    Current_Aggregation_Variable_ColName_List = Current_Aggregation_Variable.columns

                    # FOR LOOP: For each element in element
                    for ColName1 in element:

                        # FOR LOOP: For each element in Current_Aggregation_Variable_ColName_List
                        for ColName2 in Current_Aggregation_Variable_ColName_List:

                            # IF LOOP: For checking presence of ColName1 in ColName2
                            if (ColName2.find(ColName1) >= 0):  # ColName1 present in ColName2

                                # Appending ColName2 to Current_DF_Cols_Desired
                                Current_DF_Cols_Desired.append(ColName2)

                                # IF ELSE LOOP: For aggregation_type
                                if (aggregation_type == 1):  # Normal Aggregation

                                    # Do Nothing
                                    Do_Nothing = 0

                                elif (aggregation_type == 2):  # Weighted Area Aggregation

                                    # Aggregate by Area
                                    Current_Aggregation_Variable[ColName2] = Unique_Zone_Area_Dict[ColName1] * \
                                                                             Current_Aggregation_Variable[ColName2]

                                elif (aggregation_type == 3):  # Weighted Volume Aggregation

                                    # Aggregate by Volume
                                    Current_Aggregation_Variable[ColName2] = Unique_Zone_Volume_Dict[ColName1] * \
                                                                             Current_Aggregation_Variable[ColName2]

                    # IF ELSE LOOP: For aggregating according to aggregation_type and storing in Aggregation_Dict
                    if (aggregation_type == 1):  # Normal Aggregation

                        # Filling Aggregation_Dict with Current_Aggregation_Variable
                        Aggregation_Dict[Aggregated_Zone_Name_1][variable_name] = \
                        Current_Aggregation_Variable[Current_DF_Cols_Desired].mean(1)

                    elif (aggregation_type == 2):  # Weighted Area Aggregation

                        # Filling Aggregation_Dict with Current_Aggregation_Variable
                        Aggregation_Dict[Aggregated_Zone_Name_1][variable_name] = (
                                                                                                         Current_Aggregation_Variable[
                                                                                                             Current_DF_Cols_Desired].sum(
                                                                                                             1)) / (
                                                                                                     Zone_TotalArea_List[
                                                                                                         Counter])

                    elif (aggregation_type == 3):  # Weighted Volume Aggregation

                        # Filling Aggregation_Dict with Current_Aggregation_Variable
                        Aggregation_Dict[Aggregated_Zone_Name_1][variable_name] = (
                                                                                                         Current_Aggregation_Variable[
                                                                                                             Current_DF_Cols_Desired].sum(
                                                                                                             1)) / (
                                                                                                     Zone_TotalVolume_List[
                                                                                                         Counter])

            elif (Current_Aggregation_Variable_Type == 'Surface'):  # Surface

                try:
                    # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                    Current_Aggregation_Variable = IDF_OutputVariable_Dict[variable_name[:-1]]

                except KeyError:
                    # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                    Current_Aggregation_Variable = IDF_OutputVariable_Dict[
                        variable_name[:-1] + ".csv"]

                # Getting Dataframe subset based on element
                Current_DF_Cols_Desired = []

                # Initializing Current_DF
                Current_DF = pd.DataFrame()

                #  Getting Current_Aggregation_Variable_ColName_List
                Current_Aggregation_Variable_ColName_List = Current_Aggregation_Variable.columns

                # FOR LOOP: For each element in element
                for ColName1 in element:

                    # FOR LOOP: For each element in Current_Aggregation_Variable_ColName_List
                    for ColName2 in Current_Aggregation_Variable_ColName_List:

                        # IF LOOP: For checking presence of ColName1 in ColName2
                        if (ColName2.find(ColName1) >= 0):  # ColName1 present in ColName2

                            # Appending ColName2 to Current_DF_Cols_Desired
                            Current_DF_Cols_Desired.append(ColName2)

                            # IF ELSE LOOP: For aggregation_type
                            if (aggregation_type == 1):  # Normal Aggregation

                                # Do Nothing
                                Do_Nothing = 0

                            elif (aggregation_type == 2):  # Weighted Area Aggregation

                                # Aggregate by Area
                                Current_Aggregation_Variable[ColName2] = Unique_Zone_Area_Dict[ColName1] * \
                                                                         Current_Aggregation_Variable[ColName2]

                            elif (aggregation_type == 3):  # Weighted Volume Aggregation

                                # Aggregate by Volume
                                Current_Aggregation_Variable[ColName2] = Unique_Zone_Volume_Dict[ColName1] * \
                                                                         Current_Aggregation_Variable[ColName2]

                    # IF ELSE LOOP: For filling Up Current_DF according to variable_name
                    if ((variable_name.find('Heat') >= 0) or (
                            variable_name.find('Gain') >= 0) or (
                            variable_name.find('Rate') >= 0) or (
                            variable_name.find('Power') >= 0) or (
                            variable_name.find('Energy') >= 0)):  # Its an additive Variable

                        # Adding Column to Current_DF
                        Current_DF[ColName1] = Current_Aggregation_Variable[Current_DF_Cols_Desired].sum(1)

                    else:  # It's a mean Variable

                        # Addding Column to Current_DF
                        Current_DF[ColName1] = Current_Aggregation_Variable[Current_DF_Cols_Desired].mean(1)

                # IF ELSE LOOP: For aggregating according to aggregation_type and storing in Aggregation_Dict
                if (aggregation_type == 1):  # Normal Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][variable_name] = Current_DF[
                        element].mean(1)

                elif (aggregation_type == 2):  # Weighted Area Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][variable_name] = (Current_DF[
                                                                                                      element].sum(
                        1)) / (Zone_TotalArea_List[Counter])

                elif (aggregation_type == 3):  # Weighted Volume Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][variable_name] = (Current_DF[
                                                                                                      element].sum(
                        1)) / (Zone_TotalVolume_List[Counter])


            elif (Current_Aggregation_Variable_Type == 'System'):  # System Node

                try:
                    # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                    Current_Aggregation_Variable = IDF_OutputVariable_Dict[variable_name[:-1]]

                except KeyError:
                    # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                    Current_Aggregation_Variable = IDF_OutputVariable_Dict[
                        variable_name[:-1] + ".csv"]

                # Getting Dataframe subset based on element
                Current_DF_Cols_Desired = []

                #  Getting Current_Aggregation_Variable_ColName_List
                Current_Aggregation_Variable_ColName_List = Current_Aggregation_Variable.columns

                # FOR LOOP: For each element in element
                for ColName1 in element:

                    # FOR LOOP: For each element in Current_Aggregation_Variable_ColName_List
                    for ColName2 in Current_Aggregation_Variable_ColName_List:

                        # IF LOOP: For checking presence of ColName1 in ColName2
                        if ((ColName2.find(ColName1) >= 0) and (
                                ColName2.find(SystemNode_Name) >= 0)):  # ColName1 present in ColName2

                            # Appending ColName2 to Current_DF_Cols_Desired
                            Current_DF_Cols_Desired.append(ColName2)

                            # IF ELSE LOOP: For aggregation_type
                            if (aggregation_type == 1):  # Normal Aggregation

                                # Do Nothing
                                Do_Nothing = 0

                            elif (aggregation_type == 2):  # Weighted Area Aggregation

                                # Aggregate by Area
                                Current_Aggregation_Variable[ColName2] = Unique_Zone_Area_Dict[ColName1] * \
                                                                         Current_Aggregation_Variable[ColName2]

                            elif (aggregation_type == 3):  # Weighted Volume Aggregation

                                # Aggregate by Volume
                                Current_Aggregation_Variable[ColName2] = Unique_Zone_Volume_Dict[ColName1] * \
                                                                         Current_Aggregation_Variable[ColName2]

                # IF ELSE LOOP: For aggregating according to aggregation_type and storing in Aggregation_Dict
                if (aggregation_type == 1):  # Normal Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][variable_name] = \
                    Current_Aggregation_Variable[Current_DF_Cols_Desired].mean(1)

                elif (aggregation_type == 2):  # Weighted Area Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][variable_name] = (
                                                                                                     Current_Aggregation_Variable[
                                                                                                         Current_DF_Cols_Desired].sum(
                                                                                                         1)) / (
                                                                                                 Zone_TotalArea_List[
                                                                                                     Counter])

                elif (aggregation_type == 3):  # Weighted Volume Aggregation

                    # Filling Aggregation_Dict with Current_Aggregation_Variable
                    Aggregation_Dict[Aggregated_Zone_Name_1][variable_name] = (
                                                                                                     Current_Aggregation_Variable[
                                                                                                         Current_DF_Cols_Desired].sum(
                                                                                                         1)) / (
                                                                                                 Zone_TotalVolume_List[
                                                                                                     Counter])


            elif (Current_Aggregation_Variable_Type == 'Schedule'):  # Schedule

                try:

                    # Getting Dataframe subset based on element
                    Current_DF_Cols_Desired = []

                    # Create a CurrentLevel_List
                    CurrentLevel_List = []

                    # Creating Current_VariableName_1
                    Current_Aggregation_VariableName_1 = variable_name.split(' ')[0] + ' ' + variable_name.split(' ')[1]

                    # Get Current_Element
                    Current_Element = variable_name.split(' ')[2]

                    # Creating Current_EIO_Dict_Key
                    Current_EIO_Dict_Key = Current_Element + ' ' + 'Internal Gains Nominal'

                    # Creating Current_EIO_Dict_Key
                    Current_EIO_Dict_Key_Level = Current_Element + '_' + 'Level'

                    # IF ELSE LOOP: For creating Current_EIO_Dict_Key_Level_ColName based on Current_Element
                    if (Current_Element == 'People'):  # People

                        Current_EIO_Dict_Key_Level_ColName = 'Number of People {}'

                    elif (Current_Element == 'Lights'):  # Lights

                        Current_EIO_Dict_Key_Level_ColName = 'Lighting Level {W}'

                    else:  # ElectricEquipment, OtherEquipment, HotWaterEquipment, SteamEquipment

                        Current_EIO_Dict_Key_Level_ColName = 'Equipment Level {W}'

                    # Getting Current_EIO_Dict_DF
                    Current_EIO_Dict_DF = Eio_OutputFile_Dict[Current_EIO_Dict_Key]

                    # Getting Current_Aggregation_Variable from IDF_OutputVariable_Dict
                    Current_Aggregation_Variable = IDF_OutputVariable_Dict[Current_Aggregation_VariableName_1]

                    #  Getting Current_Aggregation_Variable_ColName_List
                    Current_Aggregation_Variable_ColName_List = Current_Aggregation_Variable.columns

                    # FOR LOOP: For each element in element
                    for ColName1 in element:

                        # element should only be only be 2D

                        # Getting ColName2 from the 'Schedule Name' Column of Current_EIO_Dict_DF
                        # need to remove duplicates from Current_EIO_Dict_DF['Zone Name']
                        Current_EIO_Dict_DF = Current_EIO_Dict_DF.drop_duplicates(subset=["Zone Name"], keep='last')

                        # Un-Elegant Solution: when we run into non-thermal zones, we skip them.
                        try:
                            ColName2 = str(
                                Current_EIO_Dict_DF[Current_EIO_Dict_DF['Zone Name'] == ColName1.strip()]['Schedule Name'].iloc[
                                    0])
                            # Appending ColName2 to Current_DF_Cols_Desired
                            Current_DF_Cols_Desired.append(ColName2)

                            # Getting Equipment Level
                            Current_EquipmentLevel = float(
                                Current_EIO_Dict_DF[Current_EIO_Dict_DF['Zone Name'] == ColName1.strip()][
                                    Current_EIO_Dict_Key_Level_ColName].iloc[0])

                            # Appending Current_EquipmentLevel to CurrentLevel_List
                            CurrentLevel_List.append(Current_EquipmentLevel)

                        except(IndexError):

                            print(10 * ' ' + ColName1 + ' Not a Thermal Zone\n')

                    # FOR LOOP: Getting Corrected Current_DF_Cols_Desired
                    Current_DF_Cols_Desired_Corrected = []

                    for ColName3 in Current_DF_Cols_Desired:
                        for ColName4 in Current_Aggregation_Variable.columns:
                            if (ColName4.find(
                                ColName3) >= 0):                        Current_DF_Cols_Desired_Corrected.append(
                                ColName4)

                    # Filling Aggregation_Dict with Current_Aggregation_Variable and Current_EIO_Dict_Key_Level
                    Aggregation_Dict[Aggregated_Zone_Name_1][variable_name] = (
                        Current_Aggregation_Variable[Current_DF_Cols_Desired_Corrected]
                        .mean(axis=1)
                        .fillna(0.0)
                    )

                    Aggregation_Dict[Aggregated_Zone_Name_2][Current_EIO_Dict_Key_Level] = pd.DataFrame(np.array([sum(CurrentLevel_List) / len(CurrentLevel_List)]))

                except Exception as e:
                    print(e)

            # else: # Any other Variable

    # =============================================================================
    # Creating Sim_AggregatedData Folder
    # =============================================================================

    simulation_results_folderpath = os.path.join(variables_pickle_filepath, '..', '..')
    aggregation_folderpath = os.path.join(simulation_results_folderpath, 'Sim_Aggregated_Data')
    aggregation_pickle_filepath = os.path.join(aggregation_folderpath, Aggregation_File_Name)
    if not os.path.exists(aggregation_folderpath): os.makedirs(aggregation_folderpath)
    pickle.dump(Aggregation_Dict, open(aggregation_pickle_filepath, "wb"))

    return aggregation_pickle_filepath