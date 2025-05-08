# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 15:32:25 2024

@author: Ninad Gaikwad
"""

# Importing Desired Modules
import numpy as np
import pandas as pd
import os
import shutil
import base64
import re
import zlib
import zipfile



# My App Module

def CreateTimeVector(TimeDuration, TimeStep):
    
    TimeVector = np.arange(0, TimeDuration, TimeStep)
    
    TimeVector = np.reshape(TimeVector,(TimeVector.shape[0],1))
    
    return TimeVector

def CreateSine(TimeVector, A, F, P):
    
    Sine = A*np.sin(2*np.pi*F*TimeVector+np.radians(P))
    
    return Sine
    
def Compute_with_Sines(TimeVector, Sine1, Sine2, Computation_Option):
    
    # omputing new Sine Wave
    
    if (Computation_Option == 1): # Addition
    
        Sine_New = Sine1 + Sine2
    
    elif (Computation_Option == 2): # Subtraction
    
        Sine_New = Sine1 - Sine2
    
    elif (Computation_Option == 3): # Multiplication
    
        Sine_New = Sine1 * Sine2
        
    # Creating a Combined Table for Graphing purposes
    Combined_Array = np.hstack((TimeVector, Sine1, Sine2, Sine_New))
    
    Sines_DF = pd.DataFrame(Combined_Array, columns = ['Time','Sine_1','Sine_2','Sine_New'])
    
    return Sines_DF



def create_simulation_folder(simName_FilePath, IDF_FilePath, Weather_FilePath):
    # Create the main folder
    os.makedirs(simName_FilePath, exist_ok=True)
    
    # Create the Temporary Folder inside the main folder
    temp_folder = os.path.join(simName_FilePath, "Temporary Folder")
    os.makedirs(temp_folder, exist_ok=True)
    
    # Copy the IDF file to the Temporary Folder
    if os.path.isfile(IDF_FilePath):
        shutil.copy(IDF_FilePath, temp_folder)
    else:
        print(f"IDF file not found: {IDF_FilePath}")
    
    # Copy the Weather file to the Temporary Folder
    if os.path.isfile(Weather_FilePath):
        shutil.copy(Weather_FilePath, temp_folder)
    else:
        print(f"Weather file not found: {Weather_FilePath}")
    
    print(f"Files copied to {temp_folder}")

# function for saving the uploaded file
def save_file(name, content,UPLOAD_DIRECTORY):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]

    # Saving file to directory
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))

# function for getting directory
def list_contents(folder_directory):
    contents = os.listdir(folder_directory)
    return contents

# function for 
def EPGen_eio_dict_generator(Eio_OutputFile_Path):

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

    return Eio_OutputFile_Dict


def compress(file_names, path):
    print("File Paths:")
    print(file_names)

    # Select the compression mode ZIP_DEFLATED for compression
    # or zipfile.ZIP_STORED to just store the file
    compression = zipfile.ZIP_DEFLATED

    # create the zip file first parameter path/name, second mode
    zf = zipfile.ZipFile(path + "\\RAWs.zip", mode="w")
    try:
        for file_name in file_names:
            # Add file to the zip file
            # first parameter file to zip, second filename in zip
            file_name1 = file_name.split('\\')[-1]

            zf.write(file_name, file_name1, compress_type=compression)

    except FileNotFoundError:
        print("An error occurred")
    finally:
        # Don't forget to close the file!
        zf.close()
