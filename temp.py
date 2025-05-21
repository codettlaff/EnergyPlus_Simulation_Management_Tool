import os
import shutil
import requests

THIS_SCRIPT_DIR = os.path.dirname(__file__)

def copy_data_folder():
    source_folderpath = r"D:\Building_Modeling_Code\Data"
    destination_folderpath = os.path.join(THIS_SCRIPT_DIR, 'Data')

    if not os.path.exists(destination_folderpath): os.makedirs(destination_folderpath)

    # Loop through every directory and file in the source folder
    for root, dirs, files in os.walk(source_folderpath):
        # Create the corresponding folder in the destination, preserving the structure
        relative_path = os.path.relpath(root, source_folderpath)
        destination_dir = os.path.join(destination_folderpath, relative_path)
        os.makedirs(destination_dir, exist_ok=True)

        # Copy only files that end with .idf or .epw
        for file in files:
            if file.endswith(('.idf', '.epw')):
                src_file = os.path.join(root, file)
                dest_file = os.path.join(destination_dir, file)
                shutil.copy2(src_file, dest_file)

github_url = "https://raw.githubusercontent.com/codettlaff/Building_Code/master"
data_folderpath = "Data/Commercial_Prototypes/ASHRAE/90_1_2013"
data_filename = "ASHRAE901_OfficeLarge_STD2013_Seattle.idf"
data_url = github_url + '/' + data_folderpath + '/' + data_filename
save_to = os.path.join(THIS_SCRIPT_DIR, 'Data_Generation', 'Temporary_Folder', data_filename)

AUTH_TOKEN = "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"
HEADERS = {"Authorization": f"token {AUTH_TOKEN}"}

def download_github_file(file_path, save_to):

    url = data_url
    os.makedirs(os.path.dirname(save_to), exist_ok=True)

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        with open(save_to, 'wb') as f:
            f.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {file_path}: {e}")

download_github_file(data_url, save_to)