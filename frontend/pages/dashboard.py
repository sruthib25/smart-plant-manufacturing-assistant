import streamlit as st
import time
import pandas as pd
from utils.api_client import get_sensor_data, trigger_fault

st.set_page_config(page_title="Plant Dashboard", layout="wide")

st.title("🏭 Smart Manufacturing Plant Dashboard")

# Fault Trigger Section
with st.expander("⚠️ Simulate Faults"):
    c1, c2, c3 = st.columns(3)
    with c1:
        machine = st.selectbox("Machine", ["CNC-204", "PRESS-505", "ROBOT-101"])
    with c2:
        fault = st.selectbox("Fault Type", ["overheat", "vibration", "pressure_loss"])
    with c3:
        if st.button("Trigger Fault", type="primary"):
            res = trigger_fault(machine, fault)
            st.warning(res)

# Auto-refresh loop
placeholder = st.empty()

while True:
    data = get_sensor_data()
    
    with placeholder.container():
        if not data:
            st.error("Cannot connect to backend. Is it running?")
        else:
            for machine_id, metrics in data.items():
                st.subheader(f"Machine: {machine_id}")
                
                # Dynamic Status Color
                status = metrics.get('status', 'Running')
                if status == 'Critical':
                    st.error(f"Status: {status}")
                elif status == 'Warning':
                    st.warning(f"Status: {status}")
                else:
                    st.success(f"Status: {status}")

                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Temperature", f"{metrics['temperature']:.1f} °C")
                k2.metric("Vibration", f"{metrics['vibration']:.2f} mm/s")
                k3.metric("RPM", f"{metrics['rpm']}")
                k4.metric("Pressure", f"{metrics['pressure']:.1f} bar")
                
                st.divider()
    
    time.sleep(2)
