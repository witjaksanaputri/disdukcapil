import pandas as pd
import glob
import os

# --- PASTE ALAMAT FOLDER ANDA DI BAWAH INI (JANGAN LUPA HURUF r) ---
folder_path = r"D:\MAGANG DISDUKCAPIL" 
# -------------------------------------------------------------------

print(f"📂 Mencoba membuka folder: {folder_path}")

# Cek apakah foldernya beneran ada?
if not os.path.exists(folder_path):
    print("❌ ERROR: Folder tidak ditemukan!")
    print("Saran: Coba copy ulang alamat folder dari File Explorer.")
else:
    print("✅ Folder ditemukan! Mencari file Excel...")
    
    # Gabungkan alamat folder dengan pola *.xlsx
    pola_file = os.path.join(folder_path, "*.xlsx")
    files = glob.glob(pola_file)
    
    if not files:
        print("❌ ERROR: Folder ketemu, TAPI isinya kosong (tidak ada file .xlsx)!")
        print("Saran: Pastikan file excelnya berekstensi .xlsx bukan .xls")
    else:
        print(f"✅ Ditemukan {len(files)} file Excel. Membaca Header...\n")
        
        # Mulai baca header
        sudah_dicek = []
        for file in files:
            try:
                nama_file = os.path.basename(file)
                kategori = "_".join(nama_file.split("_")[:2])
                
                if kategori not in sudah_dicek:
                    # Baca header
                    df = pd.read_excel(file, nrows=0) 
                    print(f"🔹 TIPE: {kategori}")
                    print(f"   KOLOM: {df.columns.tolist()}")
                    print("-" * 30)
                    sudah_dicek.append(kategori)
            except Exception as e:
                print(f"⚠️ Gagal baca {nama_file}: {e}")

        print("\n🏁 Selesai.")