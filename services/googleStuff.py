from oauth2client.service_account import ServiceAccountCredentials
from dev.devTokens import google_creds

# replace this .json file with your serviceaccount json key file from google cloud dev portal
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    google_creds, scope
)
