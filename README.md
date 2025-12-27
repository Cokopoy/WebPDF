# Zzzuper PDF - Web Application

Aplikasi web untuk menggabung gambar dan PDF menjadi file PDF yang rapi.

## Fitur Utama

- ✅ **Upload PDF dan Gambar** - Dukungan untuk file PDF, JPG, JPEG, dan PNG
- ✅ **Preview File** - Lihat preview file sebelum digabung
- ✅ **Rotasi Preview** - Putar gambar untuk menyesuaikan orientasi
- ✅ **Atur Urutan** - Pindahkan file ke atas atau ke bawah
- ✅ **Gabung Otomatis** - Gabungkan semua file menjadi satu PDF
- ✅ **Download Hasil** - Download PDF hasil gabung langsung ke komputer
- ✅ **Deteksi Barcode** - Gunakan barcode sebagai nama file otomatis (optional)

## Sistem Requirement

- Python 3.8 atau lebih tinggi
- pip (Package manager Python)

## Instalasi dan Setup

### 1. Clone atau Download Repository
```bash
cd C:\Ardhi\Aplikasi\ZuperPDF
```

### 2. Buat Virtual Environment (Recommended)
```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Di Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Catatan:** Jika ada error pada library pyzbar, Anda bisa skip installasinya dulu:
```bash
pip install -r requirements.txt --ignore-installed pyzbar
```

Library pyzbar diperlukan untuk deteksi barcode otomatis, jika tidak diperlukan dapat diabaikan.

### 4. Jalankan Aplikasi
```bash
python app.py
```

Output akan menampilkan:
```
 * Running on http://127.0.0.1:5000
```

### 5. Buka di Browser
Buka browser dan akses: **http://localhost:5000**

## Cara Penggunaan

### Menambah File
1. Klik tombol "📄 Tambah PDF" atau "🖼️ Tambah Gambar"
2. Pilih file yang ingin ditambahkan (bisa multiple selection)
3. File akan muncul di daftar file di panel kiri

### Preview File
1. Klik salah satu file di daftar untuk melihat preview
2. Untuk PDF, gunakan tombol Sebelumnya/Selanjutnya untuk navigasi halaman
3. Gunakan tombol rotasi untuk mengubah orientasi gambar

### Mengatur Urutan File
1. Pilih file yang ingin dipindahkan
2. Klik "⬆️ Pindah Ke Atas" atau "⬇️ Pindah Ke Bawah"

### Menghapus File
1. Klik tombol "Hapus" pada file yang ingin dihapus
2. Atau klik "🗑️ Kosongkan Daftar" untuk menghapus semua file

### Menggabung File menjadi PDF
1. Pastikan semua file sudah ditambahkan dan diatur sesuai keinginan
2. Klik tombol "✅ Gabung Gambar & PDF ke PDF"
3. File akan diproses dan otomatis diunduh
4. Anda akan ditawarkan opsi untuk menghapus file sumber setelah proses selesai

## Struktur File Aplikasi

```
ZuperPDF/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # File ini
├── templates/
│   └── index.html        # Template HTML utama
├── static/
│   ├── style.css         # Stylesheet
│   └── script.js         # JavaScript client-side
└── uploads/              # Folder untuk menyimpan file yang diunggah (auto-created)
```

## Catatan Penting

1. **Folder Uploads** - Folder `uploads/` akan dibuat otomatis di folder aplikasi. File yang diunggah disimpan sementara di sini selama session berlangsung.

2. **Session Management** - Setiap session browser berbeda akan memiliki daftar file yang terpisah. Refresh browser akan menghapus daftar file.

3. **Max File Size** - Ukuran file maksimal yang bisa diunggah adalah 500MB per file.

4. **Browser Compatibility** - Aplikasi ini bekerja optimal di browser modern (Chrome, Firefox, Edge, Safari).

## Troubleshooting

### Error: Module 'pyzbar' not found
- Barcode detection akan non-aktif, tapi aplikasi tetap berfungsi normal
- File akan diberi nama default sesuai timestamp jika barcode tidak terdeteksi

### Error: Port 5000 sudah digunakan
- Ubah port di `app.py` baris terakhir:
  ```python
  app.run(debug=True, host='127.0.0.1', port=5001)  # Ganti 5000 dengan 5001
  ```

### Browser tidak bisa akses localhost:5000
- Pastikan aplikasi sudah berjalan (lihat terminal)
- Coba akses dengan `http://127.0.0.1:5000` atau `http://localhost:5000`
- Jika masih error, cek firewall komputer Anda

## Development Mode

Aplikasi berjalan dengan `debug=True` yang berarti:
- Auto-reload ketika ada perubahan code
- Error page yang detail untuk debugging
- Jangan gunakan di production!

## Production Deployment

Untuk menjalankan di production, gunakan WSGI server seperti Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Support & Issues

Jika mengalami masalah, cek:
1. Pastikan semua dependencies terinstall dengan benar
2. Cek versi Python minimal 3.8
3. Pastikan port 5000 tidak digunakan aplikasi lain
4. Cek console browser (F12) untuk error JavaScript

## License

Aplikasi ini dibuat untuk keperluan pribadi/internal. Silakan modifikasi sesuai kebutuhan.

---

**Version 1.0 - Web Based**
Konversi dari aplikasi Tkinter desktop menjadi web application dengan Flask
