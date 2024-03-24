from oauth2client.service_account import ServiceAccountCredentials

# replace this .json file with your serviceaccount json key file from google cloud dev portal
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    './../resources/', scope
)
