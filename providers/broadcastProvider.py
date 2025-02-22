from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from providers.googleAuth import authenticate
from datetime import datetime
from shared.event import event
import logging

class broadcastProvider:
  # Configuration
  API_SERVICE_NAME = 'calendar'
  API_VERSION = 'v3'

  def __init__(self, streamProvider):
    self.logger = logging.getLogger('Sync.YoutubeBroadcast')
    self.api_client = self.authenticate()
    self.stream_provider = streamProvider

  # Authorize the request and store authorization credentials.
  def authenticate(self):
      creds = authenticate()

      try:
          service = build('youtube', 'v3', credentials=creds)
          self.logger.debug('Authenticated successfully using OAuth 2.0.')
          return service
      except Exception as e:
          self.logger.error(f'An error occurred during authentication: {e}')
          return None

  def bind(self, broadcastId):
    stream = self.stream_provider.getStream()

    if stream:
      self.logger.debug('Binding stream to broadcast.')

      request = self.api_client.liveBroadcasts().bind(
        id=broadcastId,
        streamId=stream.id,
        part='id,status'
      )

      respone = request.execute()

      self.logger.debug('Binding complete.')
    else:
      self.logger.error('Stream not found)')

  def getEvents(self):
    self.logger.debug('Retrieving upcoming broadcasts.')

    request = self.api_client.liveBroadcasts().list(
      part='id, snippet,status,contentDetails',
      broadcastStatus='upcoming',
      maxResults=10
    )
    response = request.execute()
    
    result = []
    for event in response.get('items', []):
        result.append(self.convertYoutubeBroadcastToEvent(event))

    return result

  def createEvent(self, event):
    self.logger.debug('Creating broadcast')

    broadcast = self.convertEventToYoutubeBroadcast(event)
    request = self.api_client.liveBroadcasts().insert(
        part='snippet,contentDetails,status',
        body= broadcast
    )
    response = request.execute()

    self.logger.debug('Broadcast created.')

  def updateEvent(self, event):
    self.logger.debug('Updating broadcast')

    broadcast = self.convertEventToYoutubeBroadcast(event)
    broadcast['id'] = event.id
    request = self.api_client.liveBroadcasts().update(
        part='snippet,contentDetails,status',
        body= broadcast
    )
    response = request.execute()

    self.logger.debug('Broadcast updated.')

  def deleteEvent(self, event):
    self.logger.debug('Removing broadcast')
    request = self.api_client.liveBroadcasts().delete(id=event.id)
    request.execute()
    self.logger.debug('Broadcast removed.')

  def convertYoutubeBroadcastToEvent(self, item):
    startString = item['snippet'].get('scheduledStartTime', None)
    endString = item['snippet'].get('scheduledEndTime', None)

    if startString:
      start = datetime.fromisoformat(item['snippet']['scheduledStartTime'])
    else:
      start = ''
    
    if endString:
      end = datetime.fromisoformat(item['snippet']['scheduledEndTime'])
    else:
      end = ''

    return event(item['id'], item['snippet']['title'], start, end, item['snippet']['description'])
  
  def convertEventToYoutubeBroadcast(self, item):
    return {
          'contentDetails': {
            'enableAutoStart': True,
            'enableAutoStop': True,
            'monitorStream': {
            'broadcastStreamDelayMs' : 0,
            'enableMonitorStream': False
            }
          },
          'snippet': {
            'title': item.title,
            'description': item.description,
            'scheduledStartTime': item.startTime.isoformat(),
            'scheduledEndTime': item.endTime.isoformat(),
          },
          'status': {
            'privacyStatus': 'public'
          }
      }
