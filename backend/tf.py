"""Module that provide functions to analyze eeg data in Time-Frequency.

All the different methods provided (morlet wavelet convolution, stfft, etc)
should return a dataframe, using the _new_tf_df() function."""
import numpy as np
import pandas as pd
import basic
from backend import info

def normalize_power(power, baseline):
    """Receive a power and a baseline and apply the normalization."""
    return 10*np.log10(power/baseline)

def _normalize_tf_df(times, power, norm=False, baseline=None):
    """Receive a matrix of power (columns are frequencies and row are times) and returns it normalized."""

    if not norm or baseline is None: # Only change scale
        print("not normalizing: {}, {}".format(norm, baseline))
        return np.log10(power)

    # Baseline times # parameters
    bl_init_time = float(baseline[0])
    bl_end_time = float(baseline[1])

    # Indexes:
    find_nearest = lambda val: np.searchsorted(times, val, side="left") #[0]

    bl_init_index = find_nearest(bl_init_time)
    bl_end_index = find_nearest(bl_end_time)
    print("Baseline length: {}".format(bl_end_index - bl_init_index))

    # Real time:
    bl_init_rt = times[bl_init_index]
    bl_end_rt = times[bl_end_index]
    print("Baseline time: ({}, {})".format(bl_init_rt, bl_end_rt))

    # Get size
    n_rows, n_cols = power.shape

    # Recorrer columns (freqs) and divide
    # TASK: do it without the for, using numpy.mean(axis=1)
    # TASK: use normalize_power() function
    for col in range(n_cols):
        # Calculate baseline
        baseline = np.mean(power[bl_init_index:bl_end_index, col])

        # Divide
        power[:, col] /= baseline


    # Log and multiply
    return np.log10(power)
    # NOTE: is not mult by 10 because it goes to numbers to big

def _new_tf_df(times, freqs, power):
    """Create a Time-Frequency Dataframe."""
    return pd.DataFrame(power, index=times, columns=freqs)


### STFFT
def _get_n_freqs(n_samples):
    """Return the amount of freqs (resolution), given the number of samples."""
    return n_samples // 2 + 1

def apply_fft(eeg_data_win):
    """Apply fft to a window of eeg data

    Parameters:
    eeg_data_win -- np.array of dimension [number of samples]."""

    # Choose amount of axis
    axis = eeg_data_win.ndim - 1

    n_samples = eeg_data_win.shape[-1] # Get the last dimension
    n_freqs = _get_n_freqs(n_samples) # resolution

    # Remove offset (isn't relevant)
    if axis == 0: # OPTIMIZE
        # NOTE:
        # This function is called a lot of times repeatedly,
        # this if will always do the same: if analyze.py is called it will use axis == 0 every time; if stream waves is calling it will use axis == 1 every time
        # Same with the if in Y = Y[...]
        # FIX: make stfft() function use multiple channels instead of one (also convolute()?)
        data_centered = eeg_data_win - np.mean(eeg_data_win, axis=0)
    else:
        data_centered = (eeg_data_win.T - np.mean(eeg_data_win, axis=1)).T # Transpose to match axis

    # Apply Hamming window # to taper the data
    w = np.hamming(n_samples)
    # data_centered_ham = (data_centered.T*w).T # each row does dot product with the w vector
    data_centered_ham = data_centered*w

    # Apply fft to the window
    Y = np.fft.fft(data_centered_ham, axis=axis)/n_samples # dividir por n para normalizar unidades
    Y = Y[0:n_freqs] if axis == 0 else Y[:, 0:n_freqs] # Slice according to axis
    PSD = 2*np.abs(Y) # Obtain amplitude
    return PSD**2 # Return power

def get_arr_freqs(window, srate):
    """Return the array of frequencies for stfft."""
    n_freqs = _get_n_freqs(window)
    # NOTE:
    # n_freqs is the resolution of freqs (amount of intervals)
    # srate/2 is the nyquist frequency, the max freq u can get
    return np.linspace(0, srate/2, n_freqs)

def stfft(times, eeg_data, baseline=None, norm=True, window=None, step=None, srate=None):
    """Apply the Short Time Fast Fourier Transform to eeg data.

    Parameters:
    times -- array of time
    eeg_data -- array of data from one channel
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

    n_data = len(eeg_data)
    n_times = len(times)

    if n_times != n_data:
        basic.perror("stfft(): Length of times and data don't match: {} vs {}".format(n_times, n_data))

    # Arrays
    arr_freqs = get_arr_freqs(window, srate)
    arr_times = []

    # Empty matrix # will be filled with arrays of len=n_freqs
    matrix_power = []

    # Iterate
    i = 0 # counter to slice
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
    power = _normalize_tf_df(arr_times, power, norm, baseline=baseline)

    return _new_tf_df(arr_times, arr_freqs, power)


### Convolution
def convolute(times, eeg_data, baseline=None, norm=True, srate=None, n_cycles=None):
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

    # Lengths
    n_data = len(eeg_data)
    n_wavelet = len(wavelet_time)
    n_conv = n_data + n_wavelet - 1 # Len of the convolution, see mikexcohen for details
    half_wavelet = (n_wavelet-1) // 2
    n_freqs = n_data // 2 + 1

    # Data's fft
    data_fft = np.fft.fft(eeg_data, n_conv)

    # Array of freqs to calculate for
    arr_freqs = np.linspace(1, srate/2, n_freqs)
    # arr_freqs = np.linspace(5, 30, 100) # arbitrary interval of frequencies


    # Empty matrix # will be filled with arrays of len=n_data
    matrix_power = []

    for freq in arr_freqs:
        # wave and its fft
        wave = create_wavelet(freq, n_cycles)
        wave_fft = np.fft.fft(wave, n_conv)
        wave_fft /= max(wave_fft) # To normalize units (in the final result), wavelet has a peak of 1

        # Calculate convolution
        conv = np.fft.ifft(np.multiply(data_fft, wave_fft))
        conv = conv[half_wavelet:-half_wavelet-1] # trim edges
        conv = abs(conv)**2 # Get power

        # Add to matrix
        matrix_power.append(conv)

    # Transformar a matriz de numpy # neccesary?
    power = np.matrix(matrix_power)
    power = np.transpose(power)

    # Normalization
    power = _normalize_tf_df(times, power, norm, baseline=baseline)

    return _new_tf_df(times, arr_freqs, power)


### Waves
def get_wave(power, freqs, min_freq, max_freq):
    """Return the wave (avg) of the values in a range of frequencies. Function used in real-time.

    power and freqs must be type np.array"""

    filter_freqs, = np.where((freqs >= min_freq) & (freqs <= max_freq))

    # Return the average all frequencies in that range
    return np.mean(power[:, filter_freqs], axis=1)

def get_waves(power):
    """Receive a power matrix or a list of powers and get the waves. Function used offline"""

    def _do_get_wave(power):
        """Receive a TF dataframe (time, freq, power) and return the alpha, beta, etc waves."""
        # Grab columns names (frequencies)
        freqs = list(power.columns)

        def _get_wave(min_freq, max_freq):
            """Return the wave (avg) of the values in a range of frequencies."""
            # TODO: merge this method with public one get_wave()

            # Filter freqs
            filtered_freqs = info.filter_freqs(freqs, min_freq, max_freq)
            if len(filtered_freqs) == 0:
                basic.perror("get_waves(): no data founded between {} and {} Hz, averaging all frequencies".format(min_freq, max_freq), force_continue=True)
                filtered_freqs = list(freqs)

            # Return the average frequencies in that range
            return np.mean(power[filtered_freqs], axis=1)

        # Dataframe to save all waves
        waves = pd.DataFrame()
        for w, min_freq, max_freq in info.iter_waves():
            waves[w] = _get_wave(min_freq, max_freq)

        return waves

    if type(power) is list:
        all_waves = []
        for p in power:
            all_waves.append(_do_get_wave(p))
        return all_waves

    return _do_get_wave(power)

def get_marks_waves(powers, marks_t, marks_m):
    """Receive a list of power dataframes, return a dataframe with the waves calculated by interval."""

    def _get_wave_interval(pw, min_freq, max_freq, min_time, max_time):
        """Return the wave value in an interval of time."""
        freqs = list(pw.columns)

        # Filter freqs
        filtered_freqs = info.filter_freqs(freqs, min_freq, max_freq)
        if len(filtered_freqs) == 0:
            return 0
        pw = pw[filtered_freqs]

        # Filter time
        times = np.array(pw.index)
        find_time_index = lambda val: np.searchsorted(times, val, side="left")
        t_init = find_time_index(min_time)
        t_end = find_time_index(max_time) if min_time != max_time else len(times)
        pw = pw.iloc[t_init:t_end].as_matrix()

        if pw.size == 0:
            return 0

        # Return mean over both axis
        return np.mean(pw, axis=(0,1))

    all_waves = []

    for p in powers:
        waves_dict = dict()
        for w in info.get_waves_names():
            waves_dict[w] = list() # new list for each wave
        marks_filtered = []

        n = len(marks_t)
        for i in range(n):
            if info.is_stop_mark(marks_m[i]):
                continue

            t_init = marks_t[i]
            j = i+1 if i+1 < n else i
            t_end = marks_t[j]

            for w, min_freq, max_freq in info.iter_waves():
                waves_dict[w].append(_get_wave_interval(p, min_freq, max_freq, t_init, t_end))

            marks_filtered.append(marks_m[i])

        # Dataframe to save all waves
        waves = pd.DataFrame()
        for w in info.get_waves_names():
            waves[w] = waves_dict[w]
        waves[info.messages_column] = marks_filtered

        all_waves.append(waves)

    return all_waves
