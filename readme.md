# List of command lines inside terminal to perform various operations:
## Before running the command lines, please make sure: 
## A) virtual environment is activated by running code (in mac):
source venv/bin/activate  
## B) token is valid. If not, please run this command "rm token.pickle" in terminal to delete old one and after deletion rerun python3 upDriveFile.py+any command to obtain valid token and recreate new token.pickle file.

## 1) List folders:
python3 upDriveFile.py list-folders
## 2) Upload a file to the root (main) directory of your google drive:
python3 upDriveFile.py upload --local-path /path/to/local/file
## 3) Upload a file to a specific folder:
python3 upDriveFile.py upload --local-path /path/to/local/file --drive-path folder_id
## 4) Create a new folder in the root directory:
python3 upDriveFile.py create-folder --folder-name NewFolderName
## 5) Create a new folder inside an existing folder:
python3 upDriveFile.py create-folder --folder-name NewFolderName --drive-path parent_folder_id
## 6) Download a file by name:
python3 upDriveFile.py download --file-name file_to_download --local-path /path/to/save/directory



