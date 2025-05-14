import os
import pandas as pd
import EP_DataGenerator_Script_v2_20250512 as EP_Gen

THIS_SCRIPT_DIR = os.path.dirname(__file__)

default_data_folderpath = os.path.join(THIS_SCRIPT_DIR, '..', 'Data')

# Test
TEST_IDF_FILEPATH = r"C:\Users\codett\Downloads\ASHRAE901_OfficeLarge_STD2013_Seattle_debugging.idf"
TEST_EPW_FILEPATH = r"D:\Building_Modeling_Code\Data\TMY3_WeatherFiles_Commercial\USA_WA_Seattle-Tacoma.Intl.AP.727930_TMY3.epw"
TEST_DATA_FOLDERPATH = r"D:\Building_Modeling_Code\Data"

def get_location_climate_zone(location=None, climate_zone=None):

    climate_zones = {
        "Miami": "1A",
        "Tampa": "2A",
        "Tucson": "2B",
        "Atlanta": "3A",
        "ElPaso": "3B",
        "SanDiego": "3C",
        "NewYork": "4A",
        "Albuquerque": "4B",
        "Seattle": "4C",
        "Buffalo": "5A",
        "Denver": "5B",
        "PortAngeles": "5C",
        "Rochester": "6A",
        "GreatFalls": "6B",
        "InternationalFalls": "7",
        "Fairbanks": "8"
    }

    if location: return climate_zones.get(location, "Climate Zone not found.")
    if climate_zone:
        reversed_climate_zones = {v: k for k, v in climate_zones.items()}
        return reversed_climate_zones.get(climate_zone, "Location not found.")

def get_idf_weather_filepaths(building_type, idf_filter_list, idf_weather_df=None, data_folderpath=default_data_folderpath):

    # Initialize file lists
    all_idf_filepath_list = []
    all_epw_filepath_list = []

    # If no `idf_weather_df` is provided, collect all .idf and .epw files from the data folder
    if idf_weather_df is None:
        for root, _, files in os.walk(data_folderpath):
            for file in files:
                if file.endswith(".idf") and building_type in root:
                    all_idf_filepath_list.append(os.path.join(root, file))
                elif file.endswith(".epw"):
                    all_epw_filepath_list.append(os.path.join(root, file))
        idf_files = all_idf_filepath_list
        epw_files = all_epw_filepath_list
    else:
        # Get idf and epw file lists from `idf_weather_df`
        idf_files = idf_weather_df['filtered_idf_filepath'].tolist()
        epw_files = idf_weather_df['filtered_epw_filepath'].dropna().tolist()

    # Filter IDF files based on `idf_filter_list` (2D list)
    filtered_idf_files = []
    for filters in idf_filter_list:  # Each inner list represents a set of filters
        for idf in idf_files:
            if all(f in idf for f in filters):  # All filters must match
                filtered_idf_files.append(idf)

    # Create a dataframe to store mapping of filtered IDF and EPW filepaths
    data = []
    for idf in filtered_idf_files:
        idf_filename = os.path.basename(idf)
        if building_type == 'Commercial':
            location = idf_filename.split('_')[3].replace('.idf', '')
        elif building_type == 'Residential':
            climate_zone = idf_filename.split('+')[2]
            location = get_location_climate_zone(climate_zone=climate_zone)
        elif building_type == 'Manufactured':
            location = idf_filename.split('_')[1]
        else:
            location = None

        # Find the corresponding EPW file for the location
        corresponding_epw = None
        for epw in epw_files:
            epw_filename = os.path.basename(epw).replace('.', '')
            if building_type in epw and location in epw_filename:
                corresponding_epw = epw
                break

        data.append({'filtered_idf_filepath': idf, 'filtered_epw_filepath': corresponding_epw})

    # Return as a dataframe
    return pd.DataFrame(data)

idf_filter_list = [['Seattle', 'ASHRAE901', 'STD2013']]
df = get_idf_weather_filepaths('Commercial', idf_filter_list, data_folderpath=TEST_DATA_FOLDERPATH)
idf_filter_list = [['Hospital'], ['ApartmentHighRise'], ['ApartmentMidRise']]
df = get_idf_weather_filepaths('Commercial', idf_filter_list, idf_weather_df=df)
print(df)