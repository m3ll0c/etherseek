class FilterInterface:
    def __init__(self, data):
        self.data = data

    def apply(self, criteria):
        return [item for item in self.data if criteria(item)]