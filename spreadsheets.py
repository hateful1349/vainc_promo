import json
import os
from helpers import read_config

from google_auth_httplib2 import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

config = read_config()
bd_id = config["SHEETS"]["target_sheet_link"]
creds_file = "/creds/" + config["SHEETS"]["sacc_creds_file"]

def get_service_sacc():
    creds_json = os.path.dirname(__file__) + creds_file
    scopes = "https://www.googleapis.com/auth/spreadsheets"

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(
        creds_json, scopes
    ).authorize(httplib2.Http())
    return build("sheets", "v4", http=creds_service)


sheets = get_service_sacc().spreadsheets()

ranges = ["Промо", "Карты", "КАО", "ЦАО", "ЛАО", "САО", "ОАО"]
resp = sheets.values().batchGet(spreadsheetId=bd_id, ranges=ranges)
resp = resp.execute()
# with open("regions.json", "w") as f:
#     json.dump(resp, f)
print(resp["valueRanges"][0])
# resp = (
#     get_service_sacc()
#     .spreadsheets()
#     .values()
#     .batchGet(spreadsheetId=bd_copy_sheet_id, ranges=["Промо!A1:J500"])
#     .execute()
# )

# with open("table.json", "w") as f:
#     print(resp, file=f)

# body = {
#     "valueInputOption": "RAW",
#     "data": [
#         {
#             "range": "Промо!L460",
#             "values": [["AAAAA" for k in range(10)] for i in range(10)],
#         }
#     ],
# }

# resp = (
#     get_service_sacc()
#     .spreadsheets()
#     .values()
#     .batchUpdate(spreadsheetId=spreadsheetId, body=body)
#     .execute()
# )

# i = 460
# while True:
#     sheets.values().update(
#         spreadsheetId=bd_copy_sheet_id,
#         range=f"Промо!L{i}",
#         valueInputOption="RAW",
#         body={"values": [[time(), time()]]},
#     ).execute()
#     # sheets.values().batchUpdate(spreadsheetId=bd_copy_sheet_id, body=body)
# .execute()
#     i += 1
#     sleep(1)

# print(resp)
