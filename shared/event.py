from datetime import timezone

class event:
    def __init__(self, id, title, startTime, endTime, description):
        self.id = id
        self.title = title
        self.startTime = startTime
        self.endTime = endTime
        self.description = description

    def __str__(self):
        return '%s - %s' % (self.startTime, self.title)

    def __eq__(self, x):
        return self.startTime.astimezone(timezone.utc) == x.startTime.astimezone(timezone.utc) and self.title == x.title and self.description == x.description

    def match(self, x):
        return self.startTime.astimezone(timezone.utc) == x.startTime.astimezone(timezone.utc)