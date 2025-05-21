import os
import shutil

THIS_SCRIPT_DIR = os.path.dirname(__file__)

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
