import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

st.set_page_config(page_title="MSFT HPC Support Tool", layout="wide")

def parse_gpu_xml(content):
    try:
        # Extract only the XML portion between markers
        xml_str = content.split("=== START NVIDIA-SMI XML ===")[1].split("=== END NVIDIA-SMI XML ===")[0]
        root = ET.fromstring(xml_str.strip())
        
        gpu_data = []
        driver = root.find('driver_version').text
        
        for gpu in root.findall('gpu'):
            gpu_id = gpu.find('minor_number').text
            temp = gpu.find('temperature/gpu_temp').text.replace('C', '')
            mem = gpu.find('fb_memory_usage/total').text
            vbios = gpu.find('vbios_version').text
            
            # Check for XID errors in the DMESG section of the same file
            has_xid = "XID" in content
            
            gpu_data.append({
                "ID": gpu_id, 
                "Temp": int(temp), 
                "Driver": driver, 
                "VBIOS": vbios, 
                "Memory": mem,
                "XID_Detected": has_xid
            })
        return pd.DataFrame(gpu_data)
    except Exception as e:
        st.error(f"Error parsing log: {e}")
        return None

st.title("🔎 Azure HPC & AI Health Validator")
st.markdown("Compare a **Suspect Node** against a **Golden Node** configuration.")

col1, col2 = st.columns(2)

with col1:
    bad_file = st.file_uploader("Upload 'Suspect' Log", type=["log", "txt"])
with col2:
    gold_file = st.file_uploader("Upload 'Golden' Log (Optional)", type=["log", "txt"])

if bad_file:
    bad_df = parse_gpu_xml(bad_file.getvalue().decode("utf-8"))
    
    if bad_df is not None:
        st.subheader("Suspect Node Status")
        # Visual Indicators
        metrics = st.columns(len(bad_df))
        for i, row in bad_df.iterrows():
            status = "🔴" if row['Temp'] > 80 or row['XID_Detected'] else "🟢"
            metrics[i].metric(label=f"GPU {row['ID']}", value=f"{row['Temp']}°C", delta=status)

        # Comparison Logic
        if gold_file:
            gold_df = parse_gpu_xml(gold_file.getvalue().decode("utf-8"))
            if gold_df is not None:
                st.divider()
                st.subheader("🛠️ Drift Analysis")
                
                # Check Driver Mismatch
                if bad_df['Driver'].iloc[0] != gold_df['Driver'].iloc[0]:
                    st.error(f"DRIVER MISMATCH: Suspect({bad_df['Driver'].iloc[0]}) vs Golden({gold_df['Driver'].iloc[0]})")
                else:
                    st.success("Driver versions match.")

                # Check VBIOS Mismatch
                mismatched_vbios = bad_df[bad_df['VBIOS'] != gold_df['VBIOS']]
                if not mismatched_vbios.empty:
                    st.warning("VBIOS inconsistencies detected across GPUs!")
                    st.write(bad_df[['ID', 'VBIOS']])