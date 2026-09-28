import numpy as np
from scipy.fft import fft, fftfreq

def perform_fft(waveform_data, fs=200):
    N = len(waveform_data)
    if N == 0:
        return [], []
        
    window = np.hanning(N)
    windowed_data = np.array(waveform_data) * window
    
    yf = fft(windowed_data)
    xf = fftfreq(N, 1/fs)
    
    pos_mask = xf >= 0
    freqs = xf[pos_mask]
    magnitudes = 2.0/N * np.abs(yf[pos_mask])
    
    return freqs.tolist(), magnitudes.tolist()

def extract_features(temperature, current, vibration_rms):
    return np.array([[temperature, current, vibration_rms]])