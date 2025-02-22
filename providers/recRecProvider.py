import requests
from shared.event import event
from datetime import datetime, timedelta

class recRecProvider:
    def __init__(self, api_key, competitor_id):
        self.api_key = api_key
        self.competitor_id = competitor_id

    def getEvents(self, season_id):
        matches = self.getMatchesForSeason(season_id)
        events = []

        startDate = min(x.startTime for x in matches)
        endDate = max(x.endTime for x in matches)
        delta = endDate - startDate   # returns timedelta

        for i in range(delta.days + 1):
            day = startDate.date() + timedelta(days=i)
            nextDay = day + timedelta(days=1)

            filteredMatches = [x for x in matches if x.startTime.astimezone().date() == day]

            if len(filteredMatches)>0:
                newEvent = filteredMatches[0]
                eventTitle = newEvent.title + ' CBC - ' + str(newEvent.startTime.date())

                filteredMatches.sort(key=lambda x: (x.location, x.startTime))

                description = ''
                previousLocation = None
                for match in filteredMatches:
                    if match.location != previousLocation:
                        description = description + match.location + '\n'
                        previousLocation = match.location
                    
                    description = description + str(match)  + '\n'

                events.append(event(
                    '',
                    eventTitle,
                    min(x.startTime for x in filteredMatches),
                    max(x.endTime for x in filteredMatches),
                    description
                ))


        return events

    def getSeasonIds(self, startDate):
        matches = self.getMatchesForCompetitor(self.competitor_id)

        season_ids = [x.season_id for x in matches if x.startTime>=startDate]
        return set(season_ids)


        
    def getMatches(self, payload):
        endpoint='matches'

        matches = []
        response = self.makeRequest(endpoint, payload)

        for item in response.json():
            matchStartTime = datetime.fromisoformat(item['time']).astimezone()
            eventStartTimeStamp = datetime.strptime(item['division']['start_time'], '%H:%M:%S')
            eventEndTimeStamp = datetime.strptime(item['division']['end_time'], '%H:%M:%S')
            eventStart = datetime(matchStartTime.year, matchStartTime.month, matchStartTime.day, eventStartTimeStamp.hour, eventStartTimeStamp.minute, eventStartTimeStamp.second).astimezone()
            eventEnd = datetime(matchStartTime.year, matchStartTime.month, matchStartTime.day, eventEndTimeStamp.hour, eventEndTimeStamp.minute, eventEndTimeStamp.second).astimezone()

            matches.append(
                match(
                    event(
                        item['id'],
                        item['division']['name'],
                        matchStartTime,
                        eventEnd,
                        ''
                    ),
                    item['home_competitor']['name'],
                    item['away_competitor']['name'],
                    item['home_score'],
                    item['away_score'],
                    item['location']['name'],
                    item['division']['season_id']
                )
            )
        
        return matches

    def makeRequest(self, endpoint, payload):
        url = 'https://app.recrec.io/api/'
        headers = {'X-Api-Key': self.api_key}
        return requests.get(url + endpoint, params=payload, headers=headers)

    def getMatchesForCompetitor(self, competitor_id):
        payload = {'competitor_id': competitor_id}
        return self.getMatches(payload)

    def getMatchesForDivision(self, division_id):
        payload = {'division_id': division_id}
        return self.getMatches(payload)

    def getMatchesForSeason(self, season_id):
        payload = {'season_id': season_id}
        return self.getMatches(payload)


class match(event):
    def __init__(self, newEvent, home_name, away_name, home_score, away_score, location, season_id):
        super().__init__(newEvent.id, newEvent.title, newEvent.startTime, newEvent.endTime, newEvent.description)
        self.home_name = home_name
        self.away_name = away_name
        if home_score:
            self.home_score = ' [' + str(home_score) + '] '
        else:
            self.home_score = ''
        if home_score:
            self.away_score = ' [' + str(away_score) + '] '
        else:
            self.away_score = ''
        self.location = location
        self.season_id = season_id

    def __str__(self):
        return self.startTime.strftime("%I:%M %p") + ': ' + self.home_name + str(self.home_score) + ' vs ' + self.away_name + str(self.away_score)

    def __eq__(self, item):
        return self.id == item.id

# start from competitor_id

