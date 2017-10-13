### DEPRECATED!!

"""Module that provides classes to handle the connections."""
from time import time
from collections import deque
import threading
import numpy as np
import pandas as pd
import basic
from backend import tf, info
from . import calibrators as crs, yielders

# class WaveBuffer(EEGBuffer):
#     """Buffer to stream waves data (alpha, beta, etc)."""
#
#     def start_calibrating(self):
#         """Set the status to start recording calibrating data."""
#         if not self.is_stream_connected:
#             print("Can't start calibrating if it isn't streaming") # REFACTOR: error msg
#             return False
#         return self.calibrator.start_calibrating()
#
#     def stop_calibrating(self):
#         """Set the status to stop recording calibrating data."""
#         return self.calibrator.stop_calibrating()
#
#     def start_collecting(self):
#         """Start collecting baseline data to detect emotions."""
#         if self.calibrator.is_calibrated():
#             return self.feeler.start_calibrating()
#         else:
#             print("You must calibrate the data before collecting") # REFACTOR: error msg
#             return False
#
#     def stop_collecting(self):
#         """Stop collecting data to detect emotions."""
#         if self.calibrator.is_calibrated():
#             return self.feeler.stop_calibrating()
#         else:
#             print("You must calibrate the data before collecting") # REFACTOR: error msg
#             return False
