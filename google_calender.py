from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
# from oauth2client import file, client, tools
from oauth2client.service_account import ServiceAccountCredentials

import os

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'


def get_schedule(calendar_id="primary"):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # store = file.Storage('google_key.json')
    # creds = store.get()
    # if not creds or creds.invalid:
    #     flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    #     creds = tools.run_flow(flow, store)
    google_keys = {
        "type": "service_account",
        "project_id": os.environ['GOOGLE_SERVICE_PROJECT_ID'],
        "private_key_id": os.environ['GOOGLE_SERVICE_PRIVATE_KEY_ID'],
        "private_key": os.environ['GOOGLE_SERVICE_PRIVATE_KEY'],
        "client_email": os.environ['GOOGLE_SERVICE_CLIENT_EMAIL'],
        "client_id": os.environ['GOOGLE_SERVICE_CLIENT_ID'],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url":  os.environ['GOOGLE_SERVICE_CLIENT_X509_CERT_URL']
     }
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        google_keys,
        scopes=SCOPES
    )
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    # print('Getting the upcoming 10 events')
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    msg = ""
    if not events:
        # print('No upcoming events found.')
        msg += 'No upcoming events found.\n'
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        # print(start, event['summary'])
        if len(start) == 10:
            new_start = start.replace("-", "/")
            new_start += " " * 7
        elif len(start) == 25:
            start_datetime = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S+09:00")
            new_start = start_datetime.strftime("%Y/%m/%d %H:%M ")
        else:
            new_start = "(No dateTime)"
        msg += "{} {}\n".format(new_start, event['summary'])
    return msg


def set_schedule(
        calendar_id="primary",
        body=None
        ):
    if not body:
        print("# set_schedule: no body")
        return False
    if not body.get("start"):
        print("# set_schedule: no 'start' in body")
        return False
    if not body.get("end"):
        print("# set_schedule: no 'end' in body")
        return False
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "google_key.json",
        scopes=SCOPES
    )
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    service.events().insert(
        calendarId=calendar_id,
        body=body
    ).execute()
    return True
