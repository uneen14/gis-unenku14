import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os
import math

# ==========================================
# KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(page_title="GIS UnenKU14", layout="wide")

# --- FUNGSI HITUNG JARAK (HAVERSINE) ---
def haversine(coord1, coord2):
    # Radius bumi dalam meter
    R = 6371000
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_total_length(coords):
    total_dist = 0
    for i in range(len(coords) - 1):
        total_dist += haversine(coords[i], coords[i+1])
    return total_dist

# --- SIDEBAR UNTUK INPUT DATA ---
with st.sidebar:
    st.header("⚙️ Kontrol Data")
    
    # 1. Input Nama Jalan
    nama_jalan_input = st.text_input("Masukkan Nama Jalan:", "Jalur Jalan Utama")
    
    # 2. Upload File GeoJSON
    uploaded_file = st.file_uploader("Unggah File GeoJSON (route.geojson)", type=["geojson", "json"])
    
    st.info("Gunakan sidebar ini untuk memperbarui data peta secara dinamis.")

# Judul Utama Berdasarkan Input
st.title(f"📍 Nama Jalan : {nama_jalan_input}")

# ==========================================
# 1. LOGIKA PEMBACAAN DATA
# ==========================================
data_json = None
sumber_data = ""

if uploaded_file is not None:
    data_json = json.load(uploaded_file)
    sumber_data = "File Upload"
    st.sidebar.success("File berhasil diunggah!")
elif os.path.exists("route.geojson"):
    with open("route.geojson", "r") as f:
        data_json = json.load(f)
    sumber_data = "route.geojson (Lokal)"

# ==========================================
# 2. VISUALISASI PETA (Jika data tersedia)
# ==========================================
if data_json:
    try:
        # Ekstraksi Koordinat
        raw_coords = data_json["geometry"]["coordinates"]
        path = [[p[1], p[0]] for p in raw_coords]
        
        # Hitung Panjang Jalan
        total_panjang = calculate_total_length(path)
        
        # Penentuan Center Peta
        start_lat, start_lon = path[0][0], path[0][1]
        
        m = folium.Map(location=[start_lat, start_lon], zoom_start=18, tiles='OpenStreetMap')

        # --- STYLE JALAN GAYA ATLAS (Ukuran Diperbesar) ---
        folium.PolyLine(path, color='#000000', weight=14, opacity=1, name="Outline").add_to(m)
        folium.PolyLine(path, color='#07c1f0', weight=8, opacity=1, name="Isi Jalan").add_to(m)

        # --- FASILITAS RUMAH ---
        rumah_coords = [[[-7.65365, 108.58760], [-7.65365, 108.58765], [-7.65370, 108.58765], [-7.65370, 108.58760]]]
        for r in rumah_coords:
            folium.Polygon(r, color='red', fill=True, fill_color='red', fill_opacity=0.7, weight=1, tooltip="Bangunan Rumah").add_to(m)

        # --- FASILITAS JEMBATAN ---
        folium.Marker([-7.6568, 108.5867], icon=folium.Icon(color='black', icon='archway', prefix='fa'), tooltip="Jembatan").add_to(m)

        # ==========================================
        # 3. LEGENDA MINIMALIS (Ditambah Info Panjang Jalan)
        # ==========================================
        legenda_html = f'''
             <div style="
             position: fixed; 
             top: 20px; right: 20px; width: 220px;
             background-color: white; 
             border: 2px solid #333; 
             z-index: 9999; 
             font-size: 13px;
             font-family: 'Segoe UI', sans-serif;
             border-radius: 10px; 
             padding: 15px;
             box-shadow: 0 4px 15px rgba(0,0,0,0.2);
             color: #333;
             ">
             <div style="font-weight: bold; margin-bottom: 12px; border-bottom: 1px solid #ddd; padding-bottom: 8px; text-align: center;">
                Legenda Peta
             </div>
             
             <!-- Item Jalan -->
             <div style="display: flex; flex-direction: column; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="min-width: 30px; display: flex; justify-content: center; margin-right: 12px;">
                        <div style="width: 25px; height: 10px; background: white; border: 2px solid black;"></div>
                    </div>
                    <span style="font-weight: 600;">{nama_jalan_input}</span>
                </div>
                <div style="margin-left: 42px; font-size: 11px; color: #666;">
                    📏 Panjang: <b>{total_panjang:.1f} meter</b>
                </div>
             </div>
             
             <!-- Item Rumah -->
             <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="min-width: 30px; display: flex; justify-content: center; margin-right: 12px;">
                    <div style="width: 16px; height: 16px; background: red; border: 1px solid #b20000; border-radius: 2px;"></div>
                </div>
                <span style="font-weight: 600;">Rumah</span>
             </div>
             
             <!-- Item Jembatan -->
             <div style="display: flex; align-items: center;">
                <div style="min-width: 30px; display: flex; justify-content: center; margin-right: 12px; font-size: 18px;">
                    🌉
                </div>
                <span style="font-weight: 600;">Jembatan</span>
             </div>
             </div>
             '''
        m.get_root().html.add_child(folium.Element(legenda_html))

        # ==========================================
        # 4. TAMPILKAN DI STREAMLIT
        # ==========================================
        st_folium(m, width=1100, height=600)
        st.success(f"Berhasil! Data jalan dibaca dari: {sumber_data}")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data: {e}")

else:
    st.warning("Silakan unggah file GeoJSON di sidebar.")