import os
import shutil
import requests

THIS_SCRIPT_DIR = os.path.dirname(__file__)

github_url = "https://raw.githubusercontent.com/codettlaff/PNNL_Prototypical_Building_Models/main"
data_folderpath = "Data/Commercial_Prototypes/ASHRAE/90_1_2013"
data_filename = "ASHRAE901_ApartmentHighRise_STD2013_Albuquerque.idf"
data_url = github_url + '/' + data_folderpath + '/' + data_filename
save_to = os.path.join(THIS_SCRIPT_DIR, 'Data_Generation', 'Temporary Folder', data_filename)

AUTH_TOKEN = "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"
HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

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

