#
# This works locally but not in Streamlit Sharing. 
# The reason is that the localost redirect doesnt work
#


import os
import streamlit as st
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def authenticate():
    """Authenticate the user and return the credentials."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def list_files(service):
    """List the first 10 files in the user's Google Drive."""
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    return items

def main():
    st.title("Google Drive File Lister")
    
    st.write("Authenticate with Google Drive to list files in your Drive.")
    
    if st.button("Authenticate"):
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)
        files = list_files(service)
        
        if not files:
            st.write('No files found.')
        else:
            st.write('Files:')
            for item in files:
                st.write(f"{item['name']} ({item['id']})")

if __name__ == '__main__':
    main()