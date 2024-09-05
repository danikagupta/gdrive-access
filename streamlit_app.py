import os
import streamlit as st
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
import json

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def get_token_state(file='token.json'):
    if os.path.exists(file):
        creds = Credentials.from_authorized_user_file(file, SCOPES)
        if creds and creds.valid:
            return 'Valid',creds
        else:
            return 'Expired',creds
    else:
        return 'Absent',None
    
def get_credentials_info():
    return json.loads(st.secrets['CREDENTIALS_JSON'])


def process_code_state():
    if 'code' in st.query_params:
        flow = Flow.from_client_config(get_credentials_info(), SCOPES, redirect_uri=get_redirect_uri())
        flow.fetch_token(code=st.query_params['code'])
        creds = flow.credentials
        print(f"Creds: {creds}")
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

def get_redirect_uri():
    # Get the base URL of the current page
    base_url = st.get_option("server.baseUrlPath")
    if base_url:
       return f"{st.get_option('server.baseUrlPath')}{st.get_option('server.port')}"
    if 'REDIRECT_URL' in st.secrets:
        return st.secrets['REDIRECT_URL']
    print(f"Base URL: {base_url}, st.secrets: {st.secrets}")
    return "http://localhost:8501"

def process_code_and_token():
    #st.write("Processing code and token")
    process_code_state()   
    #st.write("Processed code state")
    token_state,creds = get_token_state()
    #st.write(f"Token state: {token_state}")
    if token_state == 'Valid':
        #st.write("Token is already valid.")
        st.session_state['creds'] = creds
    elif token_state == 'Expired':
        creds.refresh(Request())
        save_credentials(creds)
        #st.write("Token has been refreshed.")
        st.session_state['creds'] = creds
    else:
        flow = Flow.from_client_config(get_credentials_info(), SCOPES, redirect_uri=get_redirect_uri())
        auth_url, _ = flow.authorization_url(prompt='consent')
        #st.write(f"Please go to this URL to authorize the application: {auth_url}")
        st.markdown(
            f'<a href="{auth_url}" style="display: inline-block; padding: 12px 20px; background-color: #4CAF50; color: white; text-align: center; text-decoration: none; font-size: 16px; border-radius: 4px;"  target="_blank">Authenticate</a>',
            unsafe_allow_html=True
        )

def save_credentials(creds):
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

def list_drive_files(service):
    results = service.files().list(pageSize=50, fields="nextPageToken, files(name, size, modifiedTime, webViewLink, id)").execute()
    items = results.get('files', [])
    return items

def display_files(files):
    if not files:
        st.write('No files found.')
    else:
        st.dataframe(files, column_order=['name', 'size', 'modifiedTime', 'webViewLink', 'id'])
        #st.write('Files:')
        #for item in files:
        #    st.write(f"{item['name']} ({item['id']})")

def main():
    st.title("Google Drive File Lister")
    process_code_and_token()
    if 'creds' in st.session_state:
        #st.write("Got creds")
        service = build('drive', 'v3', credentials=st.session_state['creds'])
        files = list_drive_files(service)
        display_files(files)

if __name__ == '__main__':
    main()