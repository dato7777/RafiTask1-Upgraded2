from __future__ import print_function
import os.path
import io
import argparse
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Define the scopes needed for accessing Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

"""Authenticate and return the Google Drive service instance."""
def authenticate():
    creds = None
    # Check if token.pickle file exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no valid credentials, authenticate and get new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_1064085980762-du2qefanrj9u323s3850pc9scsdgdsm3.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

"""Upload a file to Google Drive."""
def upload_file(service, file_path, folder_id=None):
    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('Uploaded File ID: %s' % file.get('id'))
    return file.get('id')

"""Download a file from Google Drive."""
def download_file(service, file_id, file_path):
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print("Download %d%%." % int(status.progress() * 100))
        
        print(f"Downloaded file saved to: {file_path}")
        
    except Exception as e:
        print(f"Error downloading file: {e}")

"""List files in Google Drive."""
def list_files(service, folder_id=None):
    query = f"'{folder_id}' in parents" if folder_id else None
    results = service.files().list(q=query, pageSize=100, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(f"{item['name']} ({item['id']})")

"""List folders in Google Drive."""
def list_folders(service):
    query = "mimeType = 'application/vnd.google-apps.folder'"
    results = service.files().list(q=query, pageSize=100, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No folders found.')
    else:
        print('Folders:')
        for item in items:
            print(f"{item['name']} ({item['id']})")

"""Create a folder in Google Drive."""
def create_folder(service, folder_name, parent_id=None):
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        folder_metadata['parents'] = [parent_id]
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    print(f"Created Folder ID: {folder.get('id')}")
    return folder.get('id')

"""Retrieve a file ID by its name in Google Drive."""
def get_file_id_by_name(service, file_name, parent_id=None):
    query = f"name='{file_name}'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = service.files().list(q=query, pageSize=1, fields="files(id, name)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        print(f"No file found with name: {file_name}")
        return None

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Google Drive file operations.')
    parser.add_argument('operation', choices=['upload', 'download', 'list', 'list-folders', 'create-folder'], help='Operation to perform')
    parser.add_argument('--local-path', required=False, help='Path to the local file or directory')
    parser.add_argument('--drive-path', help='Path to the Google Drive folder for upload or file ID for download')
    parser.add_argument('--folder-name', help='Name of the folder to create in Google Drive')
    parser.add_argument('--file-name', help='Name of the file to download')

    args = parser.parse_args()
    
    # Authenticate and get the service instance
    service = authenticate()
    
    # Perform the requested operation
    if args.operation == 'upload':
        if args.local_path:
            upload_file(service, args.local_path, args.drive_path)
        else:
            print('Error: --local-path is required for upload.')
    elif args.operation == 'download':
        if args.file_name:
            file_id = get_file_id_by_name(service, args.file_name, args.drive_path)
            if file_id:
                if args.local_path and os.path.isdir(args.local_path):
                    file_path = os.path.join(args.local_path, args.file_name)
                    download_file(service, file_id, file_path)
                else:
                    print(f"Error: {args.local_path} is not a directory or is missing.")
            else:
                print(f"Error: No file found with the name {args.file_name}.")
        else:
            print('Error: --file-name is required for download.')
    elif args.operation == 'list':
        list_files(service, args.drive_path)
    elif args.operation == 'list-folders':
        list_folders(service)
    elif args.operation == 'create-folder':
        if args.folder_name:
            create_folder(service, args.folder_name, args.drive_path)
        else:
            print('Error: --folder-name is required for create-folder.')
