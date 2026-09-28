import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as plotly_go
from plotly.subplots import make_subplots
import time
import json
import os
from datetime import datetime
from ml_engine import EdgeGuardMLEngine
from preprocessing import perform_fft

# Initialize ML Engine
ml_engine = EdgeGuardMLEngine()

# Page Config
st.set_page_config(page_title="EdgeGuard Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Industrial NOC look with Enhanced Colorful Sidebar
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* --- ENHANCED SIDEBAR --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
        border-right: 2px solid #38bdf8;
        box-shadow: 5px 0 20px rgba(56, 189, 248, 0.15);
    }
    
    [data-testid="stSidebar"] h3 {
        color: #38bdf8 !important;
        font-weight: 800 !important;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        border-bottom: 2px solid #38bdf8;
        padding-bottom: 5px;
        margin-top: 25px;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }

    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: rgba(30, 41, 59, 0.7);
        border: 1px solid #8b5cf6;
        color: white;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.2);
    }
    
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        font-weight: bold;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background-color: rgba(30, 41, 59, 0.5);
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .element-container:nth-of-type(4) button:hover {
        background-color: rgba(16, 185, 129, 0.2); border-color: #10b981; color: #10b981; box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
    }
    [data-testid="stSidebar"] .element-container:nth-of-type(5) button:hover {
        background-color: rgba(245, 158, 11, 0.2); border-color: #f59e0b; color: #f59e0b; box-shadow: 0 0 15px rgba(245, 158, 11, 0.4);
    }
    [data-testid="stSidebar"] .element-container:nth-of-type(6) button:hover {
        background-color: rgba(239, 68, 68, 0.2); border-color: #ef4444; color: #ef4444; box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
    }
    
    /* --- MAIN DASHBOARD CARDS --- */
    div.css-1r6slb0, div.css-12w0qpk {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 700 !important; color: #f8fafc !important; }
    [data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 14px !important; text-transform: uppercase; letter-spacing: 0.05em; }
    h1, h2 { color: #f1f5f9 !important; font-weight: 600 !important; }
    
    .status-normal { background-color: rgba(16, 185, 129, 0.2); color: #10b981; padding: 4px 12px; border-radius: 12px; font-weight: bold; border: 1px solid #10b981; }
    .status-warning { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; padding: 4px 12px; border-radius: 12px; font-weight: bold; border: 1px solid #f59e0b; }
    .status-fault { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 4px 12px; border-radius: 12px; font-weight: bold; border: 1px solid #ef4444; }
    hr { border-color: #374151; }
</style>
""", unsafe_allow_html=True)

# State Management
if 'events' not in st.session_state:
    st.session_state.events = []

def add_event(message, level):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.events.insert(0, {"Time": timestamp, "Event": message, "Status": level})
    if len(st.session_state.events) > 15:
        st.session_state.events.pop()

def send_hardware_command(command):
    cmd_file = "data/command.txt"
    os.makedirs(os.path.dirname(cmd_file), exist_ok=True)
    with open(cmd_file, "w") as f:
        f.write(command)
    add_event(f"Hardware command sent: {command}", "INFO")

def generate_demo_waveform(scenario, samples=128):
    t = np.linspace(0, 1, samples)
    if scenario == "NORMAL":
        wave = 0.1 * np.sin(2 * np.pi * 15 * t) + np.random.normal(0, 0.02, samples)
        return wave.tolist(), 41.2 + np.random.normal(0, 0.5), 0.85 + np.random.normal(0, 0.02)
    elif scenario == "WARNING":
        wave = 0.4 * np.sin(2 * np.pi * 15 * t) + 0.2 * np.sin(2 * np.pi * 45 * t) + np.random.normal(0, 0.1, samples)
        return wave.tolist(), 64.0 + np.random.normal(0, 1.5), 1.85 + np.random.normal(0, 0.1)
    else: 
        wave = 1.0 * np.sin(2 * np.pi * 15 * t) + 0.8 * np.sin(2 * np.pi * 85 * t) + np.random.normal(0, 0.3, samples)
        spike_indices = np.random.choice(samples, 5)
        wave[spike_indices] += np.random.uniform(1.5, 2.5, 5)
        return wave.tolist(), 91.0 + np.random.normal(0, 2.0), 3.10 + np.random.normal(0, 0.2)

def read_live_telemetry():
    filepath = "data/telemetry.jsonl"
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            if lines:
                return json.loads(lines[-1])
    except Exception:
        pass
    return None

# --- HEADER ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<h1>🛡️ EDGEGUARD <span style='font-size: 16px; color:#94a3b8; font-weight:normal;'>Autonomous Predictive Maintenance & Fault Detection</span></h1>", unsafe_allow_html=True)
with col2:
    mode_display = st.sidebar.radio("DATA SOURCE", ["🟢 DEMO / NO HARDWARE", "🔌 HARDWARE LIVE"])
    is_live = "HARDWARE LIVE" in mode_display
    
    if is_live:
        st.markdown(f"<div style='text-align:right; margin-top:15px;'><span class='status-normal'>● HARDWARE LIVE</span> <br> <span style='font-size:12px; color:#94a3b8;'>Protocol: UART / JSON | Latency: 12 ms</span></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:right; margin-top:15px;'><span class='status-warning'>● DEMO MODE</span> <br> <span style='font-size:12px; color:#94a3b8;'>Simulated Telemetry Pipeline</span></div>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top:0px; margin-bottom: 15px;'>", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.markdown("### 🎛️ OPERATOR CONTROL")
st.sidebar.markdown("<span style='color:#94a3b8; font-size: 13px;'>Select telemetry origin and simulation scenario.</span>", unsafe_allow_html=True)
st.sidebar.write("")

scenario = "NORMAL"
if not is_live:
    scenario = st.sidebar.selectbox("🎯 DEMO SCENARIO", ["NORMAL", "WARNING", "FAULT"])
else:
    st.sidebar.info("Hardware Live Mode Active. Telemetry driven by ESP32.")

st.sidebar.write("")
st.sidebar.markdown("### ⚡ MOTOR CONTROL")
st.sidebar.markdown("<span style='color:#94a3b8; font-size: 13px;'>Hardware relays and overrides.</span>", unsafe_allow_html=True)
st.sidebar.write("")

if st.sidebar.button("🟢 MOTOR ON"):
    send_hardware_command("ON") if is_live else add_event("Demo: Motor ON commanded", "INFO")
if st.sidebar.button("🟠 MOTOR OFF"):
    send_hardware_command("OFF") if is_live else add_event("Demo: Motor OFF commanded", "INFO")
if st.sidebar.button("🚨 EMERGENCY STOP"):
    send_hardware_command("STOP") if is_live else add_event("Demo: EMERGENCY STOP activated", "CRITICAL")

st.sidebar.markdown("<br><hr style='border-color: rgba(56, 189, 248, 0.2);'>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align: center; color: #64748b; font-size: 12px;'>EdgeGuard v1.0<br>Predictive Maintenance Engine</div>", unsafe_allow_html=True)

# --- DATA ACQUISITION & PROCESSING ---
if not is_live:
    wave_data, temp_val, curr_val = generate_demo_waveform(scenario)
    vib_rms = np.sqrt(np.mean(np.square(wave_data)))
    motor_state = "RUNNING" if scenario != "FAULT" else "STOPPED"
    relay_state = "ARMED" if scenario != "FAULT" else "TRIPPED"
else:
    telemetry = read_live_telemetry()
    if telemetry:
        wave_data = telemetry.get("waveform", [0]*128)
        temp_val = telemetry.get("temperature", 0)
        curr_val = telemetry.get("current", 0)
        vib_rms = telemetry.get("vibration_rms", 0)
        motor_state = "RUNNING" if telemetry.get("motor_state", 1) == 1 else "STOPPED"
        relay_state = "ARMED" if telemetry.get("motor_state", 1) == 1 else "TRIPPED"
    else:
        wave_data, temp_val, curr_val, vib_rms, motor_state, relay_state = [0]*128, 0, 0, 0, "UNKNOWN", "UNKNOWN"

# ML Prediction
classification, confidence = ml_engine.predict(temp_val, curr_val, vib_rms)
health_index = confidence * 100 if classification == "NORMAL_OPERATION" else (100 - (confidence * 100))

# Status Formatting
status_color_map = {"NORMAL_OPERATION": "status-normal", "EARLY_ABNORMALITY": "status-warning", "CRITICAL_FAULT": "status-fault"}
status_class = status_color_map.get(classification, "status-normal")

# --- KPI ROW ---
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("TEMPERATURE (°C)", f"{temp_val:.1f}", "DS18B20")
k2.metric("CURRENT (A)", f"{curr_val:.2f}", "ACS712")
k3.metric("VIBRATION RMS (g)", f"{vib_rms:.3f}", "ADXL345")
k4.metric("HEALTH SCORE", f"{health_index:.1f}%", "SVM Model")
k5.metric("PREDICTIVE RUL", "1200 h" if classification=="NORMAL_OPERATION" else ("240 h" if classification=="EARLY_ABNORMALITY" else "0 h"), "Estimated")

# --- MAIN DASHBOARD AREA ---
col_charts, col_status = st.columns([7, 3])

with col_charts:
    # Waveform Plot
    fig_wave = plotly_go.Figure()
    fig_wave.add_trace(plotly_go.Scatter(y=wave_data, mode='lines', line=dict(color='#0ea5e9', width=2)))
    fig_wave.update_layout(title="REAL-TIME DSP VIBRATION WAVEFORM", height=250, margin=dict(l=0, r=0, t=30, b=0),
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'),
                           xaxis=dict(showgrid=True, gridcolor='#374151', title="Samples"),
                           yaxis=dict(showgrid=True, gridcolor='#374151', title="Accel (g)"))
    st.plotly_chart(fig_wave, use_container_width=True)
    
    # FFT Plot
    freqs, magnitudes = perform_fft(wave_data, fs=200)
    fig_fft = plotly_go.Figure()
    fig_fft.add_trace(plotly_go.Scatter(x=freqs, y=magnitudes, mode='lines', line=dict(color='#8b5cf6', width=2), fill='tozeroy'))
    fig_fft.update_layout(title="FFT FREQUENCY SPECTRUM", height=200, margin=dict(l=0, r=0, t=30, b=0),
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'),
                          xaxis=dict(showgrid=True, gridcolor='#374151', title="Frequency (Hz)"),
                          yaxis=dict(showgrid=True, gridcolor='#374151', title="Magnitude"))
    st.plotly_chart(fig_fft, use_container_width=True)

with col_status:
    # Confidence Gauge
    st.markdown("### AI FAULT CLASSIFICATION")
    st.markdown(f"<div style='text-align:center; padding: 10px;'><span class='{status_class}' style='font-size:18px;'>{classification}</span></div>", unsafe_allow_html=True)
    
    fig_gauge = plotly_go.Figure(plotly_go.Indicator(
        mode = "gauge+number",
        value = confidence * 100,
        number = {'suffix': "%", 'font': {'color': '#f8fafc'}},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#374151"},
            'bar': {'color': "#10b981" if classification=="NORMAL_OPERATION" else ("#f59e0b" if classification=="EARLY_ABNORMALITY" else "#ef4444")},
            'bgcolor': "#1f2937",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.2)'},
                {'range': [50, 85], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [85, 100], 'color': 'rgba(16, 185, 129, 0.2)'}],
        }))
    fig_gauge.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Protection Status
    st.markdown("### ⚡ PROTECTION INTERLOCK")
    relay_color = "#10b981" if relay_state == "ARMED" else "#ef4444"
    motor_color = "#10b981" if motor_state == "RUNNING" else "#ef4444"
    st.markdown(f"""
    <div style='background-color:#1f2937; padding:15px; border-radius:8px; border:1px solid #374151;'>
        <p style='margin:0; font-size:14px; color:#94a3b8;'>RELAY STATUS</p>
        <p style='margin:0 0 10px 0; font-size:20px; font-weight:bold; color:{relay_color};'>{relay_state}</p>
        <p style='margin:0; font-size:14px; color:#94a3b8;'>MOTOR POWER</p>
        <p style='margin:0; font-size:20px; font-weight:bold; color:{motor_color};'>{motor_state}</p>
    </div>
    """, unsafe_allow_html=True)

# --- RECENT EVENTS ---
st.markdown("### 📋 RECENT EVENTS & ALERTS")
if classification != "NORMAL_OPERATION" and (len(st.session_state.events) == 0 or st.session_state.events[0]["Event"] != classification):
    add_event(f"AI Classification change: {classification}", "WARNING" if classification=="EARLY_ABNORMALITY" else "CRITICAL")

if st.session_state.events:
    df_events = pd.DataFrame(st.session_state.events)
    st.dataframe(df_events, use_container_width=True, hide_index=True)
else:
    st.info("No recent events logged.")

# Auto-refresh mechanism
time.sleep(1.0)
st.rerun()