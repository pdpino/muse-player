"""Test tf filesystem."""
import unittest
import pandas as pd
import os
import backend.filesystem as fs

class TestTFFileHandler(unittest.TestCase):

    def test_load(self):
        df = fs.TFFileHandler.load("data", channel="TP9")

        self.assertIsInstance(df, pd.DataFrame, "'df' returned is not DataFrame")

    def test_save(self):
        # Fake data
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=["col1", "col2", "col3"])
        name = "testing_save"

        # Test
        full_filename = fs.TFFileHandler.save(name, df, channel="TP9", ret_fname=True)
        self.assertTrue(os.path.isfile(full_filename), "File was not saved correctly")
        os.remove(full_filename)

if __name__ == '__main__':
    unittest.main()
