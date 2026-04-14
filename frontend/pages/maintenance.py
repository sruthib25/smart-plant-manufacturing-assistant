import streamlit as st
import pandas as pd
from utils.api_client import get_inventory, trigger_scarcity_alert, analyze_log

st.set_page_config(page_title="Maintenance & Analysis", layout="wide")
st.title("🛠️ Maintenance & Analysis Hub")

tab1, tab2 = st.tabs(["Spare Parts & Maintenance", "CSV Log Analysis"])

with tab1:
    st.header("📦 Spare Parts Inventory")
    
    inventory = get_inventory()
    
    if inventory:
        # Convert to DataFrame for better display
        df = pd.DataFrame(inventory)
        
        # Display as a table with actions
        # Streamlit dataframe doesn't support buttons inside easily, so we iterate
        for index, row in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 2])
            with col1:
                st.write(f"**{row['machine_id']}**")
            with col2:
                st.write(row['name'])
            with col3:
                st.write(f"Stock: {row['stock']}")
            with col4:
                st.write(f"Min: {row['min_stock']}")
            with col5:
                if row['stock'] <= row['min_stock']:
                    st.error("Low Stock!")
                
                if st.button(f"Report Scarcity", key=f"btn_{row['id']}"):
                    if trigger_scarcity_alert(row['machine_id'], row['name']):
                        st.success(f"Alert sent to management for {row['name']}!")
                    else:
                        st.error("Failed to send alert.")
            st.divider()
    else:
        st.info("No inventory data available.")

with tab2:
    st.header("📊 Machine Log Analysis")
    
    uploaded_file = st.file_uploader("Upload Machine Log (CSV)", type="csv")
    
    if uploaded_file is not None:
        # Read locally for visualization
        try:
            # We need to reset the pointer for the backend call or read bytes once
            bytes_data = uploaded_file.getvalue()
            
            # Authorization check or just display
            df_viz = pd.read_csv(uploaded_file)
            st.subheader("Data Preview")
            st.dataframe(df_viz.head())
            
            st.subheader("Performance Visualization")
            # Attempt to find numeric columns
            numeric_cols = df_viz.select_dtypes(include=['float', 'int']).columns
            
            if 'temperature_c' in numeric_cols:
                st.write("### Temperature (°C)")
                st.line_chart(df_viz[['temperature_c']], color="#FF4B4B")
            
            if 'pressure_psi' in numeric_cols:
                st.write("### Pressure (PSI)")
                st.line_chart(df_viz[['pressure_psi']], color="#4B90FF")
                
            if 'vibration_mm_s' in numeric_cols:
                st.write("### Vibration (mm/s)")
                st.line_chart(df_viz[['vibration_mm_s']], color="#FFAA00")
                
            other_cols = [c for c in numeric_cols if c not in ['temperature_c', 'pressure_psi', 'vibration_mm_s']]
            if other_cols:
                st.write("### Other Metrics")
                st.line_chart(df_viz[other_cols])
            
            if st.button("Analyze with AI"):
                with st.spinner("AI is analyzing the log..."):
                    result = analyze_log(bytes_data)
                    
                    if result:
                        st.success("Analysis Complete")
                        st.divider()
                        st.markdown("### 🤖 AI Performance Report")
                        st.markdown(result.get("report", "No report generated."))
                        
                        with st.expander("View Statistical Details"):
                            st.json(result.get("stats", {}))
                    else:
                        st.error("Analysis failed. Ensure backend is running.")
        except Exception as e:
            st.error(f"Error reading file: {e}")
