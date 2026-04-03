import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os
import math

# ==========================================
# 1. KONFIGURASI HALAMAN (RESPONSIF)
# ==========================================
st.set_page_config(
    page_title="GIS UnenKU14", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. CSS CUSTOM (SOLUSI AGAR TIDAK TERPOTONG)
# ==========================================
st.markdown("""
    <style>
    /* Memberikan jarak atas 80px agar tidak tertutup jam/status bar HP */
    .main .block-container {
        padding-top: 80px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. RUMUS MATEMATIKA (HAVERSINE)
# ==========================================
def haversine(coord1, coord2):
    """Menghitung jarak presisi antara dua titik koordinat dalam meter"""
    try:
        R = 6371000 # Radius bumi dalam meter
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    except:
        return 0

def calculate_total_length(coords):
    if not coords or len(coords) < 2: return 0
    return sum(haversine(coords[i], coords[i+1]) for i in range(len(coords) - 1))
# ==========================================
# 4. FUNGSI LAPORAN PDF
# ==========================================
def create_pdf_report(nama, panjang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="LAPORAN INFRASTRUKTUR JALAN", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Nama Jalur: {nama}", ln=True)
    pdf.cell(200, 10, txt=f"Total Panjang: {panjang:.2f} Meter", ln=True)
    pdf.ln(20)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 10, txt="Dicetak melalui Aplikasi GIS UnenKU14", ln=True, align="R")
    return pdf.output(dest="S").encode("latin-1")
# ==========================================
# 4. SIDEBAR & INPUT
# ==========================================
with st.sidebar:
    st.header("⚙️ Pengaturan Data")
    nama_jalan_input = st.text_input("Nama Jalan:", "Jalur Jalan Utama")
    uploaded_file = st.file_uploader("Unggah GeoJSON Baru", type=["geojson", "json"])
    st.divider()

    st.subheader("📄 Laporan")
    # Tombol Download PDF
    st.sidebar("📄 Laporan")
    if st.button("Siapkan Laporan PDF"):
        # Muat data sementara untuk PDF
        temp_data = None
        if uploaded_file: temp_data = json.load(uploaded_file)
        elif os.path.exists("route.geojson"):
            with open("route.geojson", "r") as f: temp_data = json.load(f)
        
        if temp_data:
            p_coords = [[p[1], p[0]] for p in temp_data["geometry"]["coordinates"]]
            p_jarak = calculate_total_length(p_coords)
            pdf_bytes = create_pdf_report(nama_jalan_input, p_jarak)
            
        st.download_button(
            label="📥 Unduh PDF Sekarang",
            data=pdf_bytes,
            file_name=f"Laporan_{nama_jalan_input}.pdf",
            mime="application/pdf"
            )
        else:
            st.error("Data tidak ditemukan.")

# Tampilkan Judul dengan Class CSS yang sudah dibuat
st.markdown(f'<h3 class="judul-jalan">📍 {nama_jalan_input}</h3>', unsafe_allow_html=True)

# ==========================================
# 5. PEMROSESAN DATA
# ==========================================
data_json = None

# Cek file unggahan atau file default di server
try:
    if uploaded_file is not None:
        data_json = json.load(uploaded_file)
    elif os.path.exists("route.geojson"):
        with open("route.geojson", "r") as f:
            data_json = json.load(f)
except Exception as e:
    st.error(f"Gagal memuat data: {e}")

# ==========================================
# 6. VISUALISASI PETA
# ==========================================
if data_json:
    try:
        # Cek struktur GeoJSON
        if "geometry" in data_json and "coordinates" in data_json["geometry"]:
            raw_coords = data_json["geometry"]["coordinates"]
            # Balik [lon, lat] jadi [lat, lon] untuk Folium
            path = [[p[1], p[0]] for p in raw_coords]
            total_panjang = calculate_total_length(path)
            
            # Buat Objek Peta (Fokus ke titik pertama)
            m = folium.Map(location=path[0], zoom_start=18, control_scale=True)
            
            # Gambar Jalur (Hitam Putih agar 'Ngajaran'/Jelas)
            folium.PolyLine(path, color='#fbfcfa', weight=8, opacity=0.8).add_to(m)
            folium.PolyLine(path, color='#35d7f0', weight=6, opacity=1).add_to(m)

            # Floating Info Box (Versi HTML)
            info_html = f'''
                <div style="position: fixed; top: 150px; left: 20px; width: 160px; 
                background: white; border: 2px solid #000; z-index: 9999; 
                font-family: sans-serif; font-size: 12px; padding: 10px; border-radius: 10px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                <b>DATA INFRASTRUKTUR</b><br>
                Panjang: <b>{total_panjang:.2f} meter</b>
                </div>
            '''
            m.get_root().html.add_child(folium.Element(info_html))

            # Tampilkan Peta di Streamlit
            st_folium(m, use_container_width=True, height=400)
            
        else:
            st.warning("Format GeoJSON tidak dikenali. Pastikan ada bagian 'geometry' dan 'coordinates'.")
    except Exception as e:
        st.error(f"Kesalahan Visualisasi: {e}")
else:
    st.info("👋 Selamat Datang! Silakan unggah file 'route.geojson' melalui Sidebar untuk melihat peta.")
