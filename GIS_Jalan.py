import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os
import math

# ==========================================
# KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="GIS UnenKU14", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS untuk memastikan peta memenuhi layar HP dan menghilangkan error UI
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem; }
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI HITUNG JARAK ---
def haversine(coord1, coord2):
    try:
        R = 6371000 
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
    nama_jalan_input = st.text_input("Nama Jalan:", "Jalur Jalan Utama")
    uploaded_file = st.file_uploader("Unggah GeoJSON", type=["geojson", "json"])

st.markdown(f"### 📍 {nama_jalan_input}")

# --- PENANGANAN DATA (ANTISIPASI ERROR 500) ---
data_json = None

try:
    if uploaded_file is not None:
        data_json = json.load(uploaded_file)
    elif os.path.exists("route.geojson"):
        with open("route.geojson", "r") as f:
            data_json = json.load(f)
except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat file data: {e}")

# --- VISUALISASI ---
if data_json:
    try:
        # Validasi isi GeoJSON
        if "geometry" in data_json and "coordinates" in data_json["geometry"]:
            raw_coords = data_json["geometry"]["coordinates"]
            # Konversi format [lon, lat] ke [lat, lon]
            path = [[p[1], p[0]] for p in raw_coords]
            total_panjang = calculate_total_length(path)
            
            # Buat Peta
            m = folium.Map(location=path[0], zoom_start=18)
            folium.PolyLine(path, color='#000000', weight=12, opacity=1).add_to(m)
            folium.PolyLine(path, color='#FFFFFF', weight=6, opacity=1).add_to(m)

            # Legenda Floating
            legenda_html = f'''
                 <div style="position: fixed; bottom: 20px; left: 20px; width: 140px; 
                 background: white; border: 2px solid #333; z-index: 9999; 
                 font-size: 11px; padding: 8px; border-radius: 8px;">
                 <b>INFO PETA</b><br>
                 Panjang: {total_panjang:.1f}m
                 </div>
                 '''
            m.get_root().html.add_child(folium.Element(legenda_html))

            st_folium(m, use_container_width=True, height=500)
        else:
            st.warning("Data GeoJSON ditemukan, tapi format koordinat tidak sesuai.")
    except Exception as e:
        st.error(f"Gagal menampilkan peta: {e}")
else:
    st.warning("Belum ada data peta. Silakan unggah file route.geojson ke GitHub atau lewat sidebar.")
