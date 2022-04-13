import os
from time import sleep, time

from google_auth_httplib2 import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

spreadsheetId = "1JVYiqcp2DSfrWtJ0k6958Hbnh72JrNp9ZBa44xe4pUk"
creds_file = "/creds/python-sheets-347105-e7ea64b86398.json"


def get_service_sacc():
    creds_json = os.path.dirname(__file__) + creds_file
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(
        creds_json, scopes
    ).authorize(httplib2.Http())
    return build("sheets", "v4", http=creds_service)


sheet = get_service_sacc().spreadsheets()

# resp = (
#     get_service_sacc()
#     .spreadsheets()
#     .values()
#     .batchGet(spreadsheetId=spreadsheetId, ranges=["Лист1!A1:D5"])
#     .execute()
# )

body = {
    "valueInputOption": "RAW",
    "data": [
        {
            "range": "Лист2!A1:E1",
            "values": [["AAAAA" for k in range(10)] for i in range(10)],
        }
    ],
}

# resp = (
#     get_service_sacc()
#     .spreadsheets()
#     .values()
#     .batchUpdate(spreadsheetId=spreadsheetId, body=body)
#     .execute()
# )

i = 1
while True:
    sheet.values().update(
        spreadsheetId=spreadsheetId,
        range=f"Лист1!A{i}",
        valueInputOption="RAW",
        body={"values": [[time()]]},
    ).execute()
    i += 1
    sleep(1)

print(resp)
