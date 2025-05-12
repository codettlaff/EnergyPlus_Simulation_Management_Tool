import os
from os import mkdir
import numpy as np
import pandas as pd
import scipy.io
import opyplus as op
import re
import shutil
import datetime
import pickle

THIS_SCRIPT_DIR = os.path.dirname(__file__)
SPECIAL_IDF_FILEPATH = os.path.join('Special.idf')
TEMPORARY_FOLDERPATH = os.path.join(THIS_SCRIPT_DIR, 'Temporary Folder')

# Test
TEST_IDF_FILEPATH = r"D:\Building_Modeling_Code\Data\Commercial_Prototypes\ASHRAE\90_1_2013\ASHRAE901_OfficeSmall_STD2013_Seattle.idf"
TEST_EPW_FILEPATH = r"D:\Building_Modeling_Code\Data\TMY3_WeatherFiles_Commercial\USA_WA_Seattle-Tacoma.Intl.AP.727930_TMY3.epw"

def generate_variables(idf_filepath, epw_filepath):

    edited_idf_filepath = os.path.join(TEMPORARY_FOLDERPATH, "edited.idf")
    initial_run_folderpath = os.path.join(TEMPORARY_FOLDERPATH, "initial_run")
    rdd_filepath = os.path.join(initial_run_folderpath, "eplusout.rdd")

    if not os.path.exists(TEMPORARY_FOLDERPATH): mkdir(TEMPORARY_FOLDERPATH)
    if not os.path.exists(initial_run_folderpath): mkdir(initial_run_folderpath)

    shutil.copy(idf_filepath, edited_idf_filepath)

    # Appending Output Variable Dictionary - This tells EP to generate rdd file.
    with open(edited_idf_filepath, "a") as idf_to:
        idf_to.write('\nOutput:VariableDictionary,IDF;')

    op.simulate(edited_idf_filepath, epw_filepath, base_dir_path=initial_run_folderpath)

    variable_names = []
    with open(rdd_filepath, "r") as rdd_file:

        lines = rdd_file.readlines()
        for line in lines:
            if not line.startswith('!'):
                variable_name = line.split(',')[2]
                variable_names.append(variable_name)

    shutil.rmtree(TEMPORARY_FOLDERPATH)

    return variable_names

variable_names = generate_variables(TEST_IDF_FILEPATH, TEST_EPW_FILEPATH)
print(variable_names)