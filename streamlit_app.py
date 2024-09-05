#
# This works, though the flow is slightly clunky. There are multiple browser windows that open. We will improve this.
#

import os
import streamlit as st
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build

# Define the scope for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def get_redirect_uri():
    # Get the base URL of the current page
    base_url = st.get_option("server.baseUrlPath")
    if base_url:
       return f"{st.get_option('server.baseUrlPath')}{st.get_option('server.port')}"
    if 'REDIRECT_URL' in st.secrets:
        return st.secrets['REDIRECT_URL']
    print(f"Base URL: {base_url}, st.secrets: {st.secrets}")
    return "http://localhost:8501"

st.write("Query params")
st.write(st.query_params)
st.write(f"Redirect URI: {get_redirect_uri()}")
print(f"Query parameters: {st.query_params} Redirect URI: {get_redirect_uri()}")
if 'code' in st.query_params:
    code = st.query_params['code']
    print(f"Code is: {code}")
    flow = Flow.from_client_secrets_file(
        'credentials_web.json', SCOPES,
        redirect_uri=get_redirect_uri()
    )

    flow.fetch_token(code=code)
    creds = flow.credentials
    print(f"Creds: {creds}")
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    st.session_state['authenticated'] = True

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def load_credentials_from_token():
    """
    Load user credentials from the token.json file if it exists.
    Returns:
        Credentials object or None if no valid credentials are found.
    """
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        print(f"Loaded credentials: {creds}")
        if creds is None:
            return None
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print(f"Refreshed credentials: {creds}")
            return creds
    return None

def save_credentials(creds):
    """
    Save user credentials to the token.json file.
    Args:
        creds: Credentials object to be saved.
    """
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

def authenticate_user():
    """
    Authenticate the user using OAuth 2.0 flow and return the credentials.
    Returns:
        Credentials object after successful authentication.
    """
    creds = load_credentials_from_token()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                'credentials_web.json', SCOPES,
                redirect_uri='https://improved-system-6pg4wxp44q735rgx-8501.app.github.dev/'
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.write(f"Please go to this URL to authorize the application: {auth_url}")
            
            code = st.text_input("Enter the authorization code:")
            if code:
                print(f"Code: {code}")
                flow.fetch_token(code=code)
                creds = flow.credentials
                print(f"Creds: {creds}")
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
        st.session_state['authenticated'] = True
    return creds

def list_drive_files(service):
    """
    List the first 10 files in the user's Google Drive.
    Args:
        service: Google Drive API service instance.
    Returns:
        List of files in the user's Google Drive.
    """
    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    return items

def display_files(files):
    """
    Display the list of files in the Streamlit app.
    Args:
        files: List of files to be displayed.
    """
    if not files:
        st.write('No files found.')
    else:
        st.write('Files:')
        for item in files:
            st.write(f"{item['name']} ({item['id']})")

def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("Google Drive File Lister")
    st.write("Authenticate with Google Drive to list files in your Drive.")
    
    creds = authenticate_user()
    if creds:
        service = build('drive', 'v3', credentials=creds)
        files = list_drive_files(service)
        display_files(files)

if __name__ == '__main__':
    main()