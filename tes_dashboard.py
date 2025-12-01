import streamlit as st
import pandas as pd
import plotly.express as px

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="PROFIL KEPENDUDUKAN & LAYANAN SIPIL KOTA BOGOR", layout="wide", page_icon="🏛️")

# CSS AGAR TAMPILAN MIRIP GAMBAR AI (BIRU EMAS)
#st.markdown("""
#<style>
 #   .stApp { background-color: #F8F9FA; }
  #  div[data-testid="metric-container"] {
   #     background-color: #FFFFFF;
    #    border: 1px solid #D4AF37;
     #   padding: 15px;
      #  border-radius: 10px;
       # border-top: 5px solid #002B5B;
       # box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
   # }
    #div[data-testid="metric-container"] label { color: #555; font-weight: bold; }
    #div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    #    color: #002B5B; font-size: 28px; font-weight: bold;
    #}
    #section[data-testid="stSidebar"] { background-color: #002B5B; }
    #section[data-testid="stSidebar"] h1, p, label, .stSelectbox label { color: white !important; }
#</style>
#""", unsafe_allow_html=True)

# --- CSS SUPER FIX (PAKSA WARNA) ---
st.markdown("""
<style>
    /* 1. GLOBAL: Paksa background putih & tulisan hitam untuk seluruh aplikasi */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* 2. PAKSA SEMUA TEKS UTAMA JADI HITAM */
    /* Kita targetkan elemen spesifik di area konten utama */
    div.block-container h1, 
    div.block-container h2, 
    div.block-container h3, 
    div.block-container p, 
    div.block-container span, 
    div.block-container label,
    div.block-container div {
        color: #000000 !important;
    }

    /* 3. PERBAIKI KARTU KPI (KOTAK ANGKA) */
    div[data-testid="metric-container"] {
        background-color: #F8F9FA !important;
        border: 1px solid #D4AF37;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #002B5B;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    /* Judul di dalam kartu (misal: Total Populasi) */
    div[data-testid="metric-container"] label {
        color: #333333 !important; /* Abu gelap */
    }
    /* Angka di dalam kartu */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #002B5B !important; /* Biru Tua */
    }
    
    /* 4. KHUSUS SIDEBAR (MENU KIRI) - KEMBALIKAN KE PUTIH */
    section[data-testid="stSidebar"] {
        background-color: #002B5B !important; /* Background Biru */
    }
    /* Paksa semua teks di sidebar jadi PUTIH */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #FFFFFF !important;
    }
    
    /* Pengecualian: Teks di dalam kotak pilihan (Dropdown) harus hitam biar kebaca */
    .stSelectbox div[data-baseweb="select"] div {
        color: #000000 !important;
    }
    
    /* Hilangkan padding atas berlebih */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# 2. LOAD DATA
try:
    file_excel = "MASTER_DATA_DASHBOARD.xlsx"
    # Gunakan try-except per sheet agar kalau satu hilang, yang lain tetap jalan
    xls = pd.ExcelFile(file_excel)
    
    df_penduduk = pd.read_excel(xls, "PENDUDUK") if "PENDUDUK" in xls.sheet_names else pd.DataFrame()
    df_ekonomi = pd.read_excel(xls, "PENGANGGURAN") if "PENGANGGURAN" in xls.sheet_names else pd.DataFrame()
    df_sosial = pd.read_excel(xls, "DISABILITAS") if "DISABILITAS" in xls.sheet_names else pd.DataFrame()
    df_akta = pd.read_excel(xls, "AKTA") if "AKTA" in xls.sheet_names else pd.DataFrame()
    df_agama = pd.read_excel(xls, "AGAMA") if "AGAMA" in xls.sheet_names else pd.DataFrame() # Tambah Agama

except Exception as e:
    st.error(f"Gagal membaca file Excel: {e}")
    st.stop()

# --- FUNGSI BERSIHKAN KOLOM ---
def bersihkan_kolom(df):
    if df.empty: return df
    # Paksa jadi string dan uppercase
    df.columns = df.columns.astype(str).str.strip().str.upper()
    
    # Cari kolom wilayah/kecamatan
    for col in df.columns:
        if "WILAYAH" in col or "KECAMATAN" in col:
            df = df.rename(columns={col: "WILAYAH"})
    return df

df_penduduk = bersihkan_kolom(df_penduduk)
df_ekonomi = bersihkan_kolom(df_ekonomi)
df_sosial = bersihkan_kolom(df_sosial)
df_akta = bersihkan_kolom(df_akta)
df_agama = bersihkan_kolom(df_agama)

# CEK ERROR JIKA WILAYAH TIDAK ADA
if not df_penduduk.empty and "WILAYAH" not in df_penduduk.columns:
    st.error("Kolom 'WILAYAH' tidak ditemukan di data Penduduk.")
    st.stop()

# 3. SIDEBAR FILTER
st.sidebar.title("FILTER DATA")
if not df_penduduk.empty:
    list_wilayah = sorted(df_penduduk["WILAYAH"].astype(str).unique())
    pilihan_wilayah = st.sidebar.selectbox("Pilih Wilayah:", ["Semua Wilayah"] + list_wilayah)
else:
    pilihan_wilayah = "Semua Wilayah"

st.sidebar.markdown("---")
st.sidebar.info("Dashboard Monitoring Data Agregat Disdukcapil")

# Fungsi filter helper
def filter_wilayah(df, wilayah):
    if df.empty or wilayah == "Semua Wilayah": return df
    if "WILAYAH" in df.columns:
        return df[df["WILAYAH"] == wilayah]
    return df

df_penduduk = filter_wilayah(df_penduduk, pilihan_wilayah)
df_ekonomi = filter_wilayah(df_ekonomi, pilihan_wilayah)
df_sosial = filter_wilayah(df_sosial, pilihan_wilayah)
df_akta = filter_wilayah(df_akta, pilihan_wilayah)
df_agama = filter_wilayah(df_agama, pilihan_wilayah)

# 4. HEADER
c_logo, c_judul = st.columns([1, 6])
with c_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e2/Logo_Kota_Bogor.svg", width=80)
with c_judul:
    st.title("Laporan Eksekutif Kota Bogor")
    st.markdown("**Analisis Strategis Demografi & Kesejahteraan Sosial**")

st.markdown("---")

# --- HITUNG TOTAL (DENGAN AUTO DETECT KOLOM) ---
def cari_kolom_jumlah(df, keywords=["JML", "TOTAL", "JUMLAH", "L+P"]):
    if df.empty: return []
    # Cari kolom yang mengandung salah satu kata kunci
    for key in keywords:
        candidates = [c for c in df.columns if key in c and "NO" not in c and "WILAYAH" not in c]
        if candidates:
            return candidates
    return []

# 1. POPULASI
cols_pop = cari_kolom_jumlah(df_penduduk, ["JML", "TOTAL", "JUMLAH", "PENDUDUK", "L+P"])
total_populasi = 0
if cols_pop:
    col_pop_fix = cols_pop[-1] 
    total_populasi = pd.to_numeric(df_penduduk[col_pop_fix], errors='coerce').fillna(0).sum()

# 2. PENGANGGURAN
cols_nganggur = cari_kolom_jumlah(df_ekonomi, ["TDK_BEKERJA", "PENGANGGURAN"])
total_nganggur = 0
if cols_nganggur:
    col_nganggur_fix = cols_nganggur[0]
    total_nganggur = pd.to_numeric(df_ekonomi[col_nganggur_fix], errors='coerce').fillna(0).sum()

# 3. DISABILITAS
total_disabilitas = 0
if not df_sosial.empty:
    if "TOTAL" in df_sosial.columns:
         total_disabilitas = pd.to_numeric(df_sosial["TOTAL"], errors='coerce').sum()
    else:
         for c in df_sosial.columns:
             if ("JML" in c or "TOTAL" in c) and "WILAYAH" not in c and "NO" not in c:
                 total_disabilitas += pd.to_numeric(df_sosial[c], errors='coerce').fillna(0).sum()

# 4. AKTA
cols_akta = cari_kolom_jumlah(df_akta, ["BLM", "BELUM"])
total_no_akta = 0
if cols_akta:
    col_akta_fix = cols_akta[0]
    total_no_akta = pd.to_numeric(df_akta[col_akta_fix], errors='coerce').fillna(0).sum()

# TAMPILKAN SCORECARD
c1, c2, c3, c4 = st.columns(4)
c1.metric("TOTAL POPULASI", f"{total_populasi:,.0f}")
c2.metric("PENGANGGURAN", f"{total_nganggur:,.0f}")
c3.metric("DISABILITAS", f"{total_disabilitas:,.0f}")
c4.metric("BELUM PUNYA AKTA", f"{total_no_akta:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# 5. GRAFIK UTAMA (BAR CHART)
st.subheader("PERINGKAT POPULASI PER WILAYAH")

if cols_pop:
    col_target = cols_pop[-1]
    df_grafik = df_penduduk.groupby("WILAYAH")[col_target].sum().reset_index()
    df_grafik = df_grafik.sort_values(by=col_target, ascending=True)

    fig = px.bar(df_grafik, x=col_target, y="WILAYAH", orientation='h', text=col_target,
                 color=col_target, color_continuous_scale=["#002B5B", "#D4AF37"])
    fig.update_layout(xaxis_title="", yaxis_title="", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Data populasi tidak tersedia.")

# 6. GRAFIK BAWAH (3 KOLOM: DISABILITAS, AGAMA, PEKERJAAN)
c_bawah1, c_bawah2, c_bawah3 = st.columns(3)

with c_bawah1:
    st.subheader("JENIS DISABILITAS")
    if not df_sosial.empty:
        jenis = []
        jumlah = []
        for c in df_sosial.columns:
            if ("JML" in c or "TOTAL" in c) and "WILAYAH" not in c and "NO" not in c:
                nama = c.replace("DISABILITAS", "").replace("_JML", "").replace("JML", "").strip()
                val = pd.to_numeric(df_sosial[c], errors='coerce').sum()
                if val > 0:
                    jenis.append(nama)
                    jumlah.append(val)
        
        if len(jenis) > 0:
            fig_d = px.pie(values=jumlah, names=jenis, hole=0.5, color_discrete_sequence=px.colors.sequential.Cividis)
            st.plotly_chart(fig_d, use_container_width=True)
        else:
            st.info("Data detail kosong.")
    else:
        st.info("File Disabilitas belum ada.")

with c_bawah2:
    st.subheader("KOMPOSISI AGAMA")
    if not df_agama.empty:
        agm_jenis = []
        agm_jumlah = []
        # Cari kolom agama (ISLAM, KRISTEN, dll) yang ada angka JML nya
        for c in df_agama.columns:
            # Kata kunci agama umum
            keywords_agama = ["ISLAM", "KRISTEN", "KATHOLIK", "HINDU", "BUDHA", "KHONGHUCU", "KEPERCAYAAN"]
            # Cek jika kolom mengandung nama agama DAN (mengandung JML atau tidak ada L/P nya)
            if any(k in c for k in keywords_agama) and "WILAYAH" not in c:
                # Ambil yang JML saja biar gak double hitung L/P
                if "JML" in c or "TOTAL" in c: 
                    val = pd.to_numeric(df_agama[c], errors='coerce').sum()
                    if val > 0:
                        nama_bersih = c.replace("_JML", "").replace("JML", "").strip()
                        agm_jenis.append(nama_bersih)
                        agm_jumlah.append(val)
        
        if len(agm_jenis) > 0:
            fig_agm = px.pie(values=agm_jumlah, names=agm_jenis, hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
            fig_agm.update_traces(textposition='inside', textinfo='percent+label')
            fig_agm.update_layout(showlegend=False)
            st.plotly_chart(fig_agm, use_container_width=True)
        else:
            st.info("Kolom data agama tidak terdeteksi (Pastikan ada 'JML').")
    else:
        st.info("File Agama belum dimuat di olah_data.")

with c_bawah3:
    st.subheader("STATUS PEKERJAAN")
    if not df_ekonomi.empty:
        cols_kerja = cari_kolom_jumlah(df_ekonomi, ["BEKERJA", "SUDAH BEKERJA"])
        cols_kerja = [c for c in cols_kerja if "TDK" not in c]
        
        if cols_kerja:
            jml_kerja = pd.to_numeric(df_ekonomi[cols_kerja[0]], errors='coerce').sum()
            jml_nganggur = total_nganggur
            fig_k = px.pie(values=[jml_kerja, jml_nganggur], names=["Bekerja", "Tidak Bekerja"], 
                           hole=0.5, color_discrete_sequence=["#002B5B", "#D4AF37"])
            st.plotly_chart(fig_k, use_container_width=True)
        else:
            st.info("Data detail pekerjaan kosong.")
    else:
        st.info("File Ekonomi belum ada.")