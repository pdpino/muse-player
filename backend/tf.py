"""Module that provide functions to analyze eeg data in Time-Frequency.

All the different methods provided (morlet wavelet convolution, stfft, etc)
should return a dataframe, using the _tf_df() function."""
import numpy as np
import pandas as pd
import math
import basic

def _tf_df(times, freqs, power):
    """Create a Time-Frequency Dataframe."""
    return pd.DataFrame(power, index=times, columns=freqs)

def stfft(times, eeg_data, srate=256, window=256, step=25):
    """Apply the Short Time Fast Fourier Transform to eeg data.

    Parameters:
    times -- array of time
    eeg_data -- array of data
    srate -- sample rate of the measured data
    window -- size of the sliding window
    step -- step to slide the window"""

    def get_n_freqs(n):
        """Return the amount of freqs (resolution), given the number of samples."""
        return n // 2 + 1

    def apply_fft(eeg_data):
        """Apply fft to a window of eeg data

        Parameters:
        eeg_data -- array of dimension [number of samples]."""

        n_samples = len(eeg_data)
        n_freqs = get_n_freqs(n_samples) # resolution

        # Remove offset
        data_centered = eeg_data - np.mean(eeg_data) # no interesa el offset de la onda

        # Apply Hamming window # to taper the data
        w = np.hamming(n_samples)
        data_centered_ham = (data_centered.T*w).T # dot product

        # Apply fft to the window
        Y = np.fft.fft(data_centered_ham)/n_samples # dividir por n para normalizar unidades
        PSD = 2*np.abs(Y[0:n_freqs]) # Obtain amplitude

        return PSD


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

    # Transformar a matriz de numpy # nececsary?
    power = np.matrix(matrix_power)
    power = np.log10(power) # Normalization

    return _tf_df(arr_times, arr_freqs, power)

def convolute(times, eeg_data, srate=256, n_cycles=7):
    """Compute a convolution, of the data, via freq-domain."""
    def create_wavelet(freq, srate, n_cycles):
        """Create a wavelet given certain parameters."""
        bound = 2
        tiempo = np.linspace(-bound, bound, srate)


        # Create sine wave
        sine_wave = np.exp(1j*2*math.pi*freq*tiempo) # use np.exp because is an array


        # Create gaussian
        sigma = n_cycles/(2*math.pi*freq)
        gaus = np.exp(-np.square(tiempo)/(2*sigma**2))

        wavelet = np.multiply(sine_wave, gaus)
        return wavelet

    # Lengths
    n_data = len(eeg_data)
    n_wavelet = srate # REVIEW: is ok???
    n_conv = n_data + n_wavelet - 1
    half_wavelet = n_wavelet // 2


    # Data's fft
    data_fft = np.fft.fft(eeg_data, n_conv)

    # Array of freqs to calculate for
    n_freqs = 100
    arr_freqs = np.linspace(1, srate/2, n_freqs) # srate/2: nyquist frequency; n_freqs: intervalos

    # Empty matrix # will be filled with arrays of len=n_data
    matrix_power = []

    for freq in arr_freqs:
        # wave and its fft
        wave = create_wavelet(freq, srate, n_cycles)
        wave_fft = np.fft.fft(wave, n_conv)
        wave_fft /= max(wave_fft)

        # Calculate convolution
        conv = np.fft.ifft(np.multiply(data_fft, wave_fft)) # element-wise multiplication
        conv = conv[half_wavelet:-half_wavelet+1] # trim edges
        conv = abs(conv) # Get amplitude


        # Add to matrix
        matrix_power.append(conv)

    # Transformar a matriz de numpy # neccesary?
    power = np.matrix(matrix_power)
    power = np.transpose(power)


    power = np.log10(power) # Normalization

    return _tf_df(times, arr_freqs, power)
