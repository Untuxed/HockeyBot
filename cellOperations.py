from sheets import *


async def Range_Clear(ranges):
    for r in ranges:
        SHEET.values().clear(spreadsheetId=VOODOO_SHEET_ID, range=r).execute()
    return


async def Update_Cell(cell, value):
    SHEET.values().update(
        spreadsheetId=VOODOO_SHEET_ID,
        range=cell,
        valueInputOption='RAW',
        body={'values': [[value]]}
    ).execute()


async def Update_Cell_Range(range, values):
    SHEET.values().update(
        spreadsheetId=VOODOO_SHEET_ID,
        range=range,
        valueInputOption='RAW',
        body={"values": values}
    ).execute()


def get_RSVP_Table():
    return SHEET.values().get(
                spreadsheetId=VOODOO_SHEET_ID,
                range=RSVP_SHEET_RANGE,
                valueRenderOption='FORMATTED_VALUE'
            ).execute().get('values', [])


def get_players():
    # Fetch all players from the Google Sheet
    return SHEET.values().get(
        spreadsheetId=VOODOO_SHEET_ID,
        range=ROSTER_DB_RANGE_NAME
    ).execute().get('values', [])


def get_player(memberID):
    # Fetch all players from the Google Sheet
    players = get_players()

    # Find the player with the matching ID
    player = next((player for player in players if player[4] == memberID), None)

    if player is None:
        # If the player wasn't found, raise an exception
        raise ValueError('Player does not exist.')

    return player


def generate_stats_message(player):
    number, firstName, lastName, position, memberID, status, isCaptain, handedness, gp, goals, assists, total, avg, pims = player
    stats_dict = {'GP': gp, 'GOALS': goals, 'ASSISTS': assists, 'TOTAL': total, 'PIMS': pims}
    stats_lines = [f'{key}: {value}' for key, value in stats_dict.items()]
    stats_message = f'**Stats for {firstName} {lastName}:**\n' + '\n'.join(stats_lines)
    return stats_message
