import subprocess
import sys
from pathlib import Path

project_python = Path(__file__).resolve().parent / ".venv" / "Scripts" / "python.exe"
if project_python.is_file() and Path(sys.executable).resolve() != project_python.resolve():
    raise SystemExit(
        subprocess.call([str(project_python), str(Path(__file__).resolve())])
    )

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit.runtime.scriptrunner import get_script_run_ctx

if get_script_run_ctx(suppress_warning=True) is None:
    raise SystemExit(
        subprocess.call(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(Path(__file__).resolve()),
            ]
        )
    )

st.set_page_config(
    page_title="Smart Inventory Dashboard - HCI & Data Viz",
    page_icon="📦",
    layout="wide"
)

st.markdown("""
    <style>
    .main {
        background-color: #F8F9FA;
    }
    .stMetric {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    data = {
        "ID_Barang": ["BRG001", "BRG002", "BRG003", "BRG004", "BRG005", "BRG006", "BRG007", "BRG008"],
        "Nama_Barang": ["Laptop ASUS TUF", "Mouse Wireless", "Monitor 24 Inch", "Keyboard Mechanical", "SSD 1TB", "RAM 16GB", "Kabel HDMI", "Webcam HD"],
        "Kategori": ["Elektronik", "Aksesori", "Elektronik", "Aksesori", "Komponen", "Komponen", "Aksesori", "Aksesori"],
        "Stok_Tersedia": [15, 4, 8, 2, 25, 30, 5, 12],
        "Batas_Minimum": [5, 10, 5, 5, 8, 10, 10, 5],
        "Harga_Satuan": [12000000, 150000, 2100000, 450000, 1100000, 850000, 50000, 600000]
    }
    df = pd.DataFrame(data)
    # Atribut Pre-atentif: Deteksi Stok Kritis
    df['Status_Stok'] = df.apply(lambda row: 'Kritis (Perlu Restock)' if row['Stok_Tersedia'] <= row['Batas_Minimum'] else 'Aman', axis=1)
    return df

df = load_data()

st.title("📦 Smart Inventory Dashboard")
st.caption("Implementasi Prinsip HCI & Data Visualization (Mantra: Overview First, Zoom/Filter, Detail on Demand)")
st.markdown("---")

total_barang = len(df)
total_stok = df['Stok_Tersedia'].sum()
stok_kritis_count = len(df[df['Status_Stok'] == 'Kritis (Perlu Restock)'])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Jenis Barang", value=f"{total_barang} Item")
with col2:
    st.metric(label="Total Unit Stok", value=f"{total_stok} Unit")
with col3:
    st.metric(label="Barang Stok Kritis", value=f"{stok_kritis_count} Item", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

st.sidebar.header("🔍 Filter & Kontrol Interaktif")
selected_kategori = st.sidebar.multiselect(
    "Pilih Kategori Barang:",
    options=df["Kategori"].unique(),
    default=df["Kategori"].unique()
)

selected_status = st.sidebar.radio(
    "Filter Status Stok:",
    options=["Semua", "Kritis (Perlu Restock)", "Aman"]
)

filtered_df = df[df["Kategori"].isin(selected_kategori)]
if selected_status != "Semua":
    filtered_df = filtered_df[filtered_df["Status_Stok"] == selected_status]

st.subheader("📊 Visualisasi Stok Barang")

if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan filter terpilih.")
else:
    fig = px.bar(
        filtered_df,
        x="Nama_Barang",
        y="Stok_Tersedia",
        color="Status_Stok",
        color_discrete_map={
            "Aman": "#2ECC71",                    
            "Kritis (Perlu Restock)": "#E74C3C"    
        },
        labels={"Stok_Tersedia": "Jumlah Stok", "Nama_Barang": "Nama Barang"},
        title="Tingkat Stok Barang per Item",
        text_auto=True
    )

    fig.update_yaxes(range=[0, max(df['Stok_Tersedia']) + 5])
    fig.update_layout(
        template="plotly_white",
        font_family="Arial",
        legend_title_text="Status Stok",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, width="stretch")

with st.expander("📄 Tampilkan Rincian Detail Data Inventaris (Details on Demand)"):
    st.dataframe(
        filtered_df[["ID_Barang", "Nama_Barang", "Kategori", "Stok_Tersedia", "Batas_Minimum", "Harga_Satuan", "Status_Stok"]],
        width="stretch"
    )