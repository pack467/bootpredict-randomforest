# ⚽ Football Boots Classification & Recommendation System

## Sistem Klasifikasi dan Rekomendasi Sepatu Bola menggunakan Machine Learning (Random Forest)

---

## 📋 Deskripsi Singkat

Sistem berbasis web yang mengklasifikasikan dan merekomendasikan sepatu bola berdasarkan:
- **Peminatan** (gaya bermain): Speed, Control, Power
- **Brand** (merek): Nike, Adidas, Puma, Mizuno, Umbro
- **Posisi** pemain: Striker, Midfielder, Defender, Goalkeeper

Menggunakan algoritma **Random Forest Classifier** dari Scikit-learn dengan fitur Explainable AI (penjelasan hasil prediksi).

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Backend | Python 3.10+, FastAPI |
| ML Engine | Scikit-learn, Pandas, NumPy, Joblib |
| Database | MySQL 8.0 (aiomysql async driver) |
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| UI Framework | Bootstrap 5.3.2, Bootstrap Icons |
| Auth | JWT Token (PyJWT / python-jose), bcrypt |

---

## 📦 Software yang Dibutuhkan (Prerequisites)

Sebelum menjalankan proyek ini, pastikan semua software berikut sudah **terinstall** di komputer Anda:

### 1. Python (Versi 3.10 atau lebih baru)

- **Download**: https://www.python.org/downloads/
- Pilih versi **Python 3.10+** (disarankan 3.10, 3.11, atau 3.12)
- Saat instalasi di Windows, **WAJIB centang** ✅ `Add Python to PATH`

**Verifikasi instalasi:**
```bash
python --version
# Output contoh: Python 3.11.5

pip --version
# Output contoh: pip 23.2.1
```

> ⚠️ **Penting**: Jika perintah `python` tidak dikenali, coba gunakan `python3` atau pastikan Python sudah ditambahkan ke PATH sistem.

---

### 2. MySQL Server (Versi 8.0 atau lebih baru)

- **Download**: https://dev.mysql.com/downloads/installer/
- Pilih **MySQL Installer for Windows** (atau sesuai OS Anda)
- Saat instalasi, pilih **MySQL Server** (minimal) atau **Full Installation**
- Catat **username** dan **password** yang dibuat saat instalasi

**Alternatif menggunakan XAMPP:**
- **Download XAMPP**: https://www.apachefriends.org/download.html
- XAMPP sudah termasuk MySQL (MariaDB) bawaan
- Buka **XAMPP Control Panel** → Klik **Start** pada modul **MySQL**

**Verifikasi MySQL berjalan:**
```bash
mysql -u root -p
# Masukkan password MySQL Anda
# Jika berhasil masuk ke MySQL shell, berarti sudah berjalan

# Ketik 'exit' untuk keluar dari MySQL shell
exit
```

> ⚠️ **Penting**: Pastikan MySQL Server **berjalan (running)** sebelum menjalankan aplikasi. Jika menggunakan XAMPP, pastikan modul MySQL sudah di-**Start**.

---

### 3. Git (Opsional, untuk clone repository)

- **Download**: https://git-scm.com/downloads
- Hanya diperlukan jika Anda ingin meng-clone proyek dari repository

---

### 4. Text Editor / IDE (Opsional, untuk pengembangan)

- **Visual Studio Code** (Direkomendasikan): https://code.visualstudio.com/
- Atau editor lain pilihan Anda

---

### 5. Web Browser Modern

- **Google Chrome** (Direkomendasikan)
- Mozilla Firefox
- Microsoft Edge

---

## 📁 Struktur Proyek

```
prediksi_sepatu/
├── backend/
│   ├── app/
│   │   ├── __init__.py            # Package initializer
│   │   ├── main.py                # Entry point FastAPI (uvicorn)
│   │   ├── config.py              # Konfigurasi (MySQL, JWT, paths)
│   │   ├── routes/                # API endpoint routing
│   │   │   ├── auth.py            # Route autentikasi
│   │   │   ├── prediction.py      # Route prediksi
│   │   │   ├── history.py         # Route riwayat
│   │   │   └── admin.py           # Route admin panel
│   │   ├── controllers/           # Request handlers
│   │   ├── services/              # Business logic layer
│   │   ├── models/                # Pydantic schemas (validasi data)
│   │   ├── ml/                    # Machine Learning pipeline
│   │   │   ├── preprocessing.py   # Preprocessing data
│   │   │   ├── train.py           # Training model Random Forest
│   │   │   └── predict.py         # Prediksi menggunakan model
│   │   ├── database/              # Database layer
│   │   │   ├── connection.py      # MySQL connection pool (aiomysql)
│   │   │   └── init_db.py         # Inisialisasi tabel & seed admin
│   │   └── utils/                 # Helper functions
│   ├── requirements.txt           # Daftar library Python
│   ├── generate_dataset.py        # Script generate dataset dummy
│   └── database.db                # File database SQLite (cadangan)
├── frontend/
│   ├── login.html                 # Halaman login
│   ├── register.html              # Halaman registrasi
│   ├── dashboard.html             # Halaman utama (form prediksi)
│   ├── result.html                # Halaman hasil prediksi
│   ├── history.html               # Halaman riwayat prediksi
│   ├── admin.html                 # Halaman admin panel
│   └── static/
│       ├── css/
│       │   ├── style.css          # Stylesheet utama
│       │   └── components.css     # Stylesheet komponen
│       ├── js/
│       │   ├── config.js          # Konfigurasi API endpoint
│       │   ├── main.js            # Script utilitas umum
│       │   ├── auth.js            # Script autentikasi
│       │   ├── form.js            # Script form prediksi
│       │   ├── result.js          # Script halaman hasil
│       │   ├── history.js         # Script halaman riwayat
│       │   ├── admin.js           # Script admin panel
│       │   └── theme.js           # Script toggle dark/light mode
│       └── images/                # Gambar sepatu bola (59 file PNG)
├── dataset/
│   ├── sepatu_dataset.csv         # Dataset training (CSV)
│   └── produk_sepatu.json         # Katalog produk sepatu (JSON)
├── venv/                          # Virtual environment Python
└── README.md                      # Dokumentasi proyek (file ini)
```

---

## 🚀 Panduan Lengkap Menjalankan Aplikasi (Step-by-Step)

### Langkah 1: Download / Clone Proyek

**Opsi A — Clone dari Git (jika ada repository):**
```bash
git clone <URL_REPOSITORY>
cd prediksi_sepatu
```

**Opsi B — Download manual:**
- Download file ZIP proyek
- Extract ke folder yang diinginkan, misalnya: `F:\Jokian\prediksi_sepatu`

---

### Langkah 2: Pastikan MySQL Server Berjalan

**Jika menggunakan MySQL standalone:**
1. Buka **Services** di Windows (tekan `Win + R`, ketik `services.msc`, Enter)
2. Cari **MySQL** atau **MySQL80**
3. Pastikan status **Running**. Jika belum, klik kanan → **Start**

**Jika menggunakan XAMPP:**
1. Buka **XAMPP Control Panel**
2. Klik tombol **Start** pada baris **MySQL**
3. Pastikan muncul tulisan hijau **Running**

**Konfigurasi default database yang digunakan aplikasi:**

| Parameter | Nilai Default |
|-----------|---------------|
| Host | `localhost` |
| Port | `3306` |
| Username | `root` |
| Password | `galih0249` |
| Database | `football_boots_db` |

> ⚠️ **Jika password MySQL Anda berbeda**, ubah file `backend/app/config.py` pada baris:
> ```python
> DB_PASSWORD = os.environ.get("DB_PASSWORD", "galih0249")
> ```
> Ganti `"galih0249"` dengan password MySQL Anda.
>
> **Alternatif tanpa mengubah kode** — gunakan environment variable:
> ```bash
> set DB_PASSWORD=password_anda_disini
> ```

> 💡 **Catatan**: Database `football_boots_db` beserta semua tabelnya akan **dibuat otomatis** saat aplikasi pertama kali dijalankan. Anda **tidak perlu** membuat database secara manual.

---

### Langkah 3: Buat Virtual Environment Python

Buka **Git Bash** terminal, lalu navigasi ke folder proyek:

```bash
cd /f/Jokian/prediksi_sepatu
```

Buat virtual environment baru:
```bash
python -m venv venv
```

Aktifkan virtual environment:
```bash
source venv/Scripts/activate
```

> ✅ Jika berhasil, akan muncul `(venv)` di awal baris terminal Anda:
> ```
> (venv) user@PC MINGW64 /f/Jokian/prediksi_sepatu
> $
> ```

---

### Langkah 4: Install Library Python (Dependencies)

Pastikan virtual environment **sudah aktif** (ada tulisan `(venv)`), lalu jalankan:

```bash
cd backend
pip install -r requirements.txt
```

> 💡 Jika sudah berada di folder `backend/`, cukup jalankan `pip install -r requirements.txt` saja.

**Daftar library yang akan diinstall:**

| No | Library | Versi | Fungsi |
|----|---------|-------|--------|
| 1 | `fastapi` | 0.104.1 | Framework web backend (API) |
| 2 | `uvicorn[standard]` | 0.24.0 | ASGI server untuk menjalankan FastAPI |
| 3 | `python-multipart` | 0.0.6 | Handle form data & file upload |
| 4 | `aiomysql` | 0.2.0 | Async MySQL database driver |
| 5 | `bcrypt` | 4.1.2 | Hashing password untuk keamanan |
| 6 | `pyjwt` | 2.8.0 | Membuat & verifikasi JWT token |
| 7 | `pandas` | 2.1.4 | Manipulasi data (DataFrame) |
| 8 | `numpy` | 1.26.2 | Komputasi numerik |
| 9 | `scikit-learn` | 1.3.2 | Machine Learning (Random Forest) |
| 10 | `joblib` | 1.3.2 | Menyimpan & memuat model ML |
| 11 | `python-jose[cryptography]` | 3.3.0 | JSON Web Encryption (JWT lanjutan) |
| 12 | `cryptography` | ≥41.0.0 | Library kriptografi backend |

**Verifikasi instalasi berhasil:**
```bash
pip list
```
Pastikan semua library di atas muncul di daftar.

> ⚠️ **Jika terjadi error saat instalasi:**
> - Pastikan pip sudah versi terbaru: `pip install --upgrade pip`
> - Jika error pada `bcrypt` atau `cryptography`, Anda mungkin perlu install **Microsoft C++ Build Tools**: https://visualstudio.microsoft.com/visual-cpp-build-tools/

---

### Langkah 5: Generate Dataset (Opsional)

Proyek ini sudah menyertakan dataset di folder `dataset/`. Jika ingin men-generate ulang dataset dummy:

```bash
# Pastikan berada di folder backend
python generate_dataset.py
```

Ini akan membuat file `dataset/sepatu_dataset.csv` dengan 250 sampel data training.

---

### Langkah 6: Jalankan Backend Server (FastAPI)

Pastikan Anda berada di folder `backend/` dan virtual environment aktif:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Penjelasan perintah:**
| Parameter | Fungsi |
|-----------|--------|
| `python -m uvicorn` | Menjalankan uvicorn melalui Python module (lebih reliable) |
| `app.main:app` | Menjalankan objek `app` dari file `app/main.py` |
| `--reload` | Auto-restart server saat ada perubahan kode |
| `--port 8000` | Server berjalan di port 8000 |

**Jika berhasil, akan muncul output seperti ini:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

============================================================
  Football Boots Classification System - Starting...
============================================================
[DB] Database 'football_boots_db' ensured.
[DB] All tables created successfully.
[DB] Admin user already exists.
[DB] Connection pool created: root@localhost:3306/football_boots_db
[ML] Trained model found: .../backend/app/ml/model.pkl

[OK] Application ready!
Frontend directory: .../frontend
Open http://localhost:8000 in your browser
============================================================

INFO:     Application startup complete.
```

> ⚠️ **Jangan tutup terminal ini!** Biarkan terminal tetap berjalan selama menggunakan aplikasi.

> ⚠️ **Jika muncul error koneksi database**, pastikan:
> 1. MySQL Server sudah berjalan (Running)
> 2. Username dan password MySQL sudah benar di `backend/app/config.py`
> 3. Port 3306 tidak digunakan aplikasi lain

---

### Langkah 7: Buka Aplikasi di Browser

Buka **web browser** (Chrome direkomendasikan) dan akses:

```
http://localhost:8000
```

Anda akan diarahkan ke **halaman Login**.

---

### Langkah 8: Login ke Aplikasi

**Akun Admin Default:**

| Field | Nilai |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

Atau **daftar akun baru** melalui halaman **Register**.

---

### Langkah 9: Training Model Machine Learning (WAJIB untuk pertama kali)

Sebelum bisa melakukan prediksi, model machine learning **harus dilatih** terlebih dahulu:

1. **Login sebagai Admin** (`admin` / `admin123`)
2. Anda akan masuk ke **Admin Panel**
3. Buka tab **"Training"**
4. Klik tombol **"Latih Model"**
5. Tunggu proses training selesai (beberapa detik)
6. Akan muncul metrik evaluasi model:
   - **Accuracy** (Akurasi)
   - **Precision** (Presisi)
   - **Recall**
   - **F1-Score**
   - **Cross-Validation Score** (5-fold Stratified)
   - **Confusion Matrix**

> ✅ Setelah model berhasil dilatih, pengguna biasa (role `user`) sudah bisa melakukan **prediksi sepatu bola**.

---

### Langkah 10: Melakukan Prediksi

1. **Login** dengan akun biasa (atau buat akun baru melalui Register)
2. Di halaman **Dashboard**, isi form:
   - **Peminatan**: Speed / Control / Power
   - **Brand**: Nike / Adidas / Puma / Mizuno / Umbro
   - **Posisi**: Striker / Midfielder / Defender / Goalkeeper
3. Klik **"Prediksi"**
4. Hasil prediksi akan ditampilkan di halaman **Result** beserta:
   - Klasifikasi sepatu yang direkomendasikan
   - Probabilitas tiap kelas
   - Feature Importance (Explainable AI)
   - Rekomendasi produk sepatu

---

## 📡 Daftar Halaman Web

| URL | Halaman | Akses |
|-----|---------|-------|
| `http://localhost:8000` | Login | Semua |
| `http://localhost:8000/login` | Login | Semua |
| `http://localhost:8000/register` | Registrasi | Semua |
| `http://localhost:8000/dashboard` | Dashboard (Form Prediksi) | User & Admin |
| `http://localhost:8000/result` | Hasil Prediksi | User & Admin |
| `http://localhost:8000/history` | Riwayat Prediksi | User & Admin |
| `http://localhost:8000/admin` | Admin Panel | Admin saja |

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/register` | Register user baru |
| GET | `/api/auth/me` | Mendapatkan info user yang login |

### Prediction
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/predict` | Klasifikasi & rekomendasi sepatu |

### History
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/history` | Melihat riwayat prediksi |
| DELETE | `/api/history/{id}` | Menghapus riwayat prediksi |
| GET | `/api/history/stats` | Statistik prediksi user |

### Admin
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/admin/dashboard` | Statistik dashboard admin |
| POST | `/api/admin/upload-dataset` | Upload dataset CSV baru |
| POST | `/api/admin/train` | Training model ML |
| GET | `/api/admin/training-logs` | Log riwayat training |
| GET | `/api/admin/users` | Daftar semua user |
| DELETE | `/api/admin/users/{id}` | Hapus user |
| GET | `/api/admin/dataset` | Lihat data dataset |

### Health Check
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/health` | Cek status API server |

---

## 🤖 Machine Learning Pipeline

| Tahap | Detail |
|-------|--------|
| **1. Preprocessing** | Label Encoding untuk fitur kategorikal (peminatan, brand, posisi) |
| **2. Train/Test Split** | 80% training, 20% testing (Stratified) |
| **3. Model** | Random Forest Classifier |
| **4. Hyperparameter** | `n_estimators=100`, `max_depth=10`, `min_samples_split=5`, `min_samples_leaf=2`, `class_weight="balanced"` |
| **5. Evaluasi** | Accuracy, Precision, Recall, F1-Score, Confusion Matrix |
| **6. Cross-Validation** | Stratified K-Fold (5-fold) |
| **7. Explainable AI** | Feature Importance + penjelasan dalam Bahasa Indonesia |
| **8. Model Persistence** | Disimpan dengan joblib (cache singleton di memori) |

---

## 🔧 Troubleshooting (Pemecahan Masalah)

### ❌ Error: `python is not recognized as an internal or external command`
**Solusi:**
1. Pastikan Python sudah terinstall
2. Pastikan saat instalasi Python, opsi **"Add Python to PATH"** sudah dicentang
3. Restart Command Prompt / PowerShell setelah instalasi
4. Jika masih tidak bisa, tambahkan PATH Python secara manual:
   - Buka **Settings** → **System** → **About** → **Advanced system settings**
   - Klik **Environment Variables**
   - Edit variabel **Path** → tambahkan path instalasi Python (contoh: `C:\Python311\` dan `C:\Python311\Scripts\`)

### ❌ Error: `Module not found` saat menjalankan uvicorn
**Solusi:**
1. Pastikan virtual environment sudah **aktif** (ada tulisan `(venv)` di terminal)
2. Jalankan ulang: `pip install -r requirements.txt`
3. Pastikan menjalankan perintah dari folder `backend/`

### ❌ Error: `Can't connect to MySQL server on 'localhost'`
**Solusi:**
1. Pastikan MySQL Server sudah berjalan (Running)
2. Jika menggunakan XAMPP, pastikan modul MySQL sudah di-**Start**
3. Periksa port MySQL (default: 3306) tidak digunakan aplikasi lain
4. Periksa username dan password di `backend/app/config.py`

### ❌ Error: `Access denied for user 'root'@'localhost'`
**Solusi:**
1. Password MySQL Anda tidak sesuai dengan konfigurasi
2. Ubah password di `backend/app/config.py`:
   ```python
   DB_PASSWORD = os.environ.get("DB_PASSWORD", "PASSWORD_ANDA")
   ```
3. Atau set environment variable: `set DB_PASSWORD=PASSWORD_ANDA`

### ❌ Error: `PermissionError` atau `Execution Policy` di PowerShell
**Solusi:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ Error: `error: Microsoft Visual C++ 14.0 or greater is required`
**Solusi:**
1. Download dan install **Microsoft C++ Build Tools**: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Saat instalasi, centang **"Desktop development with C++"**
3. Restart komputer
4. Jalankan ulang `pip install -r requirements.txt`

### ❌ Halaman web tidak bisa diakses / 404 Not Found
**Solusi:**
1. Pastikan backend server sedang berjalan di terminal
2. Pastikan URL yang diakses benar: `http://localhost:8000`
3. Coba refresh halaman dengan `Ctrl + F5` (hard refresh)

### ❌ Prediksi gagal / Error saat prediksi
**Solusi:**
1. Pastikan model sudah di-training melalui **Admin Panel** → **Training** → **Latih Model**
2. Jika belum pernah training, model belum ada dan prediksi akan gagal

### ❌ Port 8000 sudah digunakan
**Solusi:**
Gunakan port lain saat menjalankan server:
```bash
python -m uvicorn app.main:app --reload --port 9000
```
Lalu akses `http://localhost:9000`

> ⚠️ Jika mengganti port, ubah juga file `frontend/static/js/config.js`:
> ```javascript
> const API_BASE = 'http://localhost:9000';
> ```

---

## 📋 Ringkasan Perintah Cepat (Quick Reference)

Semua perintah di bawah menggunakan **Git Bash** terminal.

```bash
# ========================================
# SETUP PERTAMA KALI (Git Bash)
# ========================================

# 1. Masuk ke folder proyek
cd /f/Jokian/prediksi_sepatu

# 2. Buat virtual environment
python -m venv venv

# 3. Aktifkan virtual environment
source venv/Scripts/activate

# 4. Install dependencies
cd backend
pip install -r requirements.txt

# 5. Jalankan server
python -m uvicorn app.main:app --reload --port 8000

# 6. Buka browser → http://localhost:8000
# 7. Login admin → admin / admin123
# 8. Training model → Admin Panel → Training → Latih Model
# 9. Selesai! Siap digunakan.


# ========================================
# MENJALANKAN SETELAH SETUP (sehari-hari)
# ========================================

# 1. Buka Git Bash terminal
cd /f/Jokian/prediksi_sepatu

# 2. Aktifkan virtual environment
source venv/Scripts/activate

# 3. Jalankan server
cd backend
python -m uvicorn app.main:app --reload --port 8000

# 4. Buka browser → http://localhost:8000
```

---

## 🔑 Akun Default

| Username | Password | Role | Akses |
|----------|----------|------|-------|
| `admin` | `admin123` | Admin | Admin Panel, Dashboard, Prediksi, History |

> 💡 User biasa bisa mendaftar sendiri melalui halaman **Register**.

---

## ⚙️ Konfigurasi Aplikasi

Semua konfigurasi terpusat di file `backend/app/config.py`:

| Konfigurasi | Default | Keterangan |
|-------------|---------|------------|
| `DB_HOST` | `localhost` | Alamat server MySQL |
| `DB_PORT` | `3306` | Port MySQL |
| `DB_USER` | `root` | Username MySQL |
| `DB_PASSWORD` | `galih0249` | Password MySQL |
| `DB_NAME` | `football_boots_db` | Nama database |
| `SECRET_KEY` | `football-boots-...` | Secret key JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (24 jam) | Durasi token login |

Semua konfigurasi juga bisa di-override menggunakan **environment variable** tanpa mengubah kode:
```bash
# Windows CMD
set DB_PASSWORD=password_baru
set DB_HOST=192.168.1.100

# Windows PowerShell
$env:DB_PASSWORD="password_baru"
$env:DB_HOST="192.168.1.100"
```

---

## 📜 Lisensi

Proyek ini dibuat untuk keperluan **tugas akhir (skripsi)**.

---

## 📞 Kontak

Jika ada pertanyaan atau kendala, silakan hubungi pengembang proyek.
