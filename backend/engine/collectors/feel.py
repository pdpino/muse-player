from backend import info

class FeelCollector:
    """Collect feelings calculated in time."""

    def __init__(self):
        self.levels_times = []
        self.levels_relaxation = []
        self.levels_concentration = []

    def collect(self, timestamp, feeling):
        self.levels_times.append(timestamp)
        self.levels_relaxation.append(feeling[0])
        self.levels_concentration.append(feeling[1])

    def export(self):
        """Return a pd.DataFrame with the feelings. Not thread safe"""
        if len(self.levels_times) == 0:
            basic.perror("get_feelings(), No feelings found")

        timestamps = np.array(self.levels_times) - self._full_time[0][0]

        feelings_df = pd.DataFrame()
        feelings_df[info.colname_timestamps] = timestamps
        feelings_df[info.colname_relaxation] = self.levels_relaxation
        feelings_df[info.colname_concentration] = self.levels_concentration

        return feelings_df
