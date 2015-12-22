class MockResponse(object):
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data
