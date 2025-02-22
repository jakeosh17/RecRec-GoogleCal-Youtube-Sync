from providers.googleCalendarProvider import googleCalendarProvider
from providers.recRecProvider import recRecProvider
from shared.event import event
from datetime import datetime, timedelta, timezone
import os
import json
import logging
from utilities.logger import setup_logger

CONFIG='config/scheduler.config.json'
LOG_FILE='logs/sync.log'
LOG_LEVEL=logging.INFO

def executeRecRecSync(recrec, google_cal, startTime, logger):
  season_ids = recrec.getSeasonIds(startTime)

  logger.debug('Found ' + str(len(season_ids)) + ' seasons in RecRec.')

  events = []
  for season in season_ids:
    events = events + recrec.getEvents(season)

  sync(events, google_cal, logger)

def sync(events, destination, logger):
  startTime = min(x.startTime for x in events)
  endTime = max(x.endTime for x in events)

  endTime_utc = endTime.astimezone(timezone.utc)
  startTime_utc = startTime.astimezone(timezone.utc)
  destinationEvents = destination.getEvents(startTime_utc, endTime_utc)

  # verify source events are synced to destination
  for event in events:
    #find events on the same day
    day = event.startTime.astimezone().date()

    filteredEvents = [x for x in destinationEvents if x.startTime.astimezone().date() == day]

    eventFound = False
    for x in filteredEvents:
      if  event == x:
        logger.debug('Source and destination events matching and equal!')
        eventFound = True
      elif x.match(event):
        logger.info('Destination event needs updating from source.')
        eventFound = True
        event.id = x.id
        destination.updateEvent(event)
      else:
        logger.info('Event not matched--needs deletion.')
        destination.deleteEvent(x)
      
    if not(eventFound):
      logger.info('Event needs creating.')
      destination.createEvent(event)

if __name__ == '__main__':
  
  #logging
  logger = setup_logger(name='Sync', level=LOG_LEVEL, log_file=LOG_FILE)
  
  if os.path.exists(CONFIG):
    with open(CONFIG, 'r') as config:
      c = json.load(config)
      recrec_api_key = c['recrec_api_key']
      cal_id = c['cal_id']
      recrec_sync_window = c['recrec_sync_window']
      competitor_id = c['competitor_id']

    # times to sync
    now = datetime.now(timezone.utc)

    recrecStartSync = now - timedelta(seconds=recrec_sync_window)
    recrecEndSync = now + timedelta(seconds=recrec_sync_window)

    logger.debug('Creating providers.')
    recrec = recRecProvider(recrec_api_key, competitor_id=competitor_id)
    google_cal = googleCalendarProvider(cal_id)

    logger.info('Executing RecRec to Google Calendar sync.')
    executeRecRecSync(recrec, google_cal, recrecStartSync, logger)
  else:
    logger.error('CONFIG not found.')