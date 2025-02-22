class stream:
    def __init__(self, id, name, status, stream_key):
        self.status = status
        self.stream_key = stream_key
        self.id = id
        self.name = name

    def __eq__(self, o):
        self.streamKey = o.stream_key