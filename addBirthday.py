#!/usr/bin/env python

import argparse 

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


def run(args):
    if args.l:
        logout()
        return

    # Set up Google API
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

    if args.d:
        # If file is given by user, only delete birthdays of people in file 
        if args.file:
            deleteBdaysInFile(creds)
        else:
            deleteAllBdays(creds)
    elif args.file:
        addBdays(creds, args.file, args.r)
    else:
        print(f"No text file provided. Input text file required")


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
        when = datetime.datetime.strptime(date, "%m/%d")
        when = when.replace(year=datetime.datetime.now().year)
        return when
    except ValueError as error:
        pass
    return None


def addBdays(creds, file_name, can_replace):
    try: 
        # Build calendar object
        service = build("calendar", "v3", credentials=creds)

        if os.path.exists(file_name) and file_name.endswith(".txt"):
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

            # Map all names for birthday events to their respective recurring event id
            birthday_events = {}
            for event in events:
                summary = event.get("summary", "")
                if "Birthday" in summary:
                    name = summary[:summary.find("\'")]
                    if name not in birthday_events:
                        birthday_events[name] = (event, event.get("recurringEventId", ""))

            with open(file_name, "r") as f: # open file as read
                # Maps one or more people's name to their birthday
                bday_mapping = [line.split(COLON_SEP) for line in f.readlines()]
                for ind, bday in enumerate(bday_mapping):
                    if not bday:
                        print(f"Line empty. Skipped")
                        continue
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
                        if can_replace and person in birthday_events:
                            # print(f"entered for {person}")
                            success = service.events().update(calendarId='primary', eventId=birthday_events[person][1], body=event).execute()
                            print(f"SUCCESS! Event updated for {person}: {success}\n")
                        elif person not in birthday_events:
                            success = service.events().insert(calendarId='primary', body=event).execute()
                            print(f"SUCCESS! Event created for {person}: {success}\n")
            print("COMPLETE. ALL BIRTHDAYS ADDED")
        else:
            # print correction message
            print(f"file {file_name} does not exist or not a .txt file") 
    except HttpError as error:
        print(f"an error has occurred: {error}")


def deleteAllBdays(creds):
    try:
        # Build calendar object
        service = build("calendar", "v3", credentials=creds)
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
                recurringId = event.get("recurringEventId", "")
                if recurringId:
                    delete_status = service.events().delete(calendarId='primary', eventId=recurringId).execute()
                    print(f"Successfully deleted event: {delete_status}")
                else:
                    one_time_id = event.get("id", "")
                    delete_status = service.events().delete(calendarId='primary', eventId=one_time_id).execute()
                    print(f"Successfully deleted event: {delete_status}")
    except HttpError as error:
        print(f"an error has occurred: {error}")


def deleteBdaysInFile(creds, file_name):
    try:
        # Build calendar object
        service = build("calendar", "v3", credentials=creds)
        # Get all Bday Events in a year
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

        # Parse user input file 
        with open(file_name, "r") as file:
            people = set(person.strip() for person in file.readlines())
            for event in events:
                # Check if the name for event is in set of people we want to delete
                summary = event.get("summary", "")
                # Find the name by getting all characters until the apostrophe 
                if summary[:summary.find("\'")] in people:
                    delete_status = service.events().delete(calendarId='primary', eventId=event.get("recurringEventId", "")).execute()
                    print(f"Successfully deleted event: {delete_status}")
    except HttpError as error:
        print(f"an error has occurred: {error}")


def main():
    parser = argparse.ArgumentParser(description="add birthdays stored locally in text files to a google calendar")
    exclusive_group = parser.add_mutually_exclusive_group()

    # Add logout action
    exclusive_group.add_argument("--l", "--logout", action="store_true", help="logout of currently signed in user")
    exclusive_group.add_argument("-r", "-replace", action="store_true", help="Toggle ability to replace existing calendar birthdays")
    exclusive_group.add_argument("-d", "-delete", action="store_true", help="delete existing birthdays in calendar")

    parser.add_argument("-file", type=str, help="text file containing names and respective birthdays") # TODO: enforce required for everything except -d and --l

    # Set default function as run()
    parser.set_defaults(func=run)

    # Get arguments from user
    args = parser.parse_args()

    # Run default function with args as arguments
    args.func(args)
    # print(args)


def logout():
    if os.path.exists("token.json"):
        os.remove("token.json")
        print(f"Logged out of account")
    else:
        print(f"Not logged in")


if __name__ == "__main__":
    main()