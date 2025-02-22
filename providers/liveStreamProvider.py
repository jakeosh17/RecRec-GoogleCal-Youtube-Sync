from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from providers.googleAuth import authenticate
from shared.stream import stream
import logging

class liveStreamProvider:
  # Configuration
  API_SERVICE_NAME = 'calendar'
  API_VERSION = 'v3' 

  def __init__(self, stream):
    self.logger = logging.getLogger('Sync.YoutubeLiveStream')
    self.stream = stream
    self.api_client = self.authenticate()


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

  def getStream(self):
    self.logger.debug('Retrieving live streams.')

    request = self.api_client.liveStreams().list(
      part='id,snippet,cdn,status',
      mine=True,
      maxResults=10
    )
    response = request.execute()
    
    for event in response.get('items', []):
      stream = self.convertYoutubeLiveStreamToEvent(event)

      if stream.stream_key == self.stream.stream_key:
        return stream

    self.logger.info('No stream found matching stream key!')
    create_response = self.createStream(self.stream)

    for event in create_response.get('items', []):
      stream = self.convertYoutubeLiveStreamToEvent(event)

      if stream.stream_key == self.stream.stream_key:
        return stream
    
    self.logger.error('Could not create stream with matching stream key!')

  def createStream(self, stream):
    self.logger.debug('Creating stream.')

    broadcast = self.convertEventToYoutubeLiveStream(stream)
    request = self.api_client.liveStreams().insert(
        part='id,snippet,cdn,status',
        body= broadcast
    )
    response = request.execute()

    self.logger.debug('Stream created.')

    return response

  def deleteStream(self, event):
    self.logger.debug('Removing stream.')
    request = self.api_client.liveStreams().delete(id=event.id)
    request.execute()
    self.logger.debug('Stream removed.')

  def convertYoutubeLiveStreamToEvent(self, item):
    return stream(item['id'], item['snippet']['title'], item['status']['streamStatus'], item['cdn']['ingestionInfo']['streamName'])
  
  def convertEventToYoutubeLiveStream(self, item):
    return {
          'snippet': {
            'title': self.name
          },
          'cdn': {
              'frameRate': '60fps',
              'resolution': '1080p',
              'ingestionType': 'rtmp',
              'ingestionInfo': {
                'streamName': self.stream_key
              }
            }
      }