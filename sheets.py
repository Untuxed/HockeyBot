import gspread
from googleStuff import creds

client = gspread.authorize(creds)
googleDoc = client.open('VoodooSpring2024Lineup')
sheet = googleDoc.get_worksheet(0)
botSheet = googleDoc.get_worksheet(1)
