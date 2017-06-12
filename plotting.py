#/usr/bin/env python
"""Script that analyses data with a fourier transform"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from basic.data_manager import read_data


"""Basado en codigo de: https://github.com/NeuroTechX/bci-workshop"""
def compute_feature_vector(eegdata, Fs):
    """Extract the features from the EEG
    Inputs:
    eegdata: array of dimension [number of samples, number of channels]
    Fs: sampling frequency of eegdata

    Outputs:
    feature_vector: [number of features points; number of different features]


    """

    n_samples, n_channels = eegdata.shape

    ### 1. Compute the PSD # Power Spectral Density

    # Apply Hamming window
    w = np.hamming(n_samples)

    # print(w)
    # input()

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

def compute_feature_vector_one(eegdata, Fs, plot_windows=False):
    """Extract the features from the EEG, only with one axis
    Inputs:
    eegdata: array of dimension [number of samples]
    Fs: sampling frequency of eegdata

    Outputs:
    feature_vector: [number of features points; number of different features]

    """

    n_samples = len(eegdata)

    ### 1. Compute the PSD # Power Spectral Density

    ## Apply Hamming window
    w = np.hamming(n_samples)
    dataWinCentered = eegdata - np.mean(eegdata) # Remove offset # no interesa el offset de la onda
    dataWinCenteredHam = (dataWinCentered.T*w).T # QUESTION: pq una hamming window? que es lo que hace?

    ## FFT
    Y = np.fft.fft(dataWinCenteredHam) #, n=NFFT) #, axis=0)
    Y = Y/n_samples # para que este en la misma escala de los datos

    # Rango que interesa de FFT
    n_freqs = int(n_samples/2) + 1 # Tomar hasta n_freqs + 1
    PSD = np.abs(Y[0:n_freqs]) # Transformar numero complejo a real
    PSD = 2*PSD # sumar freqs positivas (0:n/2) con freqs negativas (n/2:n) para obtener amplitud total
        # Aunque, 0 y la freq de nyquist  no tienen mirror --> no hay que multiplicarlos por dos
        # Pero PSD[0] = 0 --> pq se removio el offset de los datos
        # PSD[-1] no interesa, pq es muy alto

    # Tomar rango de frecuencias
    f = np.linspace(0,Fs/2,n_freqs)
        # Fs/2: nyquist frequency
        # rango entre 0 y nyquist, en n_freqs intervalos


    ## Filtrar por frecuencias
    def filter_wrapper(PSD, condition):
        index, = np.where(condition)
        return np.mean(PSD[index]) # QUESTION: usar mean, sum, ifft?

    # Delta < 4
    delta = filter_wrapper(PSD, (f<4))

    # Theta 4-8
    theta = filter_wrapper(PSD, (f>=4) & (f<=8))

    # Alpha 8 - 12
    alpha = filter_wrapper(PSD, (f>=8) & (f<=12))

    # Beta 12-30
    beta = filter_wrapper(PSD, (f>=12) & (f<=30))

    # Gamma 30-44
    gamma = filter_wrapper(PSD, (f>=30) & (f<=44))


    # Vector de features
    feature_vector = np.array([delta, theta, alpha, beta, gamma])


    if plot_windows:
        # Plot eegdata
        plt.subplot(2, 1, 1)
        plt.plot(eegdata)
        plt.xlabel("Time (not seconds)")
        plt.ylabel("Amplitude")

        index, = np.where(f==44)
        index = int(index[0])

        # Plot FT
        plt.subplot(2, 1, 2)
        plt.plot(f[:index], PSD[:index])
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")

        print(feature_vector)
        plt.show()


    # Bool indicando si anda bien
    good = True
    if beta == 0 or delta == 0 or theta == 0 or alpha == 0 or gamma == 0: # si son 0, log tira error
        good = False

    # Aplicar log10
    feature_vector = np.log10(feature_vector)

    return list(feature_vector), good


def compute_waves(t, channel, sample_rate=256, window=256, step=25, plot_windows=False):
    """Compute the waves (alpha, beta, etc) for a given channel"""
    feats = [] # Guardar waves (features)
    tiempo = [] # Guardar tiempo
    i = 0 # contador del slice
    n = len(channel)
    contador_malos = 0

    while i < n:
        channel_slice = channel[i:i+window]
        if(len(channel_slice) >= window):
            f, good = compute_feature_vector_one(channel_slice, sample_rate, plot_windows)
            if good:
                feats.append(f)
                tiempo.append(t[i])
            else:
                contador_malos += 1
        i += step

    if contador_malos > 0:
        print("There were {} times that a channel got a 0 value (likely noise)".format(contador_malos))

    # Transformar a matriz de numpy
    feats = np.matrix(feats)

    return tiempo, feats

def plot_waves(tiempo, feats, channel_name, subplots=False):
    """Plot alpha, beta, etc waves in time """

    # Tomar señales por separado
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
    """Plot raw channels """
    for ch in ch_names:
        plt.plot(t, df[ch].as_matrix(), label=ch)

    plt.suptitle("Raw channels", fontsize=20)
    plt.legend()
    plt.show()


def create_parser(ch_names):
    """ Create the console arguments parser"""
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
    # QUESTION: como juntar todos los canales?
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
        tiempo, feats = compute_waves(t, channel, plot_windows=args.plot_window)
        plot_waves(tiempo, feats, args.channel, args.splot_waves)

    if args.raw:
        plot_raw(t, df, ch_names, args.splot_raw)

if __name__ == "__main__":
    main()
