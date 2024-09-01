import streamlit as st

from langchain_google_community import GoogleDriveLoader


from langchain.document_loaders import GoogleDriveLoader
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import os
import io

# Set up the OAuth 2.0 flow
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
REDIRECT_URI='https://opulent-tribble-qxqp65xp769f9gqw-8501.app.github.dev'

FOLDER_ID="0BwSLFlZkV9ORWFM0OW5TU0N3OGs"

def authenticate_gdrive():
    creds = None
    flow = Flow.from_client_secrets_file(
        '.credentials/credentials.json', 
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
        )
    creds = flow.run_local_server(port=0)
    return creds

def main():
    #creds = authenticate_gdrive()

    # Initialize GoogleDriveLoader
    #loader = GoogleDriveLoader(
    #    credentials=creds,
    #    folder_id=FOLDER_ID,
    #            )
    
    loader = GoogleDriveLoader(
        folder_id="1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5",
        credentials_path=".credentials/credentials.json",
        token_path=".credentials/google_token.json",
        redirect_uri=REDIRECT_URI,
        # Optional: configure whether to recursively fetch files from subfolders. Defaults to False.
        recursive=False,
        )

    # Load documents from Google Drive
    documents = loader.load()

    for doc in documents:
        print(doc)

main()

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
