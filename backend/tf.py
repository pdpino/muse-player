"""Module that provide functions to analyze eeg data in Time-Frequency.

All the different methods provided (morlet wavelet convolution, stfft, etc)
should return a dataframe, using the _new_tf_df() function."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt # DEBUG
from backend import plots # DEBUG
import basic

def _normalize_tf(times, power):
    """Receive a matrix of power (columns are frequencies and row are times) and returns it normalized."""

    return np.log10(power) # Return a "simple" normalization

    # FIXME: fix this code

    # Baseline times # parameters
    bl_init_time = 0.7
    bl_end_time = 0.9

    # Indexes:
    find_nearest = lambda val: np.searchsorted(times, val, side="left") #[0]

    bl_init_index = find_nearest(bl_init_time)
    bl_end_index = find_nearest(bl_end_time)

    # Real time:
    bl_init_rt = times[bl_init_index]
    bl_end_rt = times[bl_end_index]
    print("Baseline time: ({}, {})".format(bl_init_rt, bl_end_rt))

    # Get size
    n_rows, n_cols = power.shape

    # Recorrer columns (freqs) and divide # HACK: do it without the for, using numpy.mean(axis=1)
    for col in range(n_cols):
        # Calculate baseline
        baseline = np.mean(power[bl_init_index:bl_end_index, col])

        # Divide
        power[:, col] /= baseline

    # Log and multiply
    return 10*np.log10(power) # Decibels

def _new_tf_df(times, freqs, power):
    """Create a Time-Frequency Dataframe."""
    return pd.DataFrame(power, index=times, columns=freqs)

def stfft(times, eeg_data, srate=None, norm=True, window=None, step=None):
    """Apply the Short Time Fast Fourier Transform to eeg data.

    Parameters:
    times -- array of time
    eeg_data -- array of data
    srate -- sample rate of the measured data
    norm -- boolean indicating if normalization should be done
    window -- size of the sliding window
    step -- step to slide the window"""

    # Set DEFAULTs
    if srate is None:
        srate = 256
    if window is None:
        window = 256
    if step is None:
        step = 25


    def get_n_freqs(n):
        """Return the amount of freqs (resolution), given the number of samples."""
        return n // 2 + 1

    def apply_fft(eeg_data_win):
        """Apply fft to a window of eeg data

        Parameters:
        eeg_data_win -- array of dimension [number of samples]."""

        n_samples = len(eeg_data_win)
        n_freqs = get_n_freqs(n_samples) # resolution

        # Remove offset
        data_centered = eeg_data_win - np.mean(eeg_data_win) # no interesa el offset de la onda

        # Apply Hamming window # to taper the data
        w = np.hamming(n_samples)
        data_centered_ham = (data_centered.T*w).T # dot product

        # Apply fft to the window
        Y = np.fft.fft(data_centered_ham)/n_samples # dividir por n para normalizar unidades
        PSD = 2*np.abs(Y[0:n_freqs]) # Obtain amplitude

        return PSD**2 # Return power


    n_data = len(eeg_data)

    if len(times) != n_data:
        basic.perror("Length of times and data don't match")

    # Array of frequencies
    n_freqs = get_n_freqs(window) # resolution of freqs
    arr_freqs = np.linspace(0, srate/2, n_freqs) # srate/2: nyquist frequency; n_freqs: intervalos

    # Array of times
    arr_times = []

    # Empty matrix # will be filled with arrays of len=n_freqs
    matrix_power = []

    # Recorrer
    i = 0 # contador del slice
    while i < n_data:
        data_window = eeg_data[i:i+window]
        if(len(data_window) >= window):
            data_fft = apply_fft(data_window)

            # Add to list and matrix
            matrix_power.append(data_fft)
            arr_times.append(times[i])

        i += step


    # Transformar a matriz de numpy
    power = np.matrix(matrix_power)

    # Normalization
    if norm:
        power = _normalize_tf(arr_times, power)

    return _new_tf_df(arr_times, arr_freqs, power)

def convolute(times, eeg_data, srate=None, norm=True, n_cycles=None):
    """Compute a convolution of the data, via freq-domain.

    Parameters:
    norm -- boolean indicating if normalization should be done"""

    # Set DEFAULTs
    if srate is None:
        srate = 256
    if n_cycles is None:
        n_cycles = 7

    # Wavelet time
    bound = 2
    wavelet_time = np.arange(-bound, bound, 1/srate)

    def create_wavelet(freq, cycles):
        """Create a wavelet given certain parameters."""
        # Create sine wave
        sine_wave = np.exp(1j*2*np.pi*freq*wavelet_time) # use np.exp because is an array

        # Create gaussian
        sigma = cycles/(2*np.pi*freq)
        gaus = np.exp(-np.square(wavelet_time)/(2*sigma**2))

        # multiply
        return np.multiply(sine_wave, gaus)

    # DEBUG: Uncomment to see morlet wavelet, looks fine
    # wave = create_wavelet(6.5, n_cycles)
    # plots.plot_channel(wavelet_time, np.real(wave), "real morlet wavelet")
    # plots.plot_channel(wavelet_time, np.imag(wave), "Imag morlet wavelet")
    # plots.plot_channel(wavelet_time, np.abs(wave), "Abs morlet wavelet")

    # Lengths
    n_data = len(eeg_data)
    n_wavelet = len(wavelet_time)
    n_conv = n_data + n_wavelet - 1
    half_wavelet = (n_wavelet-1) // 2
    n_freqs = n_data // 2 + 1


    # Data's fft
    data_fft = np.fft.fft(eeg_data, n_conv) # / n_data
    # QUESTION: slice, absolute and multiply by 2 !!! But match the size of the wave_fft

    # DEBUG: testing fft data
    # plots.plot_channel(range(n_conv), data_fft, "fft data", xlab="freq")

    # Array of freqs to calculate for
    arr_freqs = np.linspace(1, srate/2, n_freqs) # srate/2: nyquist frequency; n_freqs: intervalos
    # arr_freqs = np.linspace(5, 30, 100) # arbitrary interval of frequencies


    # Empty matrix # will be filled with arrays of len=n_data
    matrix_power = []

    for freq in arr_freqs:
        # wave and its fft
        wave = create_wavelet(freq, n_cycles)
        wave_fft = np.fft.fft(wave, n_conv)

        # DEBUG: plot the wave and its fft
        if False: #freq > 25:
            plt.subplot(121)
            plt.plot(range(len(wave)), wave)
            plt.xlabel("time (index)")
            plt.ylabel("Amplitude")
            plt.title("Wave")

            plt.subplot(122)
            plt.plot(range(len(wave_fft)), abs(wave_fft))
            plt.xlabel("Freq (index)")
            plt.ylabel("Amplitude")
            plt.title("Wave fft")

            plt.suptitle("{}Hz".format(freq))
            plt.show()

        wave_fft /= max(wave_fft)

        # DEBUG: plot ffts obtained
        # plots.plot_multiple(range(len(data_fft)), [data_fft, wave_fft], "FFTs at {}Hz".format(freq), ["data", "wave"], xlab="freq (index)")

        # Calculate convolution
        conv = np.multiply(data_fft, wave_fft)

        # DEBUG: plot data_fft, wave_fft and conv fft
        if False: #freq > 25:
            plt.subplot(311)
            x = 2*abs(data_fft[:n_freqs])
            plt.plot(arr_freqs, x)
            plt.xlabel("Freq (index)")
            plt.ylabel("Amplitude")
            plt.title("Data fft")

            plt.subplot(312)
            x = abs(wave_fft[:n_freqs])
            plt.plot(arr_freqs, x)
            plt.xlabel("Freq (index)")
            plt.ylabel("Amplitude")
            plt.title("Wave fft")

            plt.subplot(313)
            x = 2*abs(conv[:n_freqs])
            plt.plot(arr_freqs, x)
            plt.xlabel("Freq (index)")
            plt.ylabel("Amplitude")
            plt.title("Multiplication")

            plt.suptitle("{}Hz".format(freq))
            plt.show()



        conv = np.fft.ifft(conv)
        conv = conv[half_wavelet:-half_wavelet-1] # trim edges
        conv = abs(conv)**2 # Get power


        # DEBUG: plot convolution at each freq
        if False and freq > 9:
            plots.plot_channel(range(len(conv)), conv, "Convolution in {} Hz".format(freq))

        # Add to matrix
        matrix_power.append(conv)

    # Transformar a matriz de numpy # neccesary?
    power = np.matrix(matrix_power)
    power = np.transpose(power)

    # Normalization
    if norm:
        power = _normalize_tf(times, power)

    return _new_tf_df(times, arr_freqs, power)

def get_waves(power):
    """Receive a TF dataframe (time, freq, power) and return the alpha, beta, etc waves."""

    # Grab columns names (frequencies)
    cols = list(power.columns)


    # Function to get wave
    def get_wave(min_freq, max_freq):
        """ """
        # Filter freqs
        filter_freqs = [freq for freq in cols if freq >= min_freq and freq <= max_freq]
        if len(filter_freqs) == 0:
            basic.perror("get_waves() No freqs founded between {} and {}".format(min_freq, max_freq)) # REVIEW

        # Filter power df
        array = power[filter_freqs]

        # Return average all frequencies in that range
        return array.mean(1)

    waves = pd.DataFrame()

    waves["delta"] = get_wave(1, 4)
    waves["theta"] = get_wave(4, 8)
    waves["alpha"] = get_wave(8, 13)
    waves["beta"] = get_wave(13, 30)
    waves["gamma"] = get_wave(30, 44)

    return waves
