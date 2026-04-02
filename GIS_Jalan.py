import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os
import math

# ==========================================
# KONFIGURASI HALAMAN STREAMLIT
# ==========================================
# Konfigurasi ini sangat krusial agar aplikasi Android tidak terpotong
st.set_page_config(
    page_title="GIS UnenKU14", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Custom untuk memaksimalkan layar HP
st.markdown("""
    <style>
    /* Menghilangkan padding utama Streamlit */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    /* Memastikan iframe peta penuh */
    iframe {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI HITUNG JARAK (HAVERSINE) ---
def haversine(coord1, coord2):
    try:
        R = 6371000 # Radius bumi dalam meter
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    except:
        return 0

def calculate_total_length(coords):
    if not coords or len(coords) < 2: return 0
    return sum(haversine(coords[i], coords[i+1]) for i in range(len(coords) - 1))

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Kontrol Data")
    nama_jalan_input = st.text_input("Masukkan Nama Jalan:", "Jalur Jalan Utama")
    uploaded_file = st.file_uploader("Unggah GeoJSON", type=["geojson", "json"])
    st.info("Gunakan sidebar ini untuk mengubah data atau nama jalan secara langsung.")

# Judul di Aplikasi
st.markdown(f"### 📍 {nama_jalan_input}")

# --- PEMBACAAN DATA ---
data_json = None
if uploaded_file:
    data_json = json.load(uploaded_file)
elif os.path.exists("route.geojson"):
    with open("route.geojson", "r") as f:
        data_json = json.load(f)

# --- VISUALISASI ---
if data_json:
    try:
        raw_coords = data_json["geometry"]["coordinates"]
        path = [[p[1], p[0]] for p in raw_coords]
        total_panjang = calculate_total_length(path)
        
        # Buat objek peta dasar
        m = folium.Map(location=path[0], zoom_start=18, control_scale=True)
        
        # Visualisasi Jalan (Gaya Modern)
        folium.PolyLine(path, color='#000000', weight=12, opacity=1).add_to(m)
        folium.PolyLine(path, color='#FFFFFF', weight=6, opacity=1).add_to(m)

        # Legenda yang dioptimalkan untuk layar Android
        legenda_html = f'''
             <div style="
                 position: fixed; 
                 bottom: 20px; left: 20px; width: 160px;
                 background-color: rgba(255, 255, 255, 0.9); 
                 border: 2px solid #555; 
                 z-index: 9999; 
                 font-size: 11px;
                 border-radius: 10px; 
                 padding: 10px;
                 box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
                 font-family: Arial, sans-serif;
             ">
             <b style="font-size: 12px; display: block; margin-bottom: 5px; text-align: center;">INFO PETA</b>
             <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 20px; height: 6px; background: white; border: 1px solid black; margin-right: 10px;"></div>
                <span>Jalan: <b>{total_panjang:.1f} m</b></span>
             </div>
             <div style="display: flex; align-items: center;">
                <div style="width: 12px; height: 12px; background: red; margin-right: 18px; border-radius: 2px;"></div>
                <span>Bangunan/Rumah</span>
             </div>
             </div>
             '''
        m.get_root().html.add_child(folium.Element(legenda_html))

        # Menampilkan peta dengan lebar otomatis (container width)
        st_folium(m, use_container_width=True, height=500)
        
    except Exception as e:
        st.error(f"Gagal memproses data: {e}")
else:
    st.warning("Menunggu data... Silakan unggah file GeoJSON melalui menu di samping kiri.")