import json
import pandas as pd

class Converter:
    def __init__(self, data):
        self.data = data

    def to_json(self):
        return json.dumps(self.data, indent=2)

    def to_df(self):
        return pd.DataFrame(self.data)