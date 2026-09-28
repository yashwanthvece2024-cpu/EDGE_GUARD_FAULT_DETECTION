import time
import json
import random
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

from config import TELEMETRY_FILE
from preprocessing import calculate_health_index
from ml_engine import predict


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="EdgeGuard | Predictive Maintenance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 80% 10%, rgba(0, 180, 255, 0.10), transparent 25%),
        radial-gradient(circle at 20% 80%, rgba(120, 50, 255, 0.10), transparent 30%),
        #050914;
    color: #e8f3ff;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #071226 0%,
        #050914 100%
    );
    border-right: 1px solid #12365c;
}

[data-testid="stMetric"] {
    background: linear-gradient(
        135deg,
        rgba(10, 27, 52, 0.95),
        rgba(7, 16, 32, 0.95)
    );
    border: 1px solid #174c79;
    padding: 18px;
    border-radius: 15px;
}

[data-testid="stMetricValue"] {
    color: #e9f7ff;
}

h1 {
    color: #eaf8ff;
}

h2, h3 {
    color: #bde9ff;
}

.demo-box {
    padding: 15px;
    border-radius: 15px;
    border: 1px solid #174c79;
    background: linear-gradient(
        135deg,
        rgba(8, 30, 58, 0.95),
        rgba(22, 10, 55, 0.95)
    );
}

.normal {
    color: #00e676;
    font-weight: bold;
}

.warning {
    color: #ffd54f;
    font-weight: bold;
}

.fault {
    color: #ff5252;
    font-weight: bold;
}

.live {
    color: #00e5ff;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "mode" not in st.session_state:
    st.session_state.mode = "DEMO"

if "scenario" not in st.session_state:
    st.session_state.scenario = "NORMAL"

if "demo_temperature" not in st.session_state:
    st.session_state.demo_temperature = 42.0

if "demo_current" not in st.session_state:
    st.session_state.demo_current = 0.9

if "demo_vibration" not in st.session_state:
    st.session_state.demo_vibration = 0.20

if "history" not in st.session_state:
    st.session_state.history = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []


# ============================================================
# FUNCTIONS
# ============================================================

def generate_demo_values(scenario):

    if scenario == "NORMAL":

        temperature = random.uniform(36, 45)
        current = random.uniform(0.65, 1.05)
        vibration = random.uniform(0.08, 0.22)

    elif scenario == "WARNING":

        temperature = random.uniform(55, 68)
        current = random.uniform(1.5, 2.2)
        vibration = random.uniform(0.35, 0.65)

    elif scenario == "FAULT":

        temperature = random.uniform(78, 90)
        current = random.uniform(2.7, 3.8)
        vibration = random.uniform(0.80, 1.30)

    elif scenario == "OVERHEATING":

        temperature = random.uniform(78, 95)
        current = random.uniform(1.5, 2.5)
        vibration = random.uniform(0.20, 0.50)

    elif scenario == "HIGH VIBRATION":

        temperature = random.uniform(45, 60)
        current = random.uniform(0.9, 1.7)
        vibration = random.uniform(0.75, 1.40)

    else:

        temperature = st.session_state.demo_temperature
        current = st.session_state.demo_current
        vibration = st.session_state.demo_vibration

    return {
        "temperature": round(temperature, 2),
        "current": round(current, 2),
        "vibration_rms": round(vibration, 3),
        "motor_state": 1,
        "source": "SIMULATION"
    }


def read_hardware():

    try:

        if not TELEMETRY_FILE.exists():
            return None

        with open(
            TELEMETRY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            lines = f.readlines()

        if not lines:
            return None

        return json.loads(lines[-1])

    except Exception:
        return None


def get_data():

    if st.session_state.mode == "DEMO":

        data = generate_demo_values(
            st.session_state.scenario
        )

    else:

        data = read_hardware()

        if data is None:
            return {
                "temperature": 0,
                "current": 0,
                "vibration_rms": 0,
                "motor_state": 0,
                "source": "WAITING"
            }

    return data


def add_history(data, result):

    point = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "temperature": data["temperature"],
        "current": data["current"],
        "vibration": data["vibration_rms"],
        "health": result["health_score"],
        "status": result["health_status"]
    }

    st.session_state.history.append(point)

    if len(st.session_state.history) > 60:
        st.session_state.history.pop(0)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "# 🛡️ EdgeGuard"
    )

    st.caption(
        "Predictive Maintenance & Fault Detection"
    )

    st.divider()

    st.markdown("### Operating Mode")

    mode = st.radio(
        "Data source",
        [
            "DEMO",
            "HARDWARE LIVE"
        ],
        index=0 if st.session_state.mode == "DEMO" else 1
    )

    st.session_state.mode = mode

    st.divider()

    if mode == "DEMO":

        st.success("🟢 SIMULATION ACTIVE")

        st.caption(
            "No hardware connected. "
            "Values are generated virtually."
        )

    else:

        st.info("🔵 HARDWARE LIVE")

        st.caption(
            "Reading ESP32 telemetry through "
            "the laptop data pipeline."
        )

    st.divider()

    st.markdown("### System")

    st.write("🟢 Dashboard Online")
    st.write("🤖 SVM Engine Ready")
    st.write("📡 Data Engine Ready")

    st.divider()

    st.caption(
        "EdgeGuard • Predict Today • Prevent Tomorrow"
    )


# ============================================================
# LIVE REFRESH
# ============================================================

st_autorefresh(
    interval=2000,
    key="edgeguard_refresh"
)


# ============================================================
# GET DATA
# ============================================================

data = get_data()

result = predict(data)

add_history(data, result)

temperature = data["temperature"]
current = data["current"]
vibration = data["vibration_rms"]

status = result["health_status"]
confidence = result["confidence"]
health = result["health_score"]


# ============================================================
# HEADER
# ============================================================

col1, col2 = st.columns([4, 1])

with col1:

    st.markdown(
        "# 🛡️ EdgeGuard Dashboard"
    )

    st.caption(
        "Real-time Monitoring  •  AI Powered  •  Predictive Maintenance"
    )

with col2:

    if st.session_state.mode == "DEMO":

        st.success(
            "🟢 SIMULATION MODE\n\nNo Hardware"
        )

    else:

        st.info(
            "🔵 HARDWARE LIVE"
        )


# ============================================================
# TOP METRICS
# ============================================================

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.metric(
        "🌡️ Temperature",
        f"{temperature:.1f} °C"
    )

with m2:
    st.metric(
        "⚡ Current",
        f"{current:.2f} A"
    )

with m3:
    st.metric(
        "〽️ Vibration RMS",
        f"{vibration:.2f} g"
    )

with m4:

    motor = "RUNNING" if data.get("motor_state", 1) else "STOPPED"

    st.metric(
        "⚙️ Motor",
        motor
    )

with m5:

    st.metric(
        "❤️ Health",
        f"{health:.0f}/100",
        status
    )


st.write("")


# ============================================================
# DEMO CONTROL PANEL
# ============================================================

if st.session_state.mode == "DEMO":

    st.markdown(
        "## 🎮 Demo Control Center"
    )

    st.caption(
        "Change the virtual machine condition and watch "
        "the AI response update automatically."
    )

    b1, b2, b3, b4, b5 = st.columns(5)

    if b1.button(
        "🟢 NORMAL",
        use_container_width=True
    ):
        st.session_state.scenario = "NORMAL"

    if b2.button(
        "🟡 WARNING",
        use_container_width=True
    ):
        st.session_state.scenario = "WARNING"

    if b3.button(
        "🔴 FAULT",
        use_container_width=True
    ):
        st.session_state.scenario = "FAULT"

    if b4.button(
        "🔥 OVERHEATING",
        use_container_width=True
    ):
        st.session_state.scenario = "OVERHEATING"

    if b5.button(
        "〽️ HIGH VIBRATION",
        use_container_width=True
    ):
        st.session_state.scenario = "HIGH VIBRATION"

    st.info(
        f"Current Scenario: **{st.session_state.scenario}**"
    )


# ============================================================
# MAIN VISUALS
# ============================================================

left, right = st.columns([2, 1])


with left:

    st.markdown(
        "## 📈 Live Sensor Telemetry"
    )

    history_df = pd.DataFrame(
        st.session_state.history
    )

    if not history_df.empty:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=history_df["time"],
                y=history_df["temperature"],
                name="Temperature °C",
                mode="lines+markers"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=history_df["time"],
                y=history_df["current"],
                name="Current A",
                mode="lines+markers"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=history_df["time"],
                y=history_df["vibration"],
                name="Vibration g",
                mode="lines+markers"
            )
        )

        fig.update_layout(
            height=430,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(3,12,28,0.7)",
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            legend=dict(
                orientation="h"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


with right:

    st.markdown(
        "## 🤖 Motor Health (SVM)"
    )

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=health,
            title={
                "text": status
            },
            gauge={
                "axis": {
                    "range": [0, 100]
                },
                "bar": {
                    "color": "#00e676"
                    if status == "NORMAL"
                    else "#ffd54f"
                    if status == "WARNING"
                    else "#ff5252"
                },
                "steps": [
                    {
                        "range": [0, 40],
                        "color": "#35151c"
                    },
                    {
                        "range": [40, 70],
                        "color": "#403819"
                    },
                    {
                        "range": [70, 100],
                        "color": "#123c2c"
                    }
                ]
            }
        )
    )

    gauge.update_layout(
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        font={
            "color": "white"
        }
    )

    st.plotly_chart(
        gauge,
        use_container_width=True
    )

    st.metric(
        "Classifier Confidence",
        f"{confidence:.1f}%"
    )


# ============================================================
# STATUS
# ============================================================

st.divider()

if status == "NORMAL":

    st.success(
        "🟢 NORMAL OPERATION — All monitored parameters are within the expected demo/model range."
    )

elif status == "WARNING":

    st.warning(
        "🟡 WARNING — Abnormal operating behavior detected."
    )

else:

    st.error(
        "🔴 FAULT DETECTED — Critical operating condition identified."
    )


# ============================================================
# TELEMETRY TABLE + ALERTS
# ============================================================

c1, c2 = st.columns(2)


with c1:

    st.markdown(
        "## 📡 Live Telemetry"
    )

    if not history_df.empty:

        display_df = history_df.tail(10).copy()

        display_df = display_df.rename(
            columns={
                "time": "Time",
                "temperature": "Temp °C",
                "current": "Current A",
                "vibration": "Vibration g",
                "health": "Health",
                "status": "Status"
            }
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


with c2:

    st.markdown(
        "## 🚨 Recent Events"
    )

    if status == "NORMAL":

        st.success(
            "Normal operation"
        )

        st.caption(
            "No critical abnormality detected."
        )

    elif status == "WARNING":

        st.warning(
            "Warning condition detected"
        )

        st.caption(
            "Monitor machine parameters."
        )

    else:

        st.error(
            "Fault condition detected"
        )

        st.caption(
            "Protective action should be considered."
        )

    st.write("")

    st.markdown("### Current Scenario")

    if st.session_state.mode == "DEMO":

        st.write(
            f"🎮 {st.session_state.scenario}"
        )

    else:

        st.write(
            "📡 ESP32 Hardware Telemetry"
        )


# ============================================================
# SYSTEM INFORMATION
# ============================================================

st.divider()

st.markdown(
    "## ⚙️ System Information"
)

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.write("**Data Source**")
    st.write(
        "Simulation"
        if st.session_state.mode == "DEMO"
        else "ESP32 Hardware"
    )

with s2:
    st.write("**AI Model**")
    st.write("SVM / RBF")

with s3:
    st.write("**Motor State**")
    st.write(
        "RUNNING"
        if data.get("motor_state", 1)
        else "STOPPED"
    )

with s4:
    st.write("**Last Update**")
    st.write(
        datetime.now().strftime("%H:%M:%S")
    )


st.caption(
    "EdgeGuard • Predict Today • Prevent Tomorrow"
)