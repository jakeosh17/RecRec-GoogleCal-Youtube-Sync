from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from providers.googleAuth import authenticate
from datetime import datetime
from shared.event import event
import logging

class googleCalendarProvider:
  API_SERVICE_NAME = 'calendar'
  API_VERSION = 'v3' 

  def __init__(self, calendar_id):
    self.logger = logging.getLogger('Sync.GoogleCalendar')
    self.api_client = self.authenticate()
    self.calendar_id = calendar_id


  # Authorize the request and store authorization credentials.
  def authenticate(self):
      creds = authenticate()

      try:
          service = build('calendar', 'v3', credentials=creds)
          self.logger.debug('Authenticated successfully using OAuth 2.0.')
          return service
      except Exception as e:
          self.logger.error(f'An error occurred during authentication: {e}')
          return None

  def getEvents(self, startTime, endTime):
    self.logger.debug('Getting events from Google Calendar.')

    startString = startTime.isoformat()
    endString = endTime.isoformat()

    request = self.api_client.events().list(
        calendarId=self.calendar_id,
        maxResults=100,
        singleEvents=True,
        orderBy='startTime',
        timeMax=endString,
        timeMin=startString,
        timeZone='UTC'
    )

    response = request.execute()

    result = []

    for item in response.get('items', []):
      result.append(self.convertGoogleEventToEvent(item))

    self.logger.info('Found %s events.' % len(result))
    return result

  def createEvent(self, event):
    self.logger.debug('Creating Google Calendar event.')

    newEvent = self.convertEventToGoogleEvent(event)

    request = self.api_client.events().insert(
      calendarId = self.calendar_id,
      body = newEvent
    )

    response = request.execute()
    self.logger.debug('Google calendar event created.')

  def updateEvent(self, event):
    self.logger.debug('Updating Google Calendar event.')

    newEvent = self.convertEventToGoogleEvent(event)

    request = self.api_client.events().update(
      calendarId = self.calendar_id,
      eventId = event.id,
      body = newEvent
    )

    response = request.execute()
    self.logger.debug('Event updated.')

  def deleteEvent(self, event):
    self.logger.debug('Removing Google Calendar event.')

    request = self.api_client.events().delete(
      calendarId = self.calendar_id,
      eventId = event.id
    )

    response = request.execute()
    self.logger.debug('Event removed.')

  def convertGoogleEventToEvent(self, item):
    tz = item['start'].get('timeZone', None)
    if tz:
      #tzinfo = gettz(tz)
      startString = item['start'].get('dateTime', None)
      endString = item['end'].get('dateTime', None)

      #start = parse(startString, tzinfos={"BRST": -7200, "CST": tzinfo})
      #end = parse(endString, tzinfos={"BRST": -7200, "CST": tzinfo})
    else:
      startString = item['start'].get('date', None) + 'T00:00:00Z'
      endString = item['end'].get('date', None) + 'T00:00:00Z'
      #start = parse(startString)
      #end = parse(endString)

    start = datetime.fromisoformat(startString)
    end = datetime.fromisoformat(endString)

    return event(item['id'], item['summary'], start, end, item.get('description', ''))

  def convertEventToGoogleEvent(self, item):
    return {
      'description' : item.description,
      'summary' : item.title,
      'start' : {
        'dateTime': item.startTime.isoformat(),
        'timeZone': 'America/New_York'
      },
      'end' : {
        'dateTime': item.endTime.isoformat(),
        'timeZone': 'America/New_York'
      }
    }