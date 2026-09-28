import numpy as np
from scipy.fft import fft, fftfreq

def perform_fft(waveform_data, fs=200):
    """
    Computes the Fast Fourier Transform of the vibration waveform.
    
    Args:
        waveform_data (list or numpy array): The raw vibration samples.
        fs (int): Sampling frequency in Hz.
        
    Returns:
        tuple: (frequencies, magnitudes) for the positive half of the spectrum.
    """
    N = len(waveform_data)
    if N == 0:
        return [], []
        
    # Apply Hanning window to reduce spectral leakage
    window = np.hanning(N)
    windowed_data = np.array(waveform_data) * window
    
    # Compute FFT
    yf = fft(windowed_data)
    xf = fftfreq(N, 1/fs)
    
    # Take only the positive half of the spectrum
    pos_mask = xf >= 0
    freqs = xf[pos_mask]
    magnitudes = 2.0/N * np.abs(yf[pos_mask])
    
    return freqs.tolist(), magnitudes.tolist()

def extract_features(temperature, current, vibration_rms):
    """Formats features for the ML model."""
    return np.array([[temperature, current, vibration_rms]])