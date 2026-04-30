# E-Commerce Dashboard 

Sebuah dashboard interaktif berbasis Streamlit untuk menganalisis dataset e-commerce publik (Olist Dataset). Dashboard ini menyajikan wawasan terkait preferensi metode pembayaran, evaluasi waktu pengiriman, serta segmentasi pelanggan menggunakan metode RFM.

## Setup Environment

Untuk menjalankan proyek ini di local, ikuti langkah-langkah instalasi berikut:

### 1. Buka Terminal
Pastikan Anda sudah berada di dalam folder proyek utama (contoh: folder `submission`).

### 2. Install Library yang Dibutuhkan
Instal dependensi library Python menggunakan `pip`. Semua daftar library sudah dicantumkan dalam `requirements.txt`.

```bash
pip install -r requirements.txt
```

*(Catatan: Jika Anda menggunakan versi Python spesifik di MacOS, gunakan perintah seperti `python3.11 -m pip install -r requirements.txt`)*

## Cara Menjalankan Dashboard (Run Streamlit App)

Setelah semua library berhasil diinstal, pastikan Anda berada di direktori `submission` lalu jalankan perintah berikut di terminal:

```bash
streamlit run dashboard/dashboard.py
```

Atau jika Anda ingin menjalankan menggunakan *path* spesifik modul Python (seperti yang Anda lakukan sebelumnya):
```bash
python3.11 -m streamlit run dashboard/dashboard.py
```

Dashboard akan otomatis terbuka di browser default Anda (biasanya di `http://localhost:8501`).
