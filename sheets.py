import gspread
from googleStuff import *

client = gspread.authorize(creds)
googleDoc = client.open('VoodooSpring2024Lineup')
sheet = googleDoc.get_worksheet(0)
botSheet = googleDoc.get_worksheet(1)
rosterSheet = googleDoc.get_worksheet(2)
# Assuming SHEET_ID is a worksheet object
rosterSheet_id = rosterSheet.spreadsheet.id  # Extract the spreadsheet ID

# Specify Google Sheet ID and range
ROSTER_SHEET_ID = rosterSheet_id
ROSTER_DB_RANGE_NAME = 'Roster DB!A2:Z100'


# Connect to Google Sheets API
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()