import numpy as np
import pandas as pd
from backend import basic, info

class FeelCollector:
    """Collect feelings calculated in time."""

    def __init__(self, feeling_names):
        self.timestamps = []
        self.feelings = []

        self.feeling_names = feeling_names

    def collect(self, timestamp, feeling):
        self.timestamps.append(timestamp)
        self.feelings.append(feeling)

    def export(self):
        """Return a pd.DataFrame with the feelings. Not thread safe"""

        if len(self.timestamps) == 0:
            basic.perror("FeelCollector.export(), No feelings found", force_continue=True)
            return None

        feelings_df = pd.DataFrame(self.feelings, columns=self.feeling_names)
        feelings_df[info.colname_timestamps] = np.array(self.timestamps)

        return feelings_df
