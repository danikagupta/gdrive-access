#
# Failed as OOB has been deprecated due to phishing concerns
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
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.write(f"Please go to this URL to authorize the application: {auth_url}")
            code = st.text_input("Enter the authorization code:")
            if code:
                flow.fetch_token(code=code)
                creds = flow.credentials
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
    st.title("Google Drive Lister Take 4")
    
    st.write("Authenticate with Google Drive to list files in your Drive.")
    
    if st.button("Authenticate"):
        creds = authenticate()
        if creds:
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