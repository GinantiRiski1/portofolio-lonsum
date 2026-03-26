# 🌿 Lonsum LEAP — Plantation Intelligence Platform v4.0

<div align="center">

<img width="406" height="124" alt="image" src="https://github.com/user-attachments/assets/14b92d89-a408-49a3-941f-8fb864755eef" />


[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM%20AI-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://integrate.api.nvidia.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Dashboard kecerdasan buatan untuk memantau, menganalisis, dan memprediksi produksi perkebunan kelapa sawit PT London Sumatra Indonesia (Lonsum)**

[🎬 Demo Video](#-demo) · [🚀Cobain Aplikasinya!](https://portofolio-lonsum-production.up.railway.app)

---

> 🏆 **LEAP Program Portfolio Project** — PT London Sumatra Indonesia Tbk  
> Developed as part of the **Lonsum Excellent Acceleration Program (LEAP)** application portfolio

</div>

---

## 📋 Daftar Isi

- [🎬 Demo](#-demo)
- [📊 Fitur Utama](#-fitur-utama)
- [💡 Business Understanding](#-business-understanding)
- [🏗️ Arsitektur Sistem](#️-arsitektur-sistem)
- [📁 Struktur Proyek](#-struktur-proyek)
- [🚀 Quick Start (Local)](#-quick-start)
- [📦 Requirements](#-requirements)
- [⚙️ Konfigurasi](#️-konfigurasi)
- [📊 Format Data CSV](#-format-data-csv)
- [🖥️ Screenshots](#️-screenshots)
- [🤖 Teknologi](#-teknologi)
- [👤 Author](#-author)

---

## 🎬 Demo

<div align="center">

### 📺 Video Demo Lengkap

[![Demo Video](screenshots/thumbnail_yt.png)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

> 🔗 **[Tonton Demo di YouTube →](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)**

### 🌐 Live Demo

> 🔗 **[Coba Aplikasi Langsung →](https://portofolio-lonsum-production.up.railway.app)**  
> *(Upload file yang tersedia di repo ini untuk mencoba)*

</div>

---

## 📊 Fitur Utama

### 🆕 New in v4.0 — Semua Fitur Enterprise

| Fitur | Deskripsi | Status |
|-------|-----------|--------|
| 📄 **PDF Annual Report** | Cover page + 6 seksi + semua chart + AI insight — satu klik, siap rapat | ✅ NEW |
| 📊 **Comparative Analysis (YoY)** | Upload 2 CSV atau 1 CSV multi-tahun → perbandingan otomatis | ✅ NEW |
| 🔔 **Alert Real-Time** | 🔴 Kritis / 🟡 Perlu Perhatian / 🟢 Normal per estate otomatis | ✅ NEW |
| 🔮 **Forecast 3 Bulan** | Prediksi produksi 3 bulan ke depan dengan widening confidence interval | ✅ NEW |
| 🏭 **Estate Drilldown Modal** | Klik estate → analisis mendalam: tren, ranking fleet, faktor dominan | ✅ NEW |
| ⚗️ **What-If Simulator** | Input manual parameter → prediksi produksi real-time dari model ML | ✅ NEW |
| ✅ **Data Quality Score** | Skor A–D otomatis: completeness, outlier %, duplikasi data | ✅ NEW |
| 🖼️ **Export Chart PNG** | Tombol download di setiap grafik untuk PowerPoint/presentasi | ✅ NEW |
| 🤖 **10 AI Insights** | Setiap visualisasi dilengkapi analisis dari NVIDIA Nemotron LLM | ✅ |
| 📊 **5 Download Excel** | Produksi bulanan, statistik estate, alert, forecast, model ML | ✅ |
| 📈 **10 Visualisasi** | Trend, seasonal, stacked bar, boxplot, heatmap, scatter, model eval, fi | ✅ |
| 🤖 **3 Model ML** | Linear Regression, Random Forest, Gradient Boosting — auto-select terbaik | ✅ |

---

## 💡 Business Understanding

### Latar Belakang

PT London Sumatra Indonesia (Lonsum) adalah salah satu perusahaan perkebunan kelapa sawit terbesar di Indonesia dengan operasi multi-estate yang tersebar di berbagai wilayah. Tantangan utama dalam manajemen produksi perkebunan:

1. **Monitoring Terfragmentasi** — Laporan produksi masih manual dan tersebar, menyulitkan pengambilan keputusan cepat
2. **Keterlambatan Deteksi Masalah** — Estate dengan produktivitas rendah sering baru terdeteksi saat akhir periode
3. **Tidak Ada Prediksi Produksi** — Perencanaan distribusi dan logistik sulit tanpa forecast yang akurat
4. **Analisis Faktor yang Lambat** — Tidak ada sistem untuk menganalisis pengaruh curah hujan, pupuk, dan tenaga kerja secara otomatis

### Solusi

**LEAP Plantation Intelligence Platform** hadir sebagai sistem monitoring produksi berbasis data yang:

```
Raw CSV Data → Automated Pipeline → 10 Charts + ML Model → AI Insights + Forecasting
```

| Problem | Solusi LEAP |
|---------|-------------|
| Laporan manual, lambat | Upload CSV → Dashboard otomatis dalam <60 detik |
| Deteksi masalah terlambat | Alert 🔴🟡🟢 real-time per estate berdasarkan produktivitas |
| Tidak ada prediksi | Forecast 3 bulan ke depan dengan confidence interval |
| Sulit analisis faktor | Korelasi + scatter + feature importance otomatis |
| Laporan tidak profesional | PDF Annual Report siap rapat satu klik |

### Metrik Keberhasilan

- **R² Model** ≥ 0.80 → Model dapat menjelaskan ≥80% variasi produksi
- **MAE** < 10% dari rata-rata produksi → Error prediksi dalam batas toleransi
- **Alert Accuracy** — Estate dengan produktivitas < 75% fleet average otomatis ditandai 🔴

### Impact untuk Lonsum

- ⏱️ **Efisiensi Waktu**: Laporan bulanan dari manual ~3 hari → otomatis <60 detik
- 📊 **Decision Support**: Manajer kebun dapat melihat kondisi seluruh estate dalam satu dashboard
- 🎯 **Proactive Management**: Alert real-time memungkinkan intervensi sebelum masalah memburuk
- 💰 **Resource Optimization**: What-If simulator membantu optimasi alokasi pupuk dan tenaga kerja

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────┐
│                     LONSUM LEAP v4.0                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📁 CSV Upload                                                  │
│       │                                                         │
│       ▼                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ Data Quality  │───▶│   Cleaning   │───▶│Feature Eng │       │
│  │   Scoring    │    │  & Imputing  │    │  + Encoding  │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                 │               │
│                                                 ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Charts     │◀───│  10 Visuals  │◀───│ ML Training │       │
│  │  (Matplotlib)│    │  Generation  │    │ (3 Models)   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                                       │               │
│         ▼                                       ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  NVIDIA NIM  │    │  Forecast    │    │   Alerts     │       │
│  │  AI Insights │    │  3 Months    │    │   🔴🟡🟢    │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │               │
│         └───────────────────┴───────────────────┘               │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │             FASTAPI BACKEND (main.py)                   │    │
│  │   /api/analyze  /api/predict  /api/estate/{name}        │    │
│  │   /api/download/pdf  /api/download/excel  ...           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │             HTML/CSS/JS FRONTEND (embedded)             │    │
│  │   Landing Page → Sidebar Dashboard → 10 Chart Cards     │    │
│  │   What-If Simulator → Estate Modal → Download Bar       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Alur Data Pipeline

```
Raw CSV
  │
  ├─→ [Data Quality] Completeness + Outlier + Duplicate → Score A/B/C/D
  │
  ├─→ [Cleaning] Impute missing (median/mode) + drop duplicates
  │
  ├─→ [Feature Engineering]
  │     year, month, quarter, productivity_ton_per_ha,
  │     production_per_worker, fertilizer_per_ha, estate_encoded
  │
  ├─→ [Alert Computation] Productivity vs fleet avg → 🔴🟡🟢
  │
  ├─→ [ML Training] Linear Regression + Random Forest + Gradient Boosting
  │     → Cross-validation → Best model selection → Feature importance
  │
  ├─→ [Forecast] Best model → 3 months ahead per estate
  │     → Widening CI: MAE × [1.0, 1.5, 2.2]
  │
  ├─→ [10 Visualizations] Matplotlib/Seaborn → Base64 PNG
  │
  └─→ [10 AI Insights] NVIDIA Nemotron LLM → Indonesian language analysis
```

---

## 📁 Struktur Proyek

```
lonsum-leap/
│
├── 📄 main.py                    # FastAPI backend + Frontend HTML (single file)
├── 📋 requirements.txt           # Python dependencies
├── 📖 README.md                  # Dokumentasi ini
└── 📊 sample_data.csv            # Sample data untuk testing 

```

---

## 🚀 Quick Start

### Prerequisites

Pastikan kamu sudah menginstall:

| Tool | Versi Minimum | Cek |
|------|--------------|-----|
| Python | 3.10+ | `python --version` |
| pip | 23.0+ | `pip --version` |
| Git | 2.x | `git --version` |

---

### Step 1 — Clone Repository

```bash
git clone https://github.com/GinantiRiski1/portofolio-lonsum.git
cd portofolio-lonsum
```

---

### Step 2 — Buat Virtual Environment

> ⚠️ **Sangat disarankan** menggunakan virtual environment agar tidak konflik dengan package Python lain

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Setelah aktif, terminal kamu akan menampilkan `(venv)` di awal baris.

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> ⏱️ Proses instalasi membutuhkan ~2–5 menit tergantung koneksi internet

Verifikasi instalasi berhasil:
```bash
pip list | grep -E "fastapi|sklearn|reportlab|pandas"
```

---

### Step 4 — Konfigurasi API Key

Buka file `main.py` dan temukan baris berikut (sekitar baris 25):

```python
NVIDIA_API_KEY  = "YOUR_NVIDIA_API_KEY_HERE"   # ← Ganti ini dengan ini "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"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL    = "meta/llama-4-maverick-17b-128e-instruct"
```

**Cara mendapatkan NVIDIA API Key:**
1. Kunjungi [https://integrate.api.nvidia.com](https://integrate.api.nvidia.com)
2. Daftar / login dengan akun NVIDIA
3. Buat API key baru
4. Copy dan paste ke `main.py`

> 💡 **Tanpa API Key:** Dashboard tetap berfungsi, namun AI Insight akan menampilkan pesan fallback

---

### Step 5 — Jalankan Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Output yang diharapkan:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Step 6 — Buka Browser

```
http://localhost:8000
```

🎉 **Dashboard siap digunakan!**

---

### Step 7 — Upload Data & Mulai Analisis

1. Klik tombol **"Mulai Analisis"** di landing page
2. Upload file CSV (gunakan `sample_data.csv` untuk testing)
3. Tunggu proses analisis ~30–60 detik (termasuk AI insights)
4. Explore dashboard, download laporan!

---

### Troubleshooting

<details>
<summary>❌ Error: <code>ModuleNotFoundError: No module named 'reportlab'</code></summary>

```bash
pip install reportlab==4.2.0
```
</details>

<details>
<summary>❌ Error: <code>Port 8000 already in use</code></summary>

Gunakan port lain:
```bash
uvicorn main:app --reload --port 8001
```
Lalu buka `http://localhost:8001`
</details>

<details>
<summary>❌ Error saat upload CSV: <code>Missing columns</code></summary>

Pastikan CSV kamu memiliki **tepat 7 kolom** berikut (nama harus persis sama):
```
date, estate, plantation_area_ha, rainfall_mm, workers, fertilizer_kg, production_tons
```
</details>

<details>
<summary>❌ AI Insights tidak muncul / error</summary>

1. Cek API key NVIDIA sudah benar di `main.py`
2. Pastikan koneksi internet aktif
3. Coba model alternatif: ganti `NVIDIA_MODEL` ke `"nvidia/llama-3.1-nemotron-ultra-253b-v1"`
</details>

<details>
<summary>⚠️ PDF Download gagal / error</summary>

```bash
pip install reportlab==4.2.0 Pillow==10.3.0
```
</details>

---

## 📦 Requirements

```
fastapi==0.111.0
uvicorn==0.30.1
python-multipart==0.0.9
pandas==2.2.2
numpy==1.26.4
matplotlib==3.9.0
seaborn==0.13.2
scikit-learn==1.5.0
openpyxl==3.1.4
xlsxwriter==3.2.0
httpx==0.27.0
reportlab==4.2.0
Pillow==10.3.0
```

---

## ⚙️ Konfigurasi

### Variabel yang Bisa Dikustomisasi (di `main.py`)

```python
# ── NVIDIA LLM Config ──────────────────────────────────────────────
NVIDIA_API_KEY  = "your-api-key"                              # API Key NVIDIA NIM
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1/..."  # Base URL API
NVIDIA_MODEL    = "meta/llama-4-maverick-17b-128e-instruct"  # Model LLM

# ── Alternatif Model LLM ───────────────────────────────────────────
# NVIDIA_MODEL = "nvidia/llama-3.1-nemotron-ultra-253b-v1"
# NVIDIA_MODEL = "meta/llama-3.1-70b-instruct"

# ── Alert Threshold ────────────────────────────────────────────────
# Di fungsi compute_alerts():
# ratio < 0.70  → 🔴 Kritis
# ratio < 0.88  → 🟡 Perlu Perhatian
# ratio >= 0.88 → 🟢 Normal

# ── Forecast Config ────────────────────────────────────────────────
# Di fungsi compute_forecast_3m():
ci_mult = [1.0, 1.5, 2.2]  # Widening CI multiplier per bulan
```

### Menjalankan di Production

```bash
# Tanpa --reload untuk production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

# Dengan HTTPS (butuh SSL certificate)
uvicorn main:app --host 0.0.0.0 --port 443 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

---

## 📊 Format Data CSV

### Kolom yang Diperlukan

| Kolom | Tipe Data | Contoh | Keterangan |
|-------|-----------|--------|------------|
| `date` | string | `2023-01-15` | Format: YYYY-MM-DD |
| `estate` | string | `Estate Alpha` | Nama kebun/estate |
| `plantation_area_ha` | integer | `850` | Luas lahan dalam hektar |
| `rainfall_mm` | integer | `215` | Curah hujan dalam mm |
| `workers` | integer | `78` | Jumlah tenaga kerja |
| `fertilizer_kg` | integer | `4200` | Penggunaan pupuk dalam kg |
| `production_tons` | float | `142.5` | Hasil produksi dalam ton |

### Contoh Data

```csv
date,estate,plantation_area_ha,rainfall_mm,workers,fertilizer_kg,production_tons
2023-01-01,Estate Alpha,850,215,78,4200,142.5
2023-01-01,Estate Beta,620,198,65,3100,98.3
2023-02-01,Estate Alpha,850,245,80,4350,155.2
2023-02-01,Estate Beta,620,230,67,3200,105.7
```

### Tips Data Berkualitas

- ✅ Minimal **100 baris** data untuk model ML yang akurat
- ✅ **Multi-estate** (minimal 2 estate) untuk perbandingan yang bermakna
- ✅ **Multi-year** (minimal 2 tahun) untuk analisis YoY dan seasonality
- ✅ Tidak ada nilai negatif pada kolom numerik
- ⚠️ Missing values akan otomatis di-impute dengan median/mode

---

## 🖥️ Tampilan Halaman Website



### 1. Landing Page

![WhatsApp Image 2026-03-26 at 21 11 43](https://github.com/user-attachments/assets/469e0a6c-a95a-40ab-a36d-73d7a15b7adc)
<br>
![WhatsApp Image 2026-03-26 at 21 12 25](https://github.com/user-attachments/assets/d475b6ec-c4c2-4150-9e1a-1942d3eb240b)
<br>
![WhatsApp Image 2026-03-26 at 21 14 07](https://github.com/user-attachments/assets/76433808-fa76-4482-9ca1-5d45e0fe7519)

---

### 2. Dashboard Overview — Upload Dokumen dan Proses Analis
![WhatsApp Image 2026-03-26 at 21 33 51](https://github.com/user-attachments/assets/5b4b2b4b-5d3d-4725-a895-4d535738eaab)
<br>
![WhatsApp Image 2026-03-26 at 21 34 28](https://github.com/user-attachments/assets/38784eb2-1436-4b37-8d70-de79341c50bb)
<br>
![WhatsApp Image 2026-03-26 at 21 32 47](https://github.com/user-attachments/assets/b7f50503-5e9b-4d04-a21f-7524a0370f84)

---
### 3. Dashboard Overview — KPI Cards & Alert Banner

![WhatsApp Image 2026-03-26 at 21 18 24](https://github.com/user-attachments/assets/4812dc16-64bc-4b5b-afdb-40d4f79ef1f5)
<br>
![WhatsApp Image 2026-03-26 at 21 19 18](https://github.com/user-attachments/assets/f0f06409-68f8-45e7-a1b3-91aae45d3145)
---
### 4. Dashboard Overview — Laporan Kualitas Data
![WhatsApp Image 2026-03-26 at 21 21 02](https://github.com/user-attachments/assets/23ad0fc0-247b-4465-ae1c-d3036366c2c8)

### 5. Dashboard Overview — Unduh Laporan Operasional
![WhatsApp Image 2026-03-26 at 21 21 50](https://github.com/user-attachments/assets/2a2ba2bd-22b8-4c3e-9026-7c4b9e542607)

### 6. Trend Analysis + AI Insight

![WhatsApp Image 2026-03-26 at 21 24 03](https://github.com/user-attachments/assets/4bc2a50a-6377-4321-992b-1f6d665ea4e6)
<br>
![WhatsApp Image 2026-03-26 at 21 24 42](https://github.com/user-attachments/assets/f8e5d010-13dc-49dc-8996-7185e7d1a393)
<br>
![WhatsApp Image 2026-03-26 at 21 25 19](https://github.com/user-attachments/assets/f8311be1-6fe2-4d11-8ee1-da183de8dff0)
<br>
![WhatsApp Image 2026-03-26 at 21 26 12](https://github.com/user-attachments/assets/ea7cc851-3611-429b-9072-968823d53dc3)
<br>
![WhatsApp Image 2026-03-26 at 21 46 30](https://github.com/user-attachments/assets/884162c3-62fa-4e16-a68b-b9060e6a5100)
<br>
![WhatsApp Image 2026-03-26 at 21 46 44](https://github.com/user-attachments/assets/4cd21548-41e7-4888-9c7a-7bc6aea39959)

---

### 4. Model Machine Learning
![WhatsApp Image 2026-03-26 at 21 44 09](https://github.com/user-attachments/assets/5174658f-1b6e-42e2-9355-f2ed5babb0bb)
<br>
![WhatsApp Image 2026-03-26 at 21 44 59](https://github.com/user-attachments/assets/0b568dbf-bb04-4799-8a3c-5860c757cdf6)

---

### 5. Forecast 3 Bulan

![WhatsApp Image 2026-03-26 at 21 27 16](https://github.com/user-attachments/assets/1857166a-7c36-4eeb-ae55-6a7ad90f6a3b)
<br>
![WhatsApp Image 2026-03-26 at 21 28 01](https://github.com/user-attachments/assets/f9ea9579-7825-49f1-ab14-d38f199e193c)

---

### 6. What-If Simulator

![WhatsApp Image 2026-03-26 at 21 28 56](https://github.com/user-attachments/assets/a9a85fa0-8b32-41de-8d0b-c6b8b6136ca0)

---

### 7. Estate Drilldown Modal
![WhatsApp Image 2026-03-26 at 21 51 00](https://github.com/user-attachments/assets/9f210984-b5bf-47df-b36b-62a135ddb541)
<br>
![WhatsApp Image 2026-03-26 at 21 50 15](https://github.com/user-attachments/assets/3b9d938f-823c-4ac1-b7f1-fa9f3ed56de4)

---

### 8. Report Preview

![WhatsApp Image 2026-03-26 at 21 53 02](https://github.com/user-attachments/assets/5506ef65-cd0e-45ee-b283-377cfefffd50)
<br>
![WhatsApp Image 2026-03-26 at 22 07 15](https://github.com/user-attachments/assets/9cb8067c-11bf-4a8e-bcfc-394cc3497d6c)
<br>
![WhatsApp Image 2026-03-26 at 22 07 46](https://github.com/user-attachments/assets/fee86174-5ce4-4b08-bfad-df0bde5bd698)
<br>
![WhatsApp Image 2026-03-26 at 22 08 09](https://github.com/user-attachments/assets/d308b9a7-7bbe-4cb9-9390-ca8e2b2fc404)
<br>
![WhatsApp Image 2026-03-26 at 22 08 27](https://github.com/user-attachments/assets/cb4de6eb-4b82-451e-915a-110b7fbf7be9)
<br>
![WhatsApp Image 2026-03-26 at 22 08 39](https://github.com/user-attachments/assets/a2bb5c87-a3f4-48cd-afe7-002f407ef0c8)

---

## 🤖 Teknologi

### Backend
| Library | Versi | Fungsi |
|---------|-------|--------|
| **FastAPI** | 0.111 | Web framework async — API endpoints & serving HTML |
| **Uvicorn** | 0.30 | ASGI server untuk FastAPI |
| **Pandas** | 2.2 | Data manipulation & feature engineering |
| **NumPy** | 1.26 | Komputasi numerik |
| **scikit-learn** | 1.5 | ML models: LinearRegression, RandomForest, GradientBoosting |
| **Matplotlib** | 3.9 | Chart generation → Base64 PNG |
| **Seaborn** | 0.13 | Statistical plots (heatmap, etc.) |
| **HTTPX** | 0.27 | Async HTTP client untuk NVIDIA NIM API |
| **ReportLab** | 4.2 | PDF generation (Annual Report) |
| **openpyxl** | 3.1 | Excel file generation |

### AI / LLM
| Service | Model | Fungsi |
|---------|-------|--------|
| **NVIDIA NIM** | `meta/llama-4-maverick-17b-128e-instruct` | 10 AI insights per analisis dalam Bahasa Indonesia |

### Frontend
| Teknologi | Keterangan |
|-----------|------------|
| **Vanilla HTML/CSS/JS** | Single-file embedded dalam `main.py` — zero dependency |
| **Plus Jakarta Sans** | Google Fonts — typography utama |
| **Fraunces** | Google Fonts — display/heading serif |
| **JetBrains Mono** | Google Fonts — monospace untuk kode & data |

### Machine Learning Pipeline
```
Features: plantation_area_ha, rainfall_mm, workers, fertilizer_kg,
          month, quarter, estate_encoded (LabelEncoder)
Target:   production_tons

Models:
  ├── Linear Regression     (baseline)
  ├── Random Forest         (n_estimators=200)
  └── Gradient Boosting     (n_estimators=200)

Selection: Best R² on test set (80/20 split) + 5-fold CV
Forecast:  Best model → 3 months ahead per estate
           CI: ±MAE × [1.0, 1.5, 2.2] (widening uncertainty)
```

---

## 🗂️ API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/` | Dashboard HTML |
| `POST` | `/api/analyze` | Upload CSV → jalankan full pipeline |
| `POST` | `/api/analyze/comparative` | Upload 2 CSV → analisis YoY |
| `POST` | `/api/predict` | What-If Simulator → prediksi ML |
| `GET` | `/api/estate/{name}` | Estate drilldown detail |
| `GET` | `/api/download/pdf` | Download PDF Annual Report |
| `GET` | `/api/download/excel` | Download Excel 5-sheet |
| `GET` | `/api/download/stats` | Download Statistik Estate |
| `GET` | `/api/download/alerts` | Download Alert Produktivitas |
| `GET` | `/api/download/forecast` | Download Forecast 3 Bulan |
| `GET` | `/api/health` | Health check |

---

## 👤 Author

<div align="center">

### Ginanti Riski

**Data Analytics · Digital Transformation · Machine Learning**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/ginanti-riski-483b7a362/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/GinantiRiski1)
[![YouTube](https://img.shields.io/badge/YouTube-Subscribe-FF0000?style=for-the-badge&logo=youtube)](https://www.youtube.com/@GinantiRiski)

---

*Dibuat sebagai Portfolio Project untuk Program LEAP — PT London Sumatra Indonesia Tbk*

*"Building data-driven solutions for sustainable plantation operations"*

</div>

---

## 📄 License

```
MIT License

Copyright (c) 2026 [Ginanti Riski]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

<div align="center">

**⭐ Star repo ini jika bermanfaat!**

[![Star History](https://img.shields.io/github/stars/YOUR_USERNAME/lonsum-leap?style=social)](https://github.com/GinantiRiski1/portofolio-lonsum)

*LEAP v4.0 · PT London Sumatra Indonesia · 2025*

</div>
