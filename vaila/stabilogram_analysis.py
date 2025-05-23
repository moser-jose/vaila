"""
Module: stabilogram_analysis.py
Description:
This module provides a comprehensive set of functions for analyzing Center of Pressure (CoP) data obtained from force plate measurements in postural control studies. The functions included in this module allow for the calculation of various stabilometric parameters and the generation of stabilogram plots to evaluate balance and stability.

The main features of this module include:
- **Root Mean Square (RMS) Calculation**: Computes the RMS of the CoP displacement in the mediolateral (ML) and anteroposterior (AP) directions, providing a measure of postural sway.
- **Speed Computation**: Calculates the instantaneous speed of the CoP using a Savitzky-Golay filter to smooth the data, allowing for analysis of the dynamics of postural control.
- **Power Spectral Density (PSD) Analysis**: Computes the PSD of the CoP signals using Welch's method, providing insight into the frequency components of postural sway.
- **Mean Square Displacement (MSD) Calculation**: Calculates the MSD over a specified time interval, which can be used to analyze the temporal characteristics of postural sway.
- **Zero-Crossings and Peaks Count**: Identifies and counts the zero-crossings and peaks in the CoP signals, which can be used to assess the regularity and variability of postural control.
- **Sway Density Calculation**: Computes the sway density of the CoP data, a measure that reflects the concentration of CoP points within a given radius over time.
- **Total Path Length Computation**: Calculates the total distance traveled by the CoP, providing a measure of the overall effort required to maintain balance.
- **Stabilogram Plotting**: Generates time series plots (stabilograms) for ML and AP CoP displacements to visualize postural sway.
- **Power Spectrum Plotting**: Creates plots of the power spectral density, highlighting maximum PSD values, their corresponding frequencies, and median frequencies to evaluate the distribution of sway energy across different frequencies.
- **CSV Export of Metrics**: Saves computed metrics to a CSV file with standardized headers, ensuring compatibility with other data analysis tools.

Author: Prof. Dr. Paulo R. P. Santiago
Version: 1.3
Date: 2024-09-12

References:
- GitHub Repository: Code Descriptors Postural Control. https://github.com/Jythen/code_descriptors_postural_control
- "Physiological Reports" - A detailed article on the usage of stabilogram analysis in postural control research. https://doi.org/10.14814/phy2.15067

Changelog:
- Version 1.3 (2024-09-12):
  - Enhanced `plot_power_spectrum` function to include indicators for maximum PSD values and their corresponding frequencies.
  - Introduced `compute_total_path_length` function to calculate the total path length of the CoP trajectory.
  - Updated function signatures and internal logic for compatibility with `cop_analysis.py`.
  - Standardized CSV output headers for improved interoperability with data processing pipelines.
  - Improved stability and performance of all analytical functions.

Usage:
To use the functions in this module for CoP analysis, import the module and call the desired functions:

```python
from stabilogram_analysis import *

# Example usage:
rms_ml, rms_ap = compute_rms(cop_x, cop_y)
speed_ml, speed_ap = compute_speed(cop_x, cop_y, fs)
plot_stabilogram(time, cop_x, cop_y, output_path)
compute_msd(S_n, fs, delta_t)
# and so on.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, savgol_filter, find_peaks


def compute_rms(cop_x, cop_y):
    """
    Calculates the RMS displacement in the ML and AP directions.

    Parameters:
    - cop_x: array-like
        CoP data in the ML direction.
    - cop_y: array-like
        CoP data in the AP direction.

    Returns:
    - rms_ml: float
        RMS displacement in the ML direction.
    - rms_ap: float
        RMS displacement in the AP direction.
    """
    rms_ml = np.sqrt(np.mean(cop_x**2))
    rms_ap = np.sqrt(np.mean(cop_y**2))
    return rms_ml, rms_ap


def compute_speed(cop_x, cop_y, fs, window_length=5, polyorder=3):
    """
    Calculates the speed of the CoP signal using the Savitzky-Golay filter.

    Parameters:
    - cop_x: array-like
        CoP data in the ML direction.
    - cop_y: array-like
        CoP data in the AP direction.
    - fs: float
        Sampling frequency in Hz.
    - window_length: int, default=5
        Length of the filter window (number of coefficients).
    - polyorder: int, default=3
        Order of the polynomial used to fit the samples.

    Returns:
    - speed_ml: array-like
        Speed in the ML direction.
    - speed_ap: array-like
        Speed in the AP direction.
    """
    delta = 1 / fs
    # Ensure window_length is odd and less than data length
    window_length = min(window_length, len(cop_x) // 2 * 2 - 1)
    if window_length % 2 == 0:
        window_length += 1
    speed_ml = savgol_filter(cop_x, window_length, polyorder, deriv=1, delta=delta)
    speed_ap = savgol_filter(cop_y, window_length, polyorder, deriv=1, delta=delta)
    return speed_ml, speed_ap


def compute_power_spectrum(cop_x, cop_y, fs):
    """
    Calculates the Power Spectral Density (PSD) of the CoP signals.

    Parameters:
    - cop_x: array-like
        CoP data in the ML direction.
    - cop_y: array-like
        CoP data in the AP direction.
    - fs: float
        Sampling frequency in Hz.

    Returns:
    - freqs_ml: array-like
        Frequencies for ML PSD.
    - psd_ml: array-like
        PSD values for the ML direction.
    - freqs_ap: array-like
        Frequencies for AP PSD.
    - psd_ap: array-like
        PSD values for the AP direction.
    """
    freqs_ml, psd_ml = welch(cop_x, fs=fs, nperseg=256)
    freqs_ap, psd_ap = welch(cop_y, fs=fs, nperseg=256)
    return freqs_ml, psd_ml, freqs_ap, psd_ap


def compute_msd(S_n, fs, delta_t):
    """
    Calculates the Mean Square Displacement (MSD) for a time interval delta_t.

    Parameters:
    - S_n: array-like
        Centered signal (X_n or Y_n).
    - fs: float
        Sampling frequency in Hz.
    - delta_t: float
        Time interval in seconds.

    Returns:
    - msd: float
        MSD value.
    """
    delta_n = int(delta_t * fs)
    N = len(S_n)
    if delta_n >= N:
        raise ValueError("delta_t is too large for the signal length.")
    diff = S_n[delta_n:] - S_n[:-delta_n]
    msd = np.mean(diff**2)
    return msd


def count_zero_crossings(signal):
    """
    Counts the number of zero-crossings in a signal.

    Parameters:
    - signal: array-like
        Signal to be analyzed.

    Returns:
    - zero_crossings: int
        Number of zero-crossings.
    """
    zero_crossings = ((signal[:-1] * signal[1:]) < 0).sum()
    return zero_crossings


def count_peaks(signal):
    """
    Counts the number of peaks in a signal.

    Parameters:
    - signal: array-like
        Signal to be analyzed.

    Returns:
    - num_peaks: int
        Number of detected peaks.
    """
    peaks, _ = find_peaks(signal)
    num_peaks = len(peaks)
    return num_peaks


def compute_sway_density(cop_signal, fs, radius=0.3):
    """
    Calculates the sway density of the CoP signal.

    Parameters:
    - cop_signal: array-like or ndarray
        CoP data, can be 1D or 2D array.
    - fs: float
        Sampling frequency in Hz.
    - radius: float, default=0.3
        Radius in cm for sway density calculation.

    Returns:
    - sway_density: array-like
        Sway density values.
    """
    N = len(cop_signal)
    sway_density = np.zeros(N)
    for t in range(N):
        distances = np.abs(cop_signal - cop_signal[t])
        sway_density[t] = np.sum(distances <= radius) / N
    return sway_density


def compute_total_path_length(cop_x, cop_y):
    """
    Calculates the total path length of the CoP trajectory.

    Parameters:
    - cop_x: array-like
        CoP data in the ML direction.
    - cop_y: array-like
        CoP data in the AP direction.

    Returns:
    - total_path_length: float
        Total path length in cm.
    """
    diffs_x = np.diff(cop_x)
    diffs_y = np.diff(cop_y)
    distances = np.sqrt(diffs_x**2 + diffs_y**2)
    total_path_length = np.sum(distances)
    return total_path_length


def plot_stabilogram(time, cop_x, cop_y, output_path):
    """
    Plots and saves the stabilogram as time series plots for ML and AP displacements.

    Parameters:
    - time: array-like
        Time vector.
    - cop_x: array-like
        CoP data in the ML direction.
    - cop_y: array-like
        CoP data in the AP direction.
    - output_path: str
        Path to save the stabilogram plot.
    """
    plt.figure(figsize=(12, 8))

    # Subplot for ML displacement
    plt.subplot(2, 1, 1)
    plt.plot(time, cop_x, color="black", linewidth=2)
    plt.title("Stabilogram - ML Displacement")
    plt.xlabel("Time (s)")
    plt.ylabel("ML Displacement (cm)")
    plt.grid(True)

    # Calculate and display min, max, and RMS
    min_ml = np.min(cop_x)
    max_ml = np.max(cop_x)
    rms_ml = np.sqrt(np.mean(cop_x**2))
    plt.axhline(min_ml, color="grey", linestyle="--", label=f"Min: {min_ml:.2f} cm")
    plt.axhline(max_ml, color="grey", linestyle="-.", label=f"Max: {max_ml:.2f} cm")
    plt.axhline(rms_ml, color="grey", linestyle=":", label=f"RMS: {rms_ml:.2f} cm")
    plt.legend()

    # Subplot for AP displacement
    plt.subplot(2, 1, 2)
    plt.plot(time, cop_y, color="black", linewidth=2)
    plt.title("Stabilogram - AP Displacement")
    plt.xlabel("Time (s)")
    plt.ylabel("AP Displacement (cm)")
    plt.grid(True)

    # Calculate and display min, max, and RMS
    min_ap = np.min(cop_y)
    max_ap = np.max(cop_y)
    rms_ap = np.sqrt(np.mean(cop_y**2))
    plt.axhline(min_ap, color="grey", linestyle="--", label=f"Min: {min_ap:.2f} cm")
    plt.axhline(max_ap, color="grey", linestyle="-.", label=f"Max: {max_ap:.2f} cm")
    plt.axhline(rms_ap, color="grey", linestyle=":", label=f"RMS: {rms_ap:.2f} cm")
    plt.legend()

    plt.tight_layout()
    plt.savefig(f"{output_path}_stabilogram.png", dpi=300)
    plt.savefig(f"{output_path}_stabilogram.svg", dpi=300)
    plt.close()


def plot_power_spectrum(freqs_ml, psd_ml, freqs_ap, psd_ap, output_path):
    """
    Plots and saves the power spectrum of the CoP signals in PNG and SVG formats, including indicators for maximum PSD values and frequencies.

    Parameters:
    - freqs_ml: array-like
        Frequencies for ML PSD.
    - psd_ml: array-like
        PSD values for the ML direction.
    - freqs_ap: array-like
        Frequencies for AP PSD.
    - psd_ap: array-like
        PSD values for the AP direction.
    - output_path: str
        Path to save the power spectrum plot.
    """
    plt.figure(figsize=(10, 8))
    plt.semilogy(freqs_ml, psd_ml, label="ML")
    plt.semilogy(freqs_ap, psd_ap, label="AP")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("PSD (cm²/Hz)")
    plt.title("Power Spectral Density")
    plt.grid(True)

    # Find maximum PSD values and their frequencies
    max_psd_ml = np.max(psd_ml)
    max_freq_ml = freqs_ml[np.argmax(psd_ml)]
    max_psd_ap = np.max(psd_ap)
    max_freq_ap = freqs_ap[np.argmax(psd_ap)]

    # Plot markers for maximum PSD values
    plt.scatter(
        max_freq_ml,
        max_psd_ml,
        color="blue",
        marker="v",
        label=f"Max ML PSD: {max_psd_ml:.2e} at {max_freq_ml:.2f} Hz",
    )
    plt.scatter(
        max_freq_ap,
        max_psd_ap,
        color="orange",
        marker="v",
        label=f"Max AP PSD: {max_psd_ap:.2e} at {max_freq_ap:.2f} Hz",
    )

    # Calculate median frequencies
    median_freq_ml = np.median(freqs_ml)
    median_freq_ap = np.median(freqs_ap)

    # Plot vertical lines for median frequencies
    plt.axvline(
        median_freq_ml,
        color="blue",
        linestyle="--",
        label=f"Median ML Frequency: {median_freq_ml:.2f} Hz",
    )
    plt.axvline(
        median_freq_ap,
        color="orange",
        linestyle="--",
        label=f"Median AP Frequency: {median_freq_ap:.2f} Hz",
    )

    plt.legend()
    plt.savefig(f"{output_path}_psd.png", dpi=300)
    plt.savefig(f"{output_path}_psd.svg", dpi=300)
    plt.close()


def save_metrics_to_csv(metrics_dict, output_path):
    """
    Saves the calculated metrics to a CSV file with standardized headers.

    Parameters:
    - metrics_dict: dict
        Dictionary containing the metrics to save.
    - output_path: str
        Path to save the metrics CSV file.
    """
    import pandas as pd

    # Standardize headers
    standardized_metrics = {}
    for key, value in metrics_dict.items():
        new_key = (
            key.replace(" ", "_")
            .replace("(", "_")
            .replace(")", "")
            .replace("²", "2")
            .replace("·", "_")
            .replace("³", "3")
        )
        standardized_metrics[new_key] = value

    df = pd.DataFrame([standardized_metrics])
    df.to_csv(f"{output_path}_metrics.csv", index=False)
