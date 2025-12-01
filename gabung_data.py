import pandas as pd
import glob
import os

# --- KONFIGURASI ---
folder_laptop = r"D:\MAGANG DISDUKCAPIL"
nama_file_hasil = "MASTER_DATA_DASHBOARD.xlsx"

# DAFTAR TARGET LENGKAP (SUDAH ADA AGAMA)
daftar_target = {
    "PENDUDUK": "JUMDUK JK",       
    "PENGANGGURAN": "AGR_ANGKA",   
    "DISABILITAS": "AGR_DISABILITAS", 
    "AKTA": "AGR_AKTA",
    "AGAMA": "AGR_AGAMA"  # <--- INI YANG TADI KURANG
}

print(f"🚀 Memulai perbaikan data di: {folder_laptop}")
data_terkumpul = {}

# --- FUNGSI PENCARI HEADER OTOMATIS ---
def cari_baris_header(file_path):
    try:
        df_intip = pd.read_excel(file_path, header=None, nrows=15)
        for i, row in df_intip.iterrows():
            baris_teks = row.astype(str).str.upper().tolist()
            if any("WILAYAH" in x or "KECAMATAN" in x for x in baris_teks):
                return i 
    except:
        pass
    return 0 

# --- PROSES UTAMA ---
for nama_sheet, kata_kunci in daftar_target.items():
    print(f"\n🔎 Mencari file topik: {nama_sheet} ...")
    pola = os.path.join(folder_laptop, f"*{kata_kunci}*.xlsx")
    files = glob.glob(pola)
    
    if not files:
        print(f"❌ Gagal: File '{kata_kunci}' tidak ditemukan.")
    else:
        file_excel = sorted(files, key=len)[0]
        try:
            posisi_header = cari_baris_header(file_excel)
            print(f"   📍 Header ditemukan di baris ke: {posisi_header + 1}")
            
            df = pd.read_excel(file_excel, header=posisi_header)
            df.columns = df.columns.astype(str).str.strip().str.upper()
            
            for col in df.columns:
                if "WILAYAH" in col or "KECAMATAN" in col:
                    df = df.rename(columns={col: "WILAYAH"})
            
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
            if "WILAYAH" in df.columns:
                data_terkumpul[nama_sheet] = df
                print(f"   ✅ Sukses! Data rapi ({len(df)} baris).")
            else:
                print("   ⚠️ Peringatan: Kolom WILAYAH tidak ketemu.")
                
        except Exception as e:
            print(f"   ⚠️ Error: {e}")

# --- SIMPAN ---
if data_terkumpul:
    print(f"\n💾 Menyimpan perbaikan ke: {nama_file_hasil}...")
    try:
        with pd.ExcelWriter(nama_file_hasil) as writer:
            for nama, df in data_terkumpul.items():
                df.to_excel(writer, sheet_name=nama, index=False)
        print("🎉 SELESAI! File Master sudah diperbarui (termasuk Data AGAMA).")
    except Exception as e:
        print(f"❌ Gagal simpan: {e}. Tutup dulu file Excelnya!")
else:
    print("❌ Tidak ada data yang berhasil diproses.")