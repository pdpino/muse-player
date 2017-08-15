"""Module to preprocess the signal."""
import matplotlib.pyplot as plt
from scipy.signal import iirnotch, lfilter, firls

def filter_notch(eegdata, freq=50, srate=256):
    """Apply a notch filter to eegdata.

    freq -- frequency to filter
    srate -- sampling rate of the signal"""

    # DEBUG: function in debug process
    w0 = freq/(srate/2)
    Q = 25 # Q factor (quality) # QUESTION: que es esto? # in the examples the value is 30 to 35
    b, a = iirnotch(w0, Q)
    filtered = lfilter(b, a, eegdata)

    # plt.plot(range(len(filtered)), filtered, label="filtered")
    # plt.plot(range(len(eegdata)), eegdata, label="eegdata")
    #
    # plt.legend()
    # plt.show()

    return filtered

def filter_highpass(eegdata, srate=256):
    """Apply a highpass filter to eegdata.

    source: https://dsp.stackexchange.com/questions/41184/high-pass-filter-in-python-scipy"""

    filter_stop_freq = 0  # Hz
    filter_pass_freq = 2  # Hz
    filter_order = 1001 # taps in the FIR filter QUESTION: what is this?

    # High-pass filter
    nyquist_rate = srate / 2.
    desired = (0, 0, 1, 1)
    bands = (0, filter_stop_freq, filter_pass_freq, nyquist_rate)
    filter_coefs = firls(filter_order, bands, desired, nyq=nyquist_rate)
    return lfilter(filter_coefs, [1], eegdata)
