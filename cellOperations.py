from sheets import *


async def rangeClear(ranges):
    for r in ranges:
        SHEET.values().clear(spreadsheetId=VOODOO_SHEET_ID, range=r).execute()
    return


async def updateCell(cell, value):
    SHEET.values().update(
        spreadsheetId=VOODOO_SHEET_ID,
        range=cell,
        valueInputOption='RAW',
        body={'values': [[value]]}
    ).execute()
