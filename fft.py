#/usr/bin/env python
"""Script that analyses data with a fourier transform"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import data_mng


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

    print(w)
    input()

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

def compute_feature_vector_one(eegdata, Fs):
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
    dataWinCentered = eegdata - np.mean(eegdata) # Remove offset # QUESTION: pq restar el promedio?
    dataWinCenteredHam = (dataWinCentered.T*w).T

    ## FFT
    Y = np.fft.fft(dataWinCenteredHam) #, n=NFFT) #, axis=0)
    Y = Y/n_samples ## QUESTION: pq esto?

    ## Tomar arreglo de frecuencias
    n_freqs = int(n_samples/2)
    PSD = 2*np.abs(Y[0:n_freqs]) # Transformar numero complejo a real # QUESTION: pq *2 ??
    f = Fs/2*np.linspace(0,1,n_freqs) # Tomar rango de frecuencias


    ## Filtrar por frecuencias
    # Delta < 4
    ind_delta, = np.where(f<4)
    delta = np.sum(PSD[ind_delta])

    # Theta 4-8
    ind_theta, = np.where((f>=4) & (f<=8))
    theta = np.sum(PSD[ind_theta])

    # Alpha 8 - 12
    ind_alpha, = np.where((f>=8) & (f<=12))
    alpha = np.sum(PSD[ind_alpha])

    # Beta 12-30
    ind_beta, = np.where((f>=12) & (f<=30))
    beta = np.sum(PSD[ind_beta])

    # Gamma 30>
    ind_gamma, = np.where((f>=30) & (f<=44))
    gamma = np.sum(PSD[ind_gamma])


    feature_vector = np.array([delta, theta, alpha, beta, gamma])


    good = True

    # Revisar si son 0, log tira error
    if beta == 0 or delta == 0 or theta == 0 or alpha == 0 or gamma == 0:
        good = False

    feature_vector = np.log10(feature_vector)

    return list(feature_vector), good

def create_parser():
    """ Create the console arguments parser"""
    parser = argparse.ArgumentParser(description='Apply FFT to data', usage='%(prog)s [options]')

    group_data = parser.add_argument_group(title="Data arguments")
    group_data.add_argument('-f', '--filename', default="dump", type=str,
                        help="Name of the .csv file to read")
    group_data.add_argument('-d', '--dir', default=None, type=str,
                        help="Subfolder to read the .csv file")

    group_plot = parser.add_argument_group(title="Plot arguments", description=None)
    group_plot.add_argument('-a', '--all', action="store_true",
                        help="Plot all the waves in the same figure. Else, use subplots")

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    # Read the file
    df = data_mng.read_data(args.filename, args.dir)

    # Some information about the channels
    ch_names = ['TP9', 'AF7', 'AF8', 'TP10']

    # Tomar data
    # data = df[ch_names].as_matrix()
    a = df['TP10'].as_matrix()

    t = df['timestamps']

    # tp10 = df['TP10'].as_matrix()
    # tp9 = df['TP9'].as_matrix()
    # af7 = df['AF7'].as_matrix()
    # af8 = df['AF8'].as_matrix()
    #
    # # plt.plot(t, tp10, label='tp10')
    # plt.plot(t, tp9, label='tp9')
    # plt.plot(t, af7, label='af7')
    # plt.plot(t, af8, label='af8')
    #
    # plt.xlim(20, 40)
    # plt.legend()
    # plt.show()
    #
    # sys.exit(0)

    # Sampling rate
    sample_rate = 256  # Hz
    window = 256 # amount of data to take at once
    step = 25 # Step to move the window each time
    feats = []
    tiempo = []
    i = 0
    n = len(a)
    contador_malos = 0
    while i < n:
        b = a[i:i+window]
        if(len(b) >= window):
            f, good = compute_feature_vector_one(b, sample_rate)
            if good:
                feats.append(f)
                tiempo.append(t[i])
            else:
                contador_malos += 1
        i += step

    feats = np.matrix(feats)
    tiempo = np.matrix(tiempo)

    print("cantidad de veces con solo 0s: {}".format(contador_malos))

    delta = feats[:, 0]
    theta = feats[:, 1]
    alpha = feats[:, 2]
    beta = feats[:, 3]
    gamma = feats[:, 4]


    def plot_wave(data, title, i):
        t = range(len(data))
        if not args.all:
            plt.subplot(3, 2, i)
            plt.title(title)

        plt.plot(t, data, label=title)

    plot_wave(delta, "Delta", 1)
    plot_wave(theta, "Theta", 2)
    plot_wave(alpha, "Alpha", 3)
    plot_wave(beta, "Beta", 4)
    plot_wave(gamma, "Gamma", 5)

    plt.ylabel("dB")
    plt.xlabel("Tiempo (no en segundos)")
    plt.legend()
    plt.show()

    # n = len(feats)
    # plt.plot(range(n), feats)
    # plt.show()

if __name__ == "__main__":
    main()
