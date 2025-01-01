#!/usr/bin/env python

import datetime
import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

COLON_SEP = ": "
COMMA_SEP = ","
# OPS = 2

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "logout":
        if os.path.exists("token.json"):
            os.remove("token.json")
            print(f"Logged out of account")
        else:
            print(f"Not logged in")
    
    elif len(sys.argv) == 3 and sys.argv[1] == "a":
        creds = None
        # Check if creds already exists 
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        # If it doesnt exist or is not valid create a new one
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save credential for next run
            with open("token.json", "w") as token: 
                token.write(creds.to_json())

        try: 
            # Build calendar object
            service = build("calendar", "v3", credentials=creds)
            # Delete all bday's before adding 
            deleteAllBdays(service)

            file_name = sys.argv[2] # os.getcwd() + 
            if os.path.exists(file_name) and file_name.endswith(".txt"):
                with open(file_name, "r") as f: # open file as read
                    # Maps one or more people's name to their birthday
                    bday_mapping = [line.split(COLON_SEP) for line in f.readlines()]
                    for ind, bday in enumerate(bday_mapping):
                        people, day = bday
                        date = get_date(day.strip())
                        if not date:
                            print(f"Invalid birthdate in line {ind}. Skipped.") # TODO: add guidelines for format 
                            continue
                        end_date = date + datetime.timedelta(days=1) 
                        
                        event = {
                            "visibility" : "private",
                            "transparency" : "transparent",
                            "recurrence" : ["RRULE:FREQ=YEARLY"]
                        }
                        event["start"] = {
                            "date" : date.strftime("%Y-%m-%d") 
                        }
                        event["end"] = {
                            "date" : end_date.strftime("%Y-%m-%d")
                        }
                        # event["eventType"] = "birthday"
                        persons = people.split(COMMA_SEP)
                        
                        for person in persons:
                            event["summary"] = f"{person}'s Birthday"
                            success = service.events().insert(calendarId='primary', body=event).execute()
                            # print(f"SUCCESS! Event created for {person}: {success}\n")
                print("COMPLETE. ALL BIRTHDAYS ADDED")
            else:
                # print correction message
                print(f"file {file_name} does not exist or not a .txt file") 
        except HttpError as error:
            print(f"an error has occurred: {error}")
    else:
        print(f"Invalid command")


def get_date(date):
    # Try %b %d format
    try: 
        when = datetime.datetime.strptime(date, "%b %d")
        when = when.replace(year=datetime.datetime.now().year)
        return when
    except ValueError as error:
        pass

    # Try %B %d format
    try: 
        when = datetime.datetime.strptime(date, "%B %d")
        when = when.replace(year=datetime.datetime.now().year)
        return when
    except ValueError as error:
        pass

    # Try %Y/%m/$d format
    try: 
        when = datetime.datetime.strptime(date, "%Y/$m/%d")
        when = when.replace(year=datetime.datetime.now().year)
        return when
    except ValueError as error:
        pass
    return None

def deleteAllBdays(service):
    # Get Events in a year
    event_results= (
        service.events()
        .list(
            calendarId="primary",
            timeMin=datetime.datetime(datetime.datetime.now().year, 1, 1).isoformat() + "Z",
            timeMax=datetime.datetime(datetime.datetime.now().year + 1, 1, 1).isoformat() + "Z",
            singleEvents=True,
        )
        .execute()
    )
    events = event_results.get("items", [])
    for event in events:
        # Check if event is a birthday. If event is a birthday, delete it
        if "Birthday" in event.get("summary", ""):
            delete_status = service.events().delete(calendarId='primary', eventId=event.get("recurringEventId", "")).execute()
            print(f"Successfully deleted event: {delete_status}")
    return 
    
if __name__ == "__main__":
    main()