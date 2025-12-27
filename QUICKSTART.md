# PANDUAN QUICK START - Zzzuper PDF Web Application

## 🚀 Cara Memulai (Langsung Buka!)

### Opsi 1: Menggunakan Batch File (Paling Mudah untuk Windows)
1. Double-click file `run.bat` di folder ZuperPDF
2. Tunggu hingga muncul pesan "Aplikasi dimulai di: http://localhost:5000"
3. Browser Anda akan otomatis membuka aplikasi (atau buka manual: http://localhost:5000)
4. Selesai!

### Opsi 2: Menggunakan PowerShell
1. Buka PowerShell
2. Navigasi ke folder ZuperPDF: `cd C:\Ardhi\Aplikasi\ZuperPDF`
3. Jalankan: `.\run.ps1`
4. Buka browser ke: http://localhost:5000

### Opsi 3: Manual dari Command Prompt/PowerShell
```bash
cd C:\Ardhi\Aplikasi\ZuperPDF
.\.venv\Scripts\activate
python app.py
```
Kemudian buka browser ke: http://localhost:5000

---

## ✅ Apa saja yang sudah dikonversi dari versi Tkinter?

### Fitur yang SUDAH TERSEDIA:
- ✅ Upload PDF dan Gambar
- ✅ Preview file (gambar dan PDF)
- ✅ Navigasi halaman PDF
- ✅ Rotasi preview (untuk testing orientasi)
- ✅ Atur urutan file (pindah ke atas/bawah)
- ✅ Hapus file individual
- ✅ Kosongkan semua file
- ✅ Gabung semua file menjadi PDF
- ✅ Download hasil gabung otomatis
- ✅ Deteksi barcode untuk nama file (optional)
- ✅ Responsive design (bisa diakses dari HP/Tablet)

### Fitur yang TIDAK TERSEDIA di versi 1.0:
- ⚠️ Atur PDF (move pages, insert, delete) - akan ditambah di update berikutnya
- ⚠️ Rename PDF berdasarkan barcode - akan ditambah di update berikutnya

---

## 📝 Instruksi Instalasi Detail

Jika Anda ingin setup manual:

### 1. Clone atau pergi ke folder aplikasi
```bash
cd C:\Ardhi\Aplikasi\ZuperPDF
```

### 2. Buat Virtual Environment (opsional tapi recommended)
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi
```bash
python app.py
```

---

## 🌐 Mengakses Aplikasi

Setelah aplikasi berjalan, buka salah satu URL berikut di browser:
- http://localhost:5000
- http://127.0.0.1:5000

---

## ⚠️ Troubleshooting

### Masalah: "Port 5000 sudah digunakan"
**Solusi:** 
1. Tutup aplikasi lain yang menggunakan port 5000
2. Atau ubah port di file `app.py` baris terakhir:
   ```python
   app.run(debug=True, host='127.0.0.1', port=5001)
   ```

### Masalah: "ModuleNotFoundError: No module named 'flask'"
**Solusi:**
```bash
pip install -r requirements.txt
```

### Masalah: Batch file tidak jalan
**Solusi:** 
1. Klik kanan `run.bat`
2. Pilih "Open with" → "Command Prompt"
3. Atau jalankan PowerShell script `run.ps1` sebaliknya

---

## 📱 Tips Penggunaan

1. **Multiple File Selection** - Saat upload, Anda bisa pilih banyak file sekaligus
2. **Preview dengan Zoom** - Scroll mouse pada area preview untuk zoom in/out
3. **Urutan Penting** - Pastikan urutan file sudah benar sebelum merge
4. **Orientasi** - Gunakan tombol rotasi preview untuk memastikan orientasi gambar sudah tepat
5. **Download Folder** - File hasil akan otomatis diunduh ke folder Downloads

---

## 🔧 Struktur Folder

```
C:\Ardhi\Aplikasi\ZuperPDF\
├── app.py                    # Main application
├── requirements.txt          # Dependencies list
├── run.bat                   # Quick start (Windows)
├── run.ps1                   # Quick start (PowerShell)
├── README.md                 # Full documentation
├── QUICKSTART.md            # File ini
├── .venv/                   # Virtual environment (auto-created)
├── templates/
│   └── index.html           # Web UI
├── static/
│   ├── style.css            # Styling
│   └── script.js            # JavaScript
└── uploads/                 # Temp folder (auto-created)
```

---

## 🎯 Next Steps

### Untuk Development:
1. Edit `static/script.js` atau `static/style.css` untuk custom UI
2. Edit `app.py` untuk menambah fitur
3. Aplikasi akan auto-reload saat ada perubahan file (karena debug mode)

### Untuk Production:
1. Set `debug=False` di `app.py`
2. Gunakan Gunicorn: `pip install gunicorn && gunicorn -w 4 app:app`
3. Deploy ke server (Heroku, AWS, DigitalOcean, etc)

---

## 📞 Support

Jika ada masalah:
1. Cek terminal/command prompt untuk error messages
2. Cek browser console (F12) untuk JavaScript errors
3. Pastikan Python versi 3.8+
4. Pastikan semua dependencies terinstall dengan benar

---

**Version 1.0 - Web Based Edition**
Dibuat dari konversi aplikasi Tkinter desktop ke Flask web app
Terakhir diupdate: Desember 2024
