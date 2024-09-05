import os
import streamlit as st
import streamlit.components.v1 as stc


import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

stc.html("""
    <script>
        const domain = window.location.hostname;
        const streamlitReturn = window.parent;
        streamlitReturn.postMessage({ domain: domain }, "*");
    </script>
""")

st.write("Query params")
st.write(st.query_params)
print(f"Query parameters: {st.query_params}")
if 'code' in st.query_params:
    code = st.query_params['code']
    print(f"Code is: {code}")
    flow = Flow.from_client_secrets_file(
        'credentials_web.json', SCOPES,
        redirect_uri='https://improved-system-6pg4wxp44q735rgx-8501.app.github.dev/'
    )

    flow.fetch_token(code=code)
    creds = flow.credentials
    print(f"Creds: {creds}")
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    st.session_state['authenticated'] = True

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

print(f"Authenticated: {st.session_state['authenticated']}")


def authenticate():
    """Authenticate the user and return the credentials."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
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

def list_files(service):
    """List the first 10 files in the user's Google Drive."""
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    return items

def main():
    st.title("Google Drive File Lister 5")
    
    st.write("Authenticate with Google Drive to list files in your Drive.")

    if st.session_state['authenticated']:
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
    else:
        creds=authenticate()
    

if __name__ == '__main__':
    main()