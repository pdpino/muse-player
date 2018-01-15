"""Test marks filesystem."""
import unittest
import pandas as pd
import os
import backend.filesystem as fs

class TestMarksFileHandler(unittest.TestCase):

    def test_load(self):
        timestamps, messages = fs.MarksFileHandler.load("data")

        self.assertIsInstance(timestamps, list, "'timestamps' are not a list")
        self.assertIsInstance(messages, list, "'messages' are not a list")

        self.assertEqual(len(timestamps), len(messages), "'timestamps' and 'messages' does not have the same length")

    def test_save(self):
        # Fake data
        timestamps = [1, 2, 3, 4]
        messages = ["a", "bb", "ccc", "d"]
        name = "testing_save"

        # Test
        full_filename = fs.MarksFileHandler.save(name, timestamps, messages, ret_fname=True)
        self.assertTrue(os.path.isfile(full_filename), "File was not saved correctly")
        os.remove(full_filename)

if __name__ == '__main__':
    unittest.main()
