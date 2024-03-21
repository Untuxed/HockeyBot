from googleStuff import *

client = gspread.authorize(creds)
googleDoc = client.open('VoodooSpring2024Lineup')
sheet = googleDoc.get_worksheet(0)

# Specify Google Sheet ID and range
VOODOO_SHEET_ID = sheet.spreadsheet.id
FORWARDS_LINEUP_RANGE = 'Lineup!A5:C8'
DEFENSE_LINEUP_RANGE = 'Lineup!A11:C13'
GOALIE_LINEUP_RANGE = 'Lineup!A16:C16'
LINEUP_RANGE_NAME = 'Lineup!A5:C16'
ROSTER_DB_RANGE_NAME = 'Roster DB!A2:Z100'
RSVP_SHEET_RANGE = 'RSVP Sheet!A2:H35'


# Connect to Google Sheets API
service = build('sheets', 'v4', credentials=creds)
SHEET = service.spreadsheets()

