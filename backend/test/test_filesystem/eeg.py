"""Test eeg filesystem."""
import unittest
import pandas as pd
import os
import backend.filesystem as fs

class TestEEGFilesystem(unittest.TestCase):

    def test_load(self):
        # Fake data
        channels = ["TP9", "TP10"]

        times, df, channels = fs.EEGFilesystem.load("data", channels)

        self.assertIsInstance(times, pd.Series, "'times' returned is not Series")
        self.assertIsInstance(df, pd.DataFrame, "'df' returned is not DataFrame")
        self.assertIsInstance(channels, list, "'channels' returned is not list")

        self.assertTrue(set(df.columns) <= set(channels), "Columns are not correctly loaded")

    def test_save(self):
        # Fake data
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=["col1", "col2", "col3"])
        name = "testing_save_eeg"

        # Test
        full_filename = fs.EEGFilesystem.save(name, df, ret_fname=True)
        self.assertTrue(os.path.isfile(full_filename), "File was not saved correctly")
        os.remove(full_filename)

if __name__ == '__main__':
    unittest.main()
