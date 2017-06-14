#/usr/bin/env python
"""Script that analyses data with a fourier transform"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from basic.data_manager import read_data
from basic import perror


def compute_feature_vector(eegdata, Fs):
    """Extract the features from the EEG
    Inputs:
    eegdata: array of dimension [number of samples, number of channels]
    Fs: sampling frequency of eegdata

    Outputs:
    feature_vector: [number of features points; number of different features]

    source: https://github.com/NeuroTechX/bci-workshop
    """

    n_samples, n_channels = eegdata.shape

    ### 1. Compute the PSD # Power Spectral Density

    # Apply Hamming window
    w = np.hamming(n_samples)
    dataWinCentered = eegdata - np.mean(eegdata, axis=0) # Remove offset
    dataWinCenteredHam = (dataWinCentered.T*w).T

    NFFT = nextpow2(n_samples)
    Y = np.fft.fft(dataWinCenteredHam, n=NFFT, axis=0)/n_samples
    a = int(NFFT/2)
    PSD = 2*np.abs(Y[0:a,:])
    f = Fs/2*np.linspace(0,1,a)


    # SPECTRAL FEATURES
    # Average of band powers
    # Delta <4
    ind_delta, = np.where(f<4)
    meanDelta = np.mean(PSD[ind_delta,:],axis=0)
    # Theta 4-8
    ind_theta, = np.where((f>=4) & (f<=8))
    meanTheta = np.mean(PSD[ind_theta,:],axis=0)
    # Alpha 8 - 12
    ind_alpha, = np.where((f>=8) & (f<=12))
    meanAlpha = np.mean(PSD[ind_alpha,:],axis=0)
    # Beta 12-30
    ind_beta, = np.where((f>=12) & (f<=30))
    meanBeta = np.mean(PSD[ind_beta,:],axis=0)
    # Gamma 30>
    ind_gamma, = np.where(f>=30)
    meanGamma = np.mean(PSD[ind_gamma,:],axis=0)


    feature_vector = np.concatenate((meanDelta, meanTheta, meanAlpha, meanBeta, meanGamma),axis=0)

    feature_vector = np.log10(feature_vector)

    return feature_vector

def compute_feature_vector_one(eegdata, Fs, plot_window=False):
    """Extract the features from the EEG, only with one axis

    Parameters:
    eegdata -- array of dimension [number of samples]
    Fs -- sampling frequency of eegdata
    plot_window -- bool, plot: data, centered_data, freq-domain with data, freq-domain with centered_data

    Return:
    feature_vector -- array: [delta, theta, alpha, beta, gamma]
    """

    n_samples = len(eegdata)
    n_freqs = int(n_samples/2) + 1 # Cantidad de frecuencias (resolucion)

    # Tomar rango de frecuencias
    f = np.linspace(0,Fs/2,n_freqs) # Fs/2: nyquist frequency; n_freqs intervalos

    # Remove offset
    data_centered = eegdata - np.mean(eegdata) # no interesa el offset de la onda

    # Apply Hamming window
    w = np.hamming(n_samples)
    data_centered_ham = (data_centered.T*w).T # QUESTION: pq una hamming window? que es lo que hace?

    def get_fft(data, n, nfreqs):
        Y = np.fft.fft(data)/n # dividir por n para normalizar unidades
        return 2*np.abs(Y[0:n_freqs])

    PSD_raw = get_fft(data_centered, n_samples, n_freqs)
    PSD_window = get_fft(data_centered_ham, n_samples, n_freqs)



    ## Filtrar por frecuencias
    def filter_wrapper(PSD, condition):
        """Filter by the wanted frequencies"""
        index, = np.where(condition)
        return np.mean(PSD[index]) # QUESTION: usar mean, sum, ifft?

    def obtain_feat_vector(PSD):
        """Receive a power spectral density and return the (d, t, a, b, g) vector of features."""
        delta = filter_wrapper(PSD, (f<4)) # Delta < 4
        theta = filter_wrapper(PSD, (f>=4) & (f<=8)) # Theta 4-8
        alpha = filter_wrapper(PSD, (f>=8) & (f<=12)) # Alpha 8 - 12
        beta = filter_wrapper(PSD, (f>=12) & (f<=30)) # Beta 12-30
        gamma = filter_wrapper(PSD, (f>=30) & (f<=44)) # Gamma 30-44

        if beta == 0 or delta == 0 or theta == 0 or alpha == 0 or gamma == 0: # si son 0, log tira error
            perror("There are features with value 0 (noise?)", force_continue=True)

        return np.array([delta, theta, alpha, beta, gamma]) # Vector de features

    feature_vector_raw = obtain_feat_vector(PSD_raw)
    feature_vector_window = obtain_feat_vector(PSD_window)

    if plot_window:
        # Plot eegdata
        plt.subplot(2, 2, 1)
        plt.plot(eegdata)
        plt.title("Data")
        plt.xlabel("Time (not seconds)")
        plt.ylabel("Amplitude")

        # Plot hamming window
        plt.subplot(2, 2, 2)
        plt.plot(data_centered_ham)
        plt.title("Data with Hamming window applied")
        plt.xlabel("Time (not seconds)")
        plt.ylabel("Amplitude")


        # Plot FT with raw data
        index, = np.where(f==44) # Desde 44Hz hacia atras
        index = int(index[0])
        plt.subplot(2, 2, 3)
        plt.plot(f[:index], PSD_raw[:index])
        plt.title("FFT with raw data")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")

        # Plot FT with windowed data
        plt.subplot(2, 2, 4)
        plt.plot(f[:index], PSD_window[:index])
        plt.title("FFT with window data")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")

        # print("features: (delta, theta, alpha, beta, gamma)")
        print("features raw: ")
        print(feature_vector_raw)

        print("features window: ")
        print(feature_vector_window)

        plt.show()
        print("----------")

    # Aplicar log10
    feature_vector = np.log10(feature_vector_window)

    return list(feature_vector)

def compute_waves(t, channel, sample_rate=256, window=256, step=25, plot_window=False):
    """Compute the waves (delta, theta, alpha, beta, gamma) for a given channel

    Parameters:
    sample_rate -- sample rate of the measured data
    window -- size of the sliding window
    step -- step to slide the window
    plot_window -- bool, passed to compute_feature_vector_one"""

    feats = [] # Guardar waves (features)
    tiempo = [] # Guardar tiempo
    i = 0 # contador del slice
    n = len(channel)

    while i < n:
        channel_slice = channel[i:i+window]
        if(len(channel_slice) >= window):
            f = compute_feature_vector_one(channel_slice, sample_rate, plot_window)
            feats.append(f)
            tiempo.append(t[i])

        i += step

    # Transformar a matriz de numpy
    feats = np.matrix(feats)

    return tiempo, feats

def plot_waves(tiempo, feats, channel_name, subplots=False):
    """Plot (delta, theta, alpha, beta, gamma) waves in time."""

    # Tomar señales en todo el tiempo
    delta = feats[:, 0]
    theta = feats[:, 1]
    alpha = feats[:, 2]
    beta = feats[:, 3]
    gamma = feats[:, 4]

    def plot_wave(data, title, i):
        if subplots:
            plt.subplot(3, 2, i)
            plt.title(title)

        plt.plot(tiempo, data, label=title)

    plt.suptitle("Waves from ch {}".format(channel_name), fontsize=20)

    plot_wave(delta, "Delta", 1)
    plot_wave(theta, "Theta", 2)
    plot_wave(alpha, "Alpha", 3)
    plot_wave(beta, "Beta", 4)
    plot_wave(gamma, "Gamma", 5)

    plt.ylabel("dB")
    plt.xlabel("Tiempo (s)")

    if not subplots:
        plt.legend()

    plt.show()

def plot_raw(t, df, ch_names, subplots=False):
    """Plot raw channels."""

    i = 1
    for ch in ch_names:
        if subplots:
            plt.subplot(3, 2, i)
            i += 1
        plt.plot(t, df[ch].as_matrix(), label=ch)

    plt.suptitle("Raw channels", fontsize=20)
    plt.legend()
    plt.show()

def create_parser(ch_names):
    """Create the console arguments parser."""
    parser = argparse.ArgumentParser(description='Apply FFT to data', usage='%(prog)s [options]')

    group_data = parser.add_argument_group(title="File arguments")
    group_data.add_argument('-f', '--fname', default="data", type=str,
                        help="Name of the .csv file to read")
    group_data.add_argument('--subfolder', default=None, type=str,
                        help="Subfolder to read the .csv file")
    group_data.add_argument('--suffix', default=None, type=str,
                        help="Suffix to append to the filename")

    group_raw = parser.add_argument_group(title="Plot raw channels", description=None)
    group_raw.add_argument('--raw', action="store_true",
                        help="Plot the raw channels")
    group_raw.add_argument('--splot_raw', action="store_true",
                        help="Plot the raw channels in subplots instead of together")

    group_waves = parser.add_argument_group(title="Plot waves arguments", description=None)
    group_waves.add_argument('--waves', action="store_true",
                        help="Plot the delta, theta, alpha, beta and gamma waves extracted from a channel")
    group_waves.add_argument('--splot_waves', action="store_true",
                        help="Plot the waves in subplots instead of one plot")
    group_waves.add_argument('--channel', choices=ch_names, default=ch_names[0], type=str,
                        help="Channel to extract the waves from")
    group_waves.add_argument('--plot_window', action="store_true",
                        help="For each window of the data taken, plot the eegdata vs the frequency domain")

    return parser

def main():
    # QUESTION: como juntar todos los canales? o usarlos por separado?

    # Channel names
    ch_names = ['TP9', 'AF7', 'AF8', 'TP10']

    # Parse args
    parser = create_parser(ch_names)
    args = parser.parse_args()

    # Read the file
    df = read_data(args.fname, args.subfolder, args.suffix)

    # Tomar data
    channel = df[args.channel].as_matrix()
    t = df['timestamps']

    if args.waves:
        tiempo, feats = compute_waves(t, channel, plot_window=args.plot_window)
        plot_waves(tiempo, feats, args.channel, args.splot_waves)

    if args.raw:
        plot_raw(t, df, ch_names, args.splot_raw)

if __name__ == "__main__":
    main()
