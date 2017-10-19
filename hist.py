"""Analyze with histograms."""
from scipy.stats import norm
from backend import filesystem, plots

# TODO: merge this in plotdata.py

def main():
    power = filesystem.load_waves("test_eyes", "TP9")

    for i in range(len(power.columns)):
        col = list(power.columns)[i]
        wave_data = power[col].as_matrix()

        mu, sd = norm.fit(wave_data)
        plots.plot_histogram(wave_data, norm.pdf, (mu, sd), title=col)

if __name__ == "__main__":
    main()
