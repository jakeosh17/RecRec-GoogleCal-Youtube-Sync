import os
import json
from providers.googleCalendarProvider import googleCalendarProvider
from providers.liveStreamProvider import liveStreamProvider
from providers.broadcastProvider import broadcastProvider
from shared.event import event
from shared.stream import stream
from datetime import datetime, timedelta, timezone
from utilities.logger import setup_logger
import logging

CONFIG='config/scheduler.config.json'
LOG_FILE='logs/sync.log'
LOG_LEVEL=logging.INFO


def executeYTSync(google_cal, youtube, streamTime, logger):
  events = google_cal.getEvents(datetime.now().astimezone(), streamTime)

  if len(events)==0:
    logger.info('No events found')
  else:
    if len(events)>1:
      logger.warn('More than one event found between now and ' + streamTime.astimezone().isoformat())
    event = events[0] 

    broadcasts = youtube.getEvents()
    if len(broadcasts)==0:
      logger.info('Broadcast needs creation.')

      if event.startTime.astimezone() < datetime.now().astimezone() - timedelta(hours=1):
        logger.error('Event start time too early. Ending...')
        return
      
      youtube.createEvent(event)
      broadcasts = youtube.getEvents()

      youtube.bind(broadcasts[0].id)

      logger.info('Broadcast created and bound to stream.')
    else:
      logger.info('Broadcast exists. Exiting...')


if __name__ == '__main__':

  #logging
  logger = setup_logger(name='Sync', level=LOG_LEVEL, log_file=LOG_FILE)
  
  if os.path.exists(CONFIG):
    with open(CONFIG, 'r') as config:
      c = json.load(config)
      cal_id = c['cal_id']
      youtube_sync_window = c['youtube_stream_sync_window']
      default_stream = stream('', c['stream_name'], '', c['stream_key'])


    # times to sync
    now = datetime.now(timezone.utc)

    streamCreationTime = now + timedelta(seconds=youtube_sync_window)

    logger.debug('Creating providers.')
    google_cal = googleCalendarProvider(cal_id)
    livestream = liveStreamProvider(default_stream)
    youtube = broadcastProvider(livestream)

    logger.info('Executing Google Calendar to Youtube Live Sync.')
    executeYTSync(google_cal, youtube, streamCreationTime, logger)
  else:
    logger.error('CONFIG not found.')