#/usr/bin/env python
"""Script that analyses data with a fourier transform"""

import numpy as np
# import mne
import pandas as pd
import matplotlib.pyplot as plt
import argparse

def using_np():
    def create_parser():
        """Create the console arguments parser"""
        parser = argparse.ArgumentParser(description='Apply Fourier transformations and plot', usage='%(prog)s [options]')

        parser.add_argument('-c', '--cols', nargs='+',
                            help="Columns to apply the transformation")
        parser.add_argument('-f', '--filename', default="dump", type=str,
                            help="Name of the csv to load")
        parser.add_argument('-d', '--dir', default="data", type=str,
                            help="Folder of the csv")
        parser.add_argument('-s', '--slice', default=None, type=int,
                            help="First n numbers to grab")


        return parser

    def get_fourier(df, col, sl=None):
        arr = df[col].as_matrix()
        if not sl is None:
            arr = arr[:sl]
        return abs(np.fft.fft(arr))

    def plot_fourier(f, col, show=False):
        x = range(len(f))
        plt.plot(x, f)
        plt.title(col)

        if show:
            plt.show()

    parser = create_parser()
    args = parser.parse_args()

    filename = args.dir + "/" + args.filename
    ext = ".csv"
    if not filename.endswith(ext):
        filename += ext

    df = pd.read_csv(filename, index_col=0)

    if args.cols is None:
        cols = list(df.columns)
    else:
        cols = args.cols

    i = 1
    for c in cols:
        f = get_fourier(df, c, sl=args.slice)
        plt.subplot(2, 3, i)#"22{}".format(i))

        i += 1

        plot_fourier(f, c)

    plt.show()

def using_mne():
    df = pd.read_csv("data/data.csv", index_col=0)

    # Some information about the channels
    ch_names = ['TP9', 'AF7', 'AF8', 'TP10']
    ch_types = ['eeg', 'eeg', 'eeg', 'eeg']

    df = df[ch_names]

    # Sampling rate
    sfreq = 500  # Hz

    # Create the info structure needed by MNE
    info = mne.create_info(ch_names=ch_names, ch_types=ch_types, sfreq=sfreq)


    # Tomar datos
    data = df.as_matrix().transpose()

    # Finally, create the Raw object
    raw = mne.io.RawArray(data, info)

    # raw.plot_psd(tmax=np.inf)

    def plot_wave(fmin, fmax, title, i):
        alpha = raw.filter(fmin,fmax, method='iir')
        a, t = alpha.get_data(start=1000, return_times=True)
        tp9 = a[0]
        af7 = a[1]
        af8 = a[2]
        tp10 = a[3]

        plt.subplot(3, 2, i)
        plt.plot(t, tp9 + af7 + af8 + tp10)
        plt.title(title)
        # plt.show()

    plot_wave(1, 4, "Delta", 1)
    plot_wave(4, 18, "Theta", 2)
    plot_wave(8, 13, "Alpha", 3)
    plot_wave(13, 30, "Beta", 4)
    plot_wave(30, 44, "Gamma", 5)

    plt.show()

def using_workshop():
    def nextpow2(i):
        """ Find the next power of 2 for number i """
        n = 1
        while n < i:
            n *= 2
        return n

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

    sd = []

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

        # Apply Hamming window
        w = np.hamming(n_samples)

        dataWinCentered = eegdata# - np.mean(eegdata) # Remove offset
        dataWinCenteredHam = (dataWinCentered.T*w).T

        Y = np.fft.fft(dataWinCenteredHam) #, n=NFFT) #, axis=0)
        Y = Y/n_samples

        n_freqs = int(n_samples/2)

        PSD = 2*np.abs(Y[0:n_freqs]) # Transformar numero complejo a real # QUESTION: pq *2 ??
        f = Fs/2*np.linspace(0,1,n_freqs) # Tomar rango de frecuencias

        # SPECTRAL FEATURES
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

        # Revisar si son 0, log tira error
        if beta == 0 or delta == 0 or theta == 0 or alpha == 0 or gamma == 0:
            print(feature_vector)
            print(eegdata)
            print(i)


        feature_vector = np.log10(feature_vector)
        sd.append(np.std(feature_vector))

        return list(feature_vector)



    df = pd.read_csv("data/data.csv", index_col=0)

    # Some information about the channels
    ch_names = ['TP9', 'AF7', 'AF8', 'TP10']



    # Tomar data
    # data = df[ch_names].as_matrix()
    a = df['AF7'].as_matrix()


    # Sampling rate
    sample_rate = 256  # Hz
    window = 256 # amount of data to take at once
    step = 25 # Step to move the window each time
    feats = []
    i = 0
    n = len(a)
    while i < n:
        b = a[i:i+window]
        if(len(b) >= window):
            feats.append(compute_feature_vector_one(b, sample_rate))
        i += step

    sd = np.array(sd)
    # print(np.mean(sd))

    feats = np.matrix(feats)
    # print(len(feats))
    # print(feats)

    delta = feats[:, 0]
    theta = feats[:, 1]
    alpha = feats[:, 2]
    beta = feats[:, 3]
    gamma = feats[:, 4]

    def plot_wave(data, title, i):
        global plot_i

        t = range(len(data))
        plt.subplot(3, 2, i)
        plt.plot(t, data)
        plt.title(title)
        # plt.show()

    plot_wave(delta, "Delta", 1)
    plot_wave(theta, "Theta", 2)
    plot_wave(alpha, "Alpha", 3)
    plot_wave(beta, "Beta", 4)
    plot_wave(gamma, "Gamma", 5)

    plt.show()

    # n = len(feats)
    # plt.plot(range(n), feats)
    # plt.show()



if __name__ == "__main__":
    using_workshop()
