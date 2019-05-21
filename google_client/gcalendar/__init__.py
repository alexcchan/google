#!/usr/bin/env python

import httplib2

from apiclient.discovery import build
from datetime import datetime,timedelta
from oauth_util import Credentials
from timezones import PACIFIC


OAUTH_SCOPE = 'https://www.googleapis.com/auth/calendar'
PACIFIC_TIME_ZONE = 'America/Los_Angeles'


class CalendarClient(object):

    def __init__(self,argparser=None,client_args={}):
        """Initialize API client."""
        credentials = Credentials(name='calendar',scope=OAUTH_SCOPE,argparser=argparser).get()
        self.service = build(serviceName='calendar', version='v3', http=credentials.authorize(httplib2.Http(**client_args)))

    def get_calendars(self,summary=None):
        """Get calendars (generator)."""
        page_token = None
        while True:
            calendars = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar in calendars['items']:
                if summary is None or calendar['summary'] == summary:
                    yield calendar
            page_token = calendars.get('nextPageToken')
            if not page_token:
                break

    def get_calendar(self,summary):
        """Get first calendar with the summary."""
        for calendar in self.get_calendars(summary=summary):
            return calendar
        return None

    def get_events(self,calendar_id,time_min=None,time_max=None,event_filter=None):
        """Get calendar events (generator)."""
        def parse_date(s):
            return datetime.strptime(s,'%Y-%m-%d')
        def parse_datetime(s):
            ts = datetime.strptime(s[:-6],'%Y-%m-%dT%H:%M:%S')
            pacific_ts = datetime(*(ts.timetuple()[:6] + (0,PACIFIC)))
            return pacific_ts
        page_token = None
        while True:
            if time_min or time_max:
                if isinstance(time_min,datetime):
                    time_min = time_min.isoformat()
                if isinstance(time_max,datetime):
                    time_max = time_max.isoformat()
                events = self.service.events().list(calendarId=calendar_id,orderBy='startTime',singleEvents=True,timeMin=time_min,timeMax=time_max,timeZone=PACIFIC_TIME_ZONE,pageToken=page_token).execute()
            else:
                events = self.service.events().list(calendarId=calendar_id,timeZone=PACIFIC_TIME_ZONE,pageToken=page_token).execute()
            for event in events['items']:
                if event_filter is not None and not event_filter(event):
                    continue
                event_start_time = None
                event_end_time = None
                event_start_date = None
                event_end_date = None
                if event.has_key('start'):
                    if event['start'].has_key('dateTime'):
                        event_start_time = parse_datetime(event['start']['dateTime'])
                        event['start']['dateTimeObj'] = event_start_time
                    if event['start'].has_key('date'):
                        event_start_date = parse_date(event['start']['date'])
                        event['start']['dateObj'] = event_start_date
                if event.has_key('end'):
                    if event['end'].has_key('dateTime'):
                        event_end_time = parse_datetime(event['end']['dateTime'])
                        event['end']['dateTimeObj'] = event_end_time
                    if event['end'].has_key('date'):
                        event_end_date = parse_date(event['end']['date'])
                        event['end']['dateObj'] = event_end_date
                event_duration = None
                if event_start_time is not None and event_end_time is not None:
                    event_duration = event_end_time - event_start_time
                elif event_start_date is not None and event_end_date is not None:
                    event_duration = event_end_date - event_start_date
                event['duration'] = event_duration
                yield event
            page_token = events.get('nextPageToken')
            if not page_token:
                break

    def get_all_day_events(self,calendar_id,time_min=None,time_max=None):
        """Get calendar all-day events (generator)."""
        def event_filter(event):
            return event.has_key('start') and event['start'].has_key('date')
        return self.get_events(calendar_id,time_min,time_max,event_filter)

    def get_week_events(self,calendar_id,weeks=1):
        """Get calendar events for this week (generator)."""
        def midnight(d):
            return datetime(d.year,d.month,d.day,0,0,0,0,d.tzinfo)
        now = PACIFIC.now()
        prev_sunday = now if now.isoweekday() == 7 else now + timedelta(days=-now.isoweekday())
        next_sunday = prev_sunday + timedelta(days=7*weeks)
        return self.get_events(calendar_id=calendar_id,time_min=midnight(prev_sunday),time_max=midnight(next_sunday))

    def create_event(self,calendar_id,summary,start_time,end_time,attendees=None):
        """Create a simple calendar event."""
        body={
            'summary': summary,
            'start': {'dateTime': start_time.isoformat()},
            'end': {'dateTime': end_time.isoformat()}
        }
        if attendees is not None:
            body['attendees'] = [{'email':attendee} for attendee in attendees]
        self.service.events().insert(calendarId=calendar_id,body=body).execute()

    def delete_event(self,calendar_id,event_id):
        """Delete a calendar event."""
        self.service.events().delete(calendarId=calendar_id,eventId=event_id).execute()

    def print_calendars(self,calendar_name,weeks=1):
        """Print this week's events for the calendar."""
        for calendar in self.get_calendars(summary=calendar_name):
            print
            print calendar_name
            self.print_week_events(calendar_id=calendar['id'],weeks=weeks)

    def print_week_events(self,calendar_id,weeks=1):
        """Print events."""
        last_start_time = None
        for event in self.get_week_events(calendar_id=calendar_id,weeks=weeks):
            start_time = event['start'].get('dateTimeObj',event['start'].get('dateObj'))
            end_time = event['end'].get('dateTimeObj',event['end'].get('dateObj'))
            if last_start_time is None or last_start_time.strftime('%Y-%m-%d') != start_time.strftime('%Y-%m-%d'):
                print
                print start_time.strftime('%Y-%m-%d %a')
            last_start_time = start_time
            if event['start'].has_key('dateTime'):
                print start_time.strftime('%H:%M'),end_time.strftime('%H:%M'),event['summary']
            else:
                print start_time.strftime('%Y-%m-%d %H:%M'),end_time.strftime('%Y-%m-%d %H:%M'),event['summary']
