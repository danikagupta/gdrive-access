# 🎈 Streamlit integration with Google Drive


### How to run it on your own machine

Set Up OAuth 2.0 Client ID for Web Application:
Go to the Google Cloud Console.
Navigate to APIs & Services > Credentials.
Click on "Create Credentials" and select "OAuth 2.0 Client ID".
Choose "Web application" as the application type.
Add the redirect URI for your Codespaces environment. This will typically be in the format https://<your-codespace-id>-<port>.app.github.dev/.

Download the credentials.json file and save it in your project directory.

Please remember to configure the REDIRECT_URL in both your Google Cloud API, as well as in secrets.toml

REDIRECT_URL='https://<your-codespace-id>-<port>.app.github.dev/'

