<div align="center">

<!-- LOGO / BANNER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=1a6b3c&height=200&section=header&text=LONSUM%20LEAP%20v5.0&fontSize=48&fontColor=ffffff&fontAlignY=38&desc=Plantation%20Intelligence%20Platform&descAlignY=58&descSize=18&descColor=c9a84c" width="100%"/>

<!-- BADGES -->
<p>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white"/>
  <img src="https://img.shields.io/badge/NVIDIA_NIM-LLM-76B900?style=for-the-badge&logo=nvidia&logoColor=white"/>
  <img src="https://img.shields.io/badge/ReportLab-PDF-CC0000?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/openpyxl-Excel-217346?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Railway-Deploy-0B0D0E?style=for-the-badge&logo=railway&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge"/>
</p>

<!-- DEMO LINKS -->
<p>
  <a href="https://lonsum.up.railway.app/">
    <img src="https://img.shields.io/badge/🌐 Live Demo-Klik di sini-1a6b3c?style=for-the-badge"/>
  </a>
  &nbsp;
  <a href="https://youtube.com/your-video-link">
    <img src="https://img.shields.io/badge/🎥 Video Demo-Tonton di YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/>
  </a>
  &nbsp;
  <a href="https://github.com/GinantiRiski1/portofolio-lonsum">
    <img src="https://img.shields.io/badge/⭐ Star Repository-GitHub-181717?style=for-the-badge&logo=github"/>
  </a>
</p>

<br/>

> **Platform kecerdasan buatan berbasis data** untuk memantau, menganalisis, dan memprediksi<br/>
> produksi perkebunan kelapa sawit PT London Sumatra Indonesia — dari CSV mentah menjadi<br/>
> laporan eksekutif siap rapat direksi, hanya dalam **30 detik**.

<br/>

</div>

---

## 📋 Daftar Isi

| # | Bagian |
|---|--------|
| 1 | [Tentang Proyek](#-tentang-proyek) |
| 2 | [Business Understanding](#-business-understanding) |
| 3 | [Solusi yang Dibangun](#-solusi-yang-dibangun) |
| 4 | [Fitur Lengkap](#-fitur-lengkap) |
| 5 | [Dokumentasi Tampilan](#-dokumentasi-tampilan) |
| 6 | [Arsitektur Sistem](#️-arsitektur-sistem) |
| 7 | [Tech Stack](#-tech-stack) |
| 8 | [Alur Pipeline Analisis](#-alur-pipeline-analisis) |
| 9 | [Model Machine Learning](#-model-machine-learning) |
| 10 | [Format Data CSV](#-format-data-csv) |
| 11 | [Struktur Proyek](#-struktur-proyek) |
| 12 | [Instalasi & Menjalankan Lokal](#-instalasi--menjalankan-di-lokal) |
| 13 | [Deployment di Railway](#-deployment-di-railway) |
| 14 | [Akun Demo](#-akun-demo) |
| 15 | [Output yang Dihasilkan](#-output-yang-dihasilkan) |
| 16 | [Changelog v5.0](#-changelog-v50) |
| 17 | [Tentang Pembuat](#-tentang-pembuat) |

---

## 🌿 Tentang Proyek

**Lonsum LEAP** *(Lonsum Enterprise Analytics Platform)* adalah sebuah **full-stack web application** yang dibangun dari nol untuk menjawab kebutuhan nyata analitik perkebunan skala enterprise.

Proyek ini menggabungkan tiga domain sekaligus:

- **Data Engineering** — pipeline ETL otomatis, data quality scoring, feature engineering
- **Machine Learning** — training, evaluasi, dan inferensi 3 model regresi secara bersamaan
- **AI Generative** — 10 insight analitis per dataset dihasilkan secara paralel via LLM (NVIDIA NIM)

Seluruh aplikasi — backend, frontend, laporan PDF, dan Excel — dibangun dalam **satu file Python** (`main.py`) tanpa framework JavaScript eksternal, membuktikan kemampuan membangun sistem end-to-end yang efisien dan terstruktur.

---

## 🏢 Business Understanding

### Latar Belakang

**PT London Sumatra Indonesia Tbk (Lonsum)** adalah salah satu perusahaan agribisnis terbesar di Indonesia, berdiri sejak 1906, dengan operasi perkebunan kelapa sawit, karet, teh, dan kakao di Sumatera, Kalimantan, Sulawesi, dan Papua.

Dengan puluhan **estate** (kebun produksi) yang tersebar di berbagai pulau, tim manajemen menghadapi tantangan nyata dalam memproses, memvisualisasikan, dan menginterpretasikan data produksi bulanan yang terus bertambah.

### Permasalahan Bisnis

```
📌 Masalah 1 — Fragmentasi Data
   Data produksi tersimpan terpisah per estate, tanpa konsolidasi terpusat.
   Tim analis menghabiskan berjam-jam hanya untuk merangkum data dasar.

📌 Masalah 2 — Tidak Ada Early Warning
   Tidak ada sistem yang memberikan sinyal dini ketika sebuah estate
   mengalami penurunan produktivitas signifikan di bawah rata-rata fleet.

📌 Masalah 3 — Laporan Manual = Lambat
   Annual report dan laporan bulanan dibuat manual di Excel/Word,
   memakan waktu berhari-hari, rentan human error.

📌 Masalah 4 — Tidak Ada Prediksi Ke Depan
   Manajemen tidak memiliki alat untuk memproyeksikan produksi bulan
   depan secara kuantitatif dan berbasis data historis.

📌 Masalah 5 — Faktor Produksi Tidak Terukur
   Tidak diketahui secara pasti faktor mana (curah hujan, pupuk,
   tenaga kerja, atau luas lahan) yang paling menentukan hasil produksi.

📌 Masalah 6 — Analisis Perbandingan Antar Tahun Sulit
   Membandingkan performa 2023 vs 2024 per estate membutuhkan
   proses pivot table manual yang memakan waktu.

📌 Masalah 7 — Knowledge Barrier
   Tidak semua manajer estate memiliki kemampuan analisis data.
   Mereka butuh cara mudah untuk "bertanya" tentang kondisi kebun mereka.
```

### Stakeholder yang Terdampak

| Stakeholder | Kebutuhan |
|---|---|
| **Direktur Operasional** | Ringkasan performa fleet cepat, forecast produksi, laporan PDF siap presentasi |
| **Manajer Estate** | Alert jika kebunnya underperform, detail perbandingan vs fleet average |
| **Data Analyst** | Dashboard interaktif, export data bersih, akses model ML |
| **Agronomi** | Analisis faktor curah hujan, pupuk, korelasi terhadap produksi |
| **Tim Finance** | Proyeksi produksi 3 bulan untuk perencanaan anggaran |

---

## 💡 Solusi yang Dibangun

LEAP menjawab setiap permasalahan di atas dengan solusi konkret:

| Masalah | Solusi LEAP | Teknologi |
|---|---|---|
| Fragmentasi data | Upload 1 CSV → konsolidasi + analisis otomatis penuh | pandas, FastAPI |
| Tidak ada early warning | Sistem alert 🔴🟡🟢 real-time per estate | Python logic, threshold engine |
| Laporan manual lambat | PDF Annual Report + 4 Excel otomatis, 1 klik | ReportLab, openpyxl |
| Tidak ada prediksi | Forecast 3 bulan dengan confidence interval | scikit-learn (RF/GB/LR) |
| Faktor produksi tidak terukur | Feature importance + analisis korelasi Pearson | Random Forest, matplotlib |
| Perbandingan YoY sulit | Comparative analysis otomatis dari CSV multi-tahun | pandas groupby, matplotlib |
| Knowledge barrier | Chat AI — tanya dalam Bahasa Indonesia natural | NVIDIA NIM, Llama 4 Maverick |

---

## ✨ Fitur Lengkap

<details>
<summary><b>💬 Chat with Your Data (NEW v5.0)</b></summary>
<br/>

Floating chat window dengan AI analyst berbasis **NVIDIA NIM (Llama 4 Maverick)**. Setelah CSV diupload, konteks dataset (ringkasan produksi, estate, model ML, alert) otomatis disuntikkan ke sistem prompt. Pengguna dapat bertanya dalam Bahasa Indonesia natural, multi-turn, tanpa perlu memahami SQL atau kode apapun.

Contoh pertanyaan yang bisa dijawab:
- *"Estate mana yang produktivitasnya paling rendah bulan ini?"*
- *"Apa rekomendasi untuk meningkatkan produksi Estate Belitung?"*
- *"Berapa prediksi produksi total bulan depan?"*

</details>

<details>
<summary><b>📄 PDF Annual Report Profesional</b></summary>
<br/>

Laporan PDF lengkap dibuat otomatis menggunakan **ReportLab** dengan elemen:
- **Cover page** — desain profesional dengan statistik ringkas dan branding Lonsum
- **Header/footer** dinamis di setiap halaman
- **6 seksi analisis** lengkap dengan chart dan tabel
- **AI insight** per seksi (bukan template statis — digenerate dari data aktual)
- Siap dibawa ke rapat direksi tanpa editing

</details>

<details>
<summary><b>🔮 Forecast 3 Bulan dengan Confidence Interval</b></summary>
<br/>

Model ML terbaik (dipilih otomatis dari 3 kandidat berdasarkan R²) memproyeksikan produksi per estate untuk **Bulan +1, +2, +3**. Confidence interval melebar sesuai horizon waktu:
- Bulan +1: ±1× MAE
- Bulan +2: ±1.5× MAE  
- Bulan +3: ±2.2× MAE

Divisualisasikan sebagai grouped bar chart dengan error bar, disertai tabel ringkas.

</details>

<details>
<summary><b>⚗️ What-If Scenario Simulator</b></summary>
<br/>

Input skenario operasional secara manual → prediksi real-time dari model terlatih. Berguna untuk menjawab pertanyaan seperti: *"Jika curah hujan turun 30% dan kita tambah 15 pekerja, produksi Estate X berubah berapa?"*

Output: prediksi ton, rentang bawah-atas, produktivitas/ha, dan perbandingan vs fleet average.

</details>

<details>
<summary><b>🔔 Alert Engine Real-time</b></summary>
<br/>

Setiap estate dikategorikan otomatis saat data diupload:

| Level | Kondisi | Warna |
|---|---|---|
| **Kritis** | Produktivitas < 70% rata-rata fleet | 🔴 Merah |
| **Perhatian** | Produktivitas 70–88% rata-rata fleet | 🟡 Kuning |
| **Normal** | Produktivitas ≥ 88% rata-rata fleet | 🟢 Hijau |

</details>

<details>
<summary><b>🏭 Estate Drilldown Interaktif</b></summary>
<br/>

Klik nama estate di dashboard → modal popup dengan:
- 4 metrik kunci (total produksi, avg bulanan, produktivitas/ha, peringkat fleet)
- Chart tren historis vs fleet average dengan anotasi
- Radar chart rasio 5 metrik vs rata-rata fleet
- AI insight spesifik untuk estate tersebut

</details>

<details>
<summary><b>📊 Perbandingan YoY Otomatis</b></summary>
<br/>

mode tersedia:
1. **Auto split** — Upload 1 CSV multi-tahun, sistem otomatis memisahkan per tahun


Output: grouped bar per estate, % change per estate, summary card, dan AI insight komparatif.

</details>

<details>
<summary><b>✅ Data Quality Scoring</b></summary>
<br/>

Sebelum analisis, setiap dataset dievaluasi kualitasnya secara otomatis:

| Komponen | Bobot | Metode |
|---|---|---|
| Completeness | 40% | Persentase sel tidak kosong |
| Outlier-free | 35% | IQR method per kolom numerik |
| Duplikasi-free | 25% | Exact duplicate rows |

Skor gabungan 0–100 divisualisasikan dengan donut gauge berwarna (hijau/kuning/merah).

</details>

---

## 📸 Dokumentasi Tampilan

> Screenshot diambil langsung dari aplikasi yang sudah di-deploy di Railway.

### 1. Landing Page — Hero Section
<img width="1919" height="877" alt="image" src="https://github.com/user-attachments/assets/79391bd9-e0ab-47fd-8e80-f3e732dc478e" />
<br>
<img width="1912" height="871" alt="image" src="https://github.com/user-attachments/assets/9b579755-9b20-4b5f-bfff-a027a23baa6a" />
<br>
<img width="1908" height="746" alt="image" src="https://github.com/user-attachments/assets/d107fa03-9025-4b18-8759-6479fbcc8daa" />

---

### 2. Halaman Login
<img width="1745" height="835" alt="image" src="https://github.com/user-attachments/assets/c0bfbb47-7d32-4fb5-9613-b3d0dd6a92e4" />

---
### 3. Dashboard - Upload Data
<img width="1907" height="868" alt="image" src="https://github.com/user-attachments/assets/53823e2c-786f-474b-8502-cd18b48d9cc3" />
<br>
<img width="1918" height="877" alt="image" src="https://github.com/user-attachments/assets/b751e04e-9585-4f89-9a64-14d873f388f8" />

---
### 4. Dashboard — KPI Overview
<img width="1919" height="868" alt="image" src="https://github.com/user-attachments/assets/dce21a86-86e0-46b6-80f5-80da8e37f4c3" />

---
### 5. Alert Produksi Real-time
<img width="1919" height="869" alt="image" src="https://github.com/user-attachments/assets/f1a6a9a7-0c75-43ed-9008-19fc9c00bde7" />

---
### 6. Data Quality Report
<img width="1913" height="882" alt="image" src="https://github.com/user-attachments/assets/55d993a5-e513-482a-b1d6-f95375790ed8" />

---

### 7. Tren Produksi Bulanan
<img width="1913" height="875" alt="image" src="https://github.com/user-attachments/assets/918114e6-8156-4fee-ab7c-d47805927417" />

---

### 8. Profil Musiman & Produksi Tahunan per Estate
<img width="1919" height="885" alt="image" src="https://github.com/user-attachments/assets/9bd22f39-c67e-4737-b7b8-8f481ade1ab1" />

---

### 9. Boxplot Distribusi & Produktivitas per Hektar
<img width="1919" height="889" alt="image" src="https://github.com/user-attachments/assets/359b46ab-38bb-49ad-91b6-b25c7956d5ca" />

---

### 9. Estate Drilldown Modal
<img width="1513" height="168" alt="image" src="https://github.com/user-attachments/assets/efb8d15c-7178-489d-9449-5ed9a0c54604" />
<br>
<img width="1919" height="875" alt="image" src="https://github.com/user-attachments/assets/fec86a6b-f95e-4d5e-a043-bbc7471ca9c8" />

---

### 10. Korelasi & Driver Produksi
<img width="1919" height="882" alt="image" src="https://github.com/user-attachments/assets/b44cac21-4401-4d12-b0fd-edbfacd7e941" />

---
### 11. Performa dan Evaluasi Model Machine Learning
<img width="1919" height="865" alt="image" src="https://github.com/user-attachments/assets/b3ee7790-113b-467c-a7fe-7a52aae81461" />
<br>
<img width="1911" height="877" alt="image" src="https://github.com/user-attachments/assets/b23cd2d0-c4c9-4ee5-9a3e-d3035c7d68d5" />

---

### 12. Feature Importance
<img width="1918" height="889" alt="image" src="https://github.com/user-attachments/assets/55d728dc-c999-4788-87ff-994d7bdbeb3b" />

---

### 13. Forecast 3 Bulan
<img width="1917" height="878" alt="image" src="https://github.com/user-attachments/assets/1a724120-be9e-4748-b989-5a4507b3d757" />
<br>
<img width="1917" height="880" alt="image" src="https://github.com/user-attachments/assets/07742a1f-9b9b-4b2f-94f0-4fb582b02849" />

---

### 14. What-If Scenario Simulator
<img width="1919" height="882" alt="image" src="https://github.com/user-attachments/assets/dc0c4541-e169-43fb-9097-3a1aa8648f9b" />


---

### 15. Analisis Perbandingan YoY
<img width="1913" height="900" alt="image" src="https://github.com/user-attachments/assets/752f895b-62bb-4eba-acd2-2ee10083f39f" />
<br>
<img width="1907" height="876" alt="image" src="https://github.com/user-attachments/assets/db54602e-a309-4820-9f59-a5f54d5963a4" />

---

### 16. Chat with Your Data
<img width="1919" height="884" alt="image" src="https://github.com/user-attachments/assets/a685201c-c435-4239-995c-c003692aa571" />


---

### 17. PDF Annual Report — Cover Page
<img width="800" height="795" alt="image" src="https://github.com/user-attachments/assets/9d91a53b-a105-4b30-88c3-ee874c122d1a" />
---

### 18. PDF Annual Report — Isi Halaman
<img width="786" height="777" alt="image" src="https://github.com/user-attachments/assets/b119ce4e-1f8a-4bcc-a54d-16acf468b409" />


---

### 19. Excel Report
<img width="1284" height="700" alt="image" src="https://github.com/user-attachments/assets/14d0d777-66c2-448e-b856-8207aaa05b05" />
<br>
<img width="1609" height="421" alt="image" src="https://github.com/user-attachments/assets/c7c10c12-2796-4ae4-b296-ce01a88e1f59" />
<br>
<img width="1218" height="706" alt="image" src="https://github.com/user-attachments/assets/308f2985-2629-4b54-a2c6-609360dd3559" />
<br>
<img width="1378" height="336" alt="image" src="https://github.com/user-attachments/assets/b269c6bf-51c3-442d-8342-5603ae622032" />


---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                          │
│                                                                   │
│   Landing Page → Login (JWT) → Upload CSV → Dashboard            │
│   ├── KPI Cards          ├── Alert Engine    ├── DQ Report       │
│   ├── 11 Chart Panels    ├── Estate Modal    ├── ML Table        │
│   ├── Forecast Table     ├── Simulator       ├── Comparative     │
│   └── Chat Window (floating, multi-turn)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │  HTTP REST (JSON / multipart)
                            │  Authorization: Bearer <JWT>
┌───────────────────────────▼─────────────────────────────────────┐
│                    FastAPI Application                            │
│                                                                   │
│  POST /api/auth/login          → JWT Token Generation            │
│  POST /api/analyze             → Core Analytics Pipeline         │
│  POST /api/analyze/comparative → YoY Comparison Engine           │
│  POST /api/predict             → Real-time ML Inference          │
│  GET  /api/estate/{name}       → Per-Estate Drilldown            │
│  POST /api/chat                → AI Conversational Agent         │
│  GET  /api/download/pdf        → PDF Report Generation           │
│  GET  /api/download/excel      → Excel Export                    │
│  GET  /api/download/stats      → Statistics Excel                │
│  GET  /api/download/alerts     → Alert Excel                     │
│  GET  /api/download/forecast   → Forecast Excel                  │
│  GET  /api/health              → Health Check                    │
└────────┬──────────────────────────┬────────────────────────────┘
         │                          │
┌────────▼──────────┐   ┌──────────▼──────────────────────────────┐
│   ML Engine        │   │         NVIDIA NIM API                   │
│                    │   │   Model: Llama 4 Maverick 17B            │
│ ┌────────────────┐ │   │                                          │
│ │LinearRegression│ │   │  10 prompts → ThreadPoolExecutor(6)      │
│ │Random Forest   │ │   │  → paralel → ~10× lebih cepat           │
│ │Gradient Boost  │ │   │                                          │
│ └────────────────┘ │   │  + Chat endpoint (multi-turn, context)   │
│                    │   └──────────────────────────────────────────┘
│ Auto-select best   │
│ by R² score        │   ┌─────────────────────────────────────────┐
│ 5-fold CV eval     │   │        Report Generator                  │
└────────────────────┘   │                                          │
                         │  ReportLab → PDF (cover + 6 sections)    │
                         │  openpyxl  → 5 Excel workbooks           │
                         │  matplotlib + seaborn → 11 PNG charts    │
                         └─────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

### Backend & API

| Teknologi | Versi | Fungsi |
|---|---|---|
| **Python** | 3.10+ | Bahasa utama |
| **FastAPI** | 0.110+ | REST API framework, routing, middleware |
| **uvicorn** | latest | ASGI server |
| **python-jose** | latest | JWT authentication & token validation |
| **httpx** | latest | HTTP client untuk NVIDIA NIM API |

### Machine Learning & Data

| Teknologi | Fungsi |
|---|---|
| **scikit-learn** | Training RF, GB, LR · cross-validation · metrics |
| **pandas** | ETL, feature engineering, aggregasi |
| **numpy** | Komputasi numerik, array operations |

### Visualisasi

| Teknologi | Fungsi |
|---|---|
| **matplotlib** | 11 jenis chart (trend, seasonal, boxplot, scatter, dsb.) |
| **seaborn** | Heatmap korelasi, styling |

### Report Generation

| Teknologi | Fungsi |
|---|---|
| **ReportLab** | PDF Annual Report profesional dengan custom canvas |
| **openpyxl** | 5 workbook Excel berwarna dengan formatting |

### AI / LLM

| Teknologi | Fungsi |
|---|---|
| **NVIDIA NIM** | Inference endpoint LLM |
| **Llama 4 Maverick 17B** | Model bahasa untuk insight & chat |
| **ThreadPoolExecutor** | Paralel 10 LLM calls (6 workers) |

### Frontend

| Teknologi | Fungsi |
|---|---|
| **Vanilla HTML/CSS/JS** | SPA tanpa framework eksternal |
| **CSS Custom Properties** | Dark mode, theming, responsive |
| **Google Fonts** | Plus Jakarta Sans, Fraunces, JetBrains Mono |

### Deployment

| Teknologi | Fungsi |
|---|---|
| **Railway** | Cloud deployment platform |
| **runtime.txt** | Menentukan versi Python di Railway |

---

## 🔄 Alur Pipeline Analisis

Ketika file CSV diupload, sistem menjalankan pipeline berikut secara berurutan:

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1 — Data Quality Assessment                            │
│                                                               │
│  Input: raw DataFrame                                         │
│  ├── Hitung completeness = 1 - (null_cells / total_cells)    │
│  ├── Detect outliers per kolom numerik via IQR method        │
│  ├── Hitung duplikat (exact match)                           │
│  └── Output: skor 0–100 + chart 3 panel                      │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2 — Preprocessing & Feature Engineering                │
│                                                               │
│  ├── Imputasi: median (numerik), modus (kategorikal)         │
│  ├── Drop duplikat, sort by date                             │
│  ├── Tambah: year, month, month_name, quarter                │
│  ├── Hitung: productivity_ton_per_ha, production_per_worker  │
│  ├──         fertilizer_per_ha                               │
│  └── Encode estate → estate_encoded (LabelEncoder)           │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3 — Chart Generation (11 visualisasi, base64 PNG)      │
│                                                               │
│  ├── Tren bulanan + rolling avg 3 bulan                      │
│  ├── Profil musiman (avg per bulan kalender)                 │
│  ├── Stacked bar tahunan per estate                          │
│  ├── Boxplot distribusi per estate                           │
│  ├── Horizontal bar produktivitas/ha                         │
│  ├── Heatmap korelasi Pearson + bar korelasi vs produksi     │
│  ├── Scatter 4 driver produksi                               │
│  ├── Evaluasi model (aktual vs prediksi, residual, hist)     │
│  └── Feature importance horizontal bar                       │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4 — Machine Learning (3 model, train_test_split 80/20) │
│                                                               │
│  Features: area_ha, rainfall, workers, fertilizer,           │
│            month, quarter, estate_encoded                     │
│  Target:   production_tons                                    │
│                                                               │
│  ├── Linear Regression                                        │
│  ├── Random Forest (n_estimators=200, n_jobs=-1)             │
│  ├── Gradient Boosting (n_estimators=200)                    │
│  ├── Evaluasi: R², MAE, RMSE, CV R² (5-fold)                │
│  └── Best model = argmax(R²)                                 │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5 — Forecast 3 Bulan                                   │
│                                                               │
│  Per estate, per horizon h ∈ {1, 2, 3}:                     │
│  ├── Buat feature vector dari data terakhir estate           │
│  ├── Prediksi dengan best_model                              │
│  └── CI: ±MAE × {1.0, 1.5, 2.2}                            │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6 — Alert Engine                                       │
│                                                               │
│  fleet_avg = mean(productivity_ton_per_ha) seluruh dataset   │
│  Per estate:                                                  │
│  ├── ratio < 0.70 → 🔴 Kritis                               │
│  ├── ratio < 0.88 → 🟡 Perhatian                            │
│  └── ratio ≥ 0.88 → 🟢 Normal                               │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7 — AI Insight Generation (paralel)                    │
│                                                               │
│  10 prompts dikirim serentak via ThreadPoolExecutor(6):      │
│  trend, seasonal, annual, boxplot, prodha,                   │
│  correlation, scatter, model, feature_importance, forecast   │
│                                                               │
│  + Build chat context (ringkasan dataset untuk /api/chat)    │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 8 — Comparative YoY (otomatis jika ≥ 2 tahun)         │
│                                                               │
│  Split by year[-2] vs year[-1]                               │
│  → grouped bar + % change + AI insight komparatif           │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
                   Dashboard Siap ✅
          (semua data disimpan di _last dict)
```

---

## 🤖 Model Machine Learning

### Kandidat Model

| Model | Kelebihan | Hyperparameter |
|---|---|---|
| **Linear Regression** | Cepat, interpretable, baseline | Default sklearn |
| **Random Forest** | Robust, handles non-linearity, feature importance | `n_estimators=200, random_state=42, n_jobs=-1` |
| **Gradient Boosting** | Akurasi tinggi, sequential boosting | `n_estimators=200, random_state=42` |

### Seleksi Model

```python
# Kriteria seleksi: R² tertinggi pada test set
best_model = argmax([lr.r2, rf.r2, gb.r2])

# Evaluasi lengkap
metrics = {
    "R²"    : r2_score(y_test, y_pred),
    "MAE"   : mean_absolute_error(y_test, y_pred),
    "RMSE"  : sqrt(mean_squared_error(y_test, y_pred)),
    "CV R²" : cross_val_score(model, X, y, cv=5, scoring="r2").mean()
}
```

### Feature Engineering

| Fitur | Sumber | Keterangan |
|---|---|---|
| `plantation_area_ha` | CSV langsung | Luas lahan aktif |
| `rainfall_mm` | CSV langsung | Curah hujan bulanan |
| `workers` | CSV langsung | Jumlah tenaga kerja |
| `fertilizer_kg` | CSV langsung | Total pupuk |
| `month` | Derived dari `date` | Komponen musiman |
| `quarter` | Derived dari `date` | Komponen kuartalan |
| `estate_encoded` | LabelEncoder | Identitas estate |

---

## 📊 Format Data CSV

### Kolom Wajib

| Kolom | Tipe Data | Format | Contoh |
|---|---|---|---|
| `date` | string | `YYYY-MM-DD` | `2023-01-01` |
| `estate` | string | Nama bebas | `Estate Belitung` |
| `plantation_area_ha` | float | Angka positif | `523.5` |
| `rainfall_mm` | float | Angka ≥ 0 | `187.3` |
| `workers` | integer | Angka positif | `78` |
| `fertilizer_kg` | float | Angka ≥ 0 | `4250.0` |
| `production_tons` | float | Angka positif | `1243.6` |

### Contoh Isi CSV

```csv
date,estate,plantation_area_ha,rainfall_mm,workers,fertilizer_kg,production_tons
2023-01-01,Estate Belitung,523.5,187.3,78,4250.0,1243.6
2023-01-01,Estate Sumatra,410.0,201.5,65,3800.0,987.2
2023-02-01,Estate Belitung,523.5,165.0,80,4100.0,1189.4
2023-02-01,Estate Sumatra,410.0,178.2,67,3750.0,945.8
2024-01-01,Estate Belitung,530.0,195.0,82,4400.0,1310.0
2024-01-01,Estate Sumatra,415.0,210.0,70,3900.0,1020.5
```

### Tips Upload Data

- ✅ **Minimal 2 estate** untuk perbandingan bermakna
- ✅ **Minimal 12 bulan** untuk analisis musiman
- ✅ **2+ tahun** data → comparative YoY muncul otomatis
- ✅ Nilai kosong (`NaN`) ditangani otomatis dengan imputasi median/modus
- ✅ Duplikat dihapus otomatis sebelum analisis
- ❌ Kolom tidak boleh diganti namanya (case-sensitive)

File contoh tersedia di repository: `data_training.csv` dan `data_uji.csv`

---

## 📁 Struktur Proyek

```
portofolio-lonsum/
│
├── 📄 main.py                        # Seluruh aplikasi (backend + frontend)
│   ├── Authentication (JWT)
│   ├── Core pipeline: process_dataset()
│   ├── ML: LinearRegression, RandomForest, GradientBoosting
│   ├── Charts: 11 visualisasi matplotlib/seaborn
│   ├── PDF: build_pdf() via ReportLab
│   ├── Excel: build_excel() via openpyxl
│   ├── AI: ask_llm() + ask_llm_parallel()
│   ├── Chat: /api/chat endpoint
│   └── HTML_PAGE: ~1500 baris SPA frontend
│
├── 📄 requirements.txt               # Dependensi Python
├── 📄 runtime.txt                    # python-3.10.x (untuk Railway)
│
├── 📊 data_training.csv              # Dataset contoh untuk training/demo
├── 📊 data_uji.csv                   # Dataset contoh untuk pengujian
│
├── 📋 Lonsum_AnnualReport.pdf    # Contoh output PDF
├── 📋 Laporan_Lonsum_Alert.xlsx      # Contoh output Excel — Alert
├── 📋 Laporan_Lonsum_Forecast.xlsx   # Contoh output Excel — Forecast
├── 📋 Laporan_Lonsum_Produksi.xlsx   # Contoh output Excel — Produksi
├── 📋 Laporan_Lonsum_Statistik.xlsx  # Contoh output Excel — Statistik
└── 📄 README.md
```

---

## 🚀 Instalasi & Menjalankan di Lokal

### Prasyarat

Pastikan sudah terinstal di komputer Anda:

| Software | Versi Minimum | Cek dengan |
|---|---|---|
| Python | 3.10 | `python --version` |
| pip | terbaru | `pip --version` |
| Git | terbaru | `git --version` |

### Langkah 1 — Clone Repository

```bash
git clone https://github.com/GinantiRiski1/portofolio-lonsum.git
cd portofolio-lonsum
```

### Langkah 2 — Buat Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

> Tanda `(venv)` akan muncul di awal baris terminal jika berhasil.

### Langkah 3 — Install Dependensi

```bash
pip install -r requirements.txt
```

Proses ini menginstal semua library yang diperlukan (FastAPI, scikit-learn, matplotlib, ReportLab, openpyxl, dll). Estimasi waktu: 2–5 menit tergantung koneksi internet.

### Langkah 4 — Jalankan Aplikasi

```bash
python main.py
```

Output yang diharapkan:
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Langkah 5 — Buka Browser

```
http://localhost:8000
```

### Langkah 6 — Login & Upload Data

1. Login dengan akun demo (lihat bagian [Akun Demo](#-akun-demo))
2. Upload file `data_training.csv` yang tersedia di repository
3. Tunggu ±30 detik — dashboard akan muncul otomatis

### Menghentikan Server

```bash
CTRL + C
```

### Troubleshooting

<details>
<summary><b>❌ Error: ModuleNotFoundError</b></summary>

Pastikan virtual environment aktif dan instalasi berhasil:
```bash
# Aktifkan venv terlebih dahulu
venv\Scripts\activate    # Windows
source venv/bin/activate # macOS/Linux

# Install ulang
pip install -r requirements.txt
```
</details>

<details>
<summary><b>❌ Error: Port 8000 already in use</b></summary>

Ganti port di baris terakhir `main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
```
Lalu buka `http://localhost:8001`
</details>

<details>
<summary><b>⚠️ AI Insight tidak muncul (teks fallback)</b></summary>

Fitur AI insight membutuhkan koneksi internet untuk memanggil NVIDIA NIM API. Dashboard tetap berjalan penuh — hanya bagian teks AI insight yang menampilkan pesan fallback. Semua chart, tabel, dan download tetap berfungsi normal.
</details>

<details>
<summary><b>⚠️ Proses lama saat pertama kali upload</b></summary>

Normal — proses pertama kali melibatkan: training 3 model ML, generating 11 chart, dan 10 paralel API calls ke NVIDIA NIM. Estimasi: 25–45 detik tergantung ukuran dataset dan kecepatan koneksi.
</details>

---

## ☁️ Deployment di Railway

### Prasyarat

- Akun [Railway](https://railway.app) (gratis untuk project pertama)
- Repository sudah di-push ke GitHub

### Langkah Deployment

**1. Pastikan file `runtime.txt` berisi:**
```
python-3.10.14
```

**2. Pastikan `requirements.txt` lengkap** (sudah tersedia di repo)

**3. Login ke Railway dan buat project baru:**
- Klik **"New Project"** → **"Deploy from GitHub repo"**
- Pilih repository `portofolio-lonsum`
- Railway akan otomatis mendeteksi Python

**4. Set Start Command di Railway:**
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**5. Deploy** — Railway akan otomatis build dan deploy.

**6. Dapatkan URL** dari tab **"Settings"** → **"Domains"**

### Catatan Penting

- Variabel `PORT` di-inject otomatis oleh Railway, tidak perlu diset manual
- Setiap push ke branch `main` akan otomatis trigger re-deploy
- Free tier Railway: 500 jam/bulan (cukup untuk demo)
- Data bersifat **stateless** (hilang saat restart) — sesuai untuk demo

---

## 🔑 Akun Demo

Tersedia dua level akses bawaan untuk keperluan demo:

| Role | Username | Password | Akses |
|---|---|---|---|
| **Administrator** | `admin` | `lonsum` | Full access — semua fitur & download |
| **Data Analyst** | `analyst` | `lonsum` | Full access — semua fitur & download |

> ⚠️ **Penting untuk production:** Ganti `SECRET_KEY` di `main.py` dengan nilai acak yang kuat, simpan `NVIDIA_API_KEY` di environment variable (bukan hardcode), dan gunakan database untuk manajemen user.

---

## 📦 Output yang Dihasilkan

### PDF Annual Report

File PDF profesional dengan:

| Seksi | Konten |
|---|---|
| **Cover Page** | Desain gelap, logo, statistik ringkas, periode, model terbaik |
| **1. Ringkasan Eksekutif** | Tabel KPI, tabel alert per estate |
| **2. Tren & Pola** | Chart tren bulanan, chart musiman + AI insight |
| **3. Perbandingan Estate** | Chart tahunan per estate, chart produktivitas/ha + AI insight |
| **4. Analisis Faktor** | Heatmap korelasi + AI insight |
| **5. Model ML** | Tabel evaluasi 3 model + chart evaluasi + AI insight |
| **6. Forecast** | Chart forecast + tabel + AI insight |

### Excel Reports

| File | Sheet | Konten |
|---|---|---|
| `Lonsum_ProduksiBulanan.xlsx` | 1 sheet | Seluruh data produksi terformat dengan header berwarna |
| `Lonsum_StatistikEstate.xlsx` | 1 sheet | Total, avg, min, max, std, prod/ha, hujan, pekerja per estate |
| `Lonsum_AlertProduktivitas.xlsx` | 1 sheet | Record di bawah threshold 75% fleet avg, highlight merah jika deficit >40% |
| `Lonsum_Forecast3Bulan.xlsx` | 1 sheet | Prediksi +1/+2/+3 bulan per estate dengan % tren |

---

## 📋 Changelog v5.0

### 🐛 Bug Fixes & Performance

| ID | Deskripsi | Dampak |
|---|---|---|
| FIX-1 | `setup_mpl()` dipanggil sekali saat module load | Eliminasi 4× overhead per upload |
| FIX-2 | LLM calls paralel via `ThreadPoolExecutor(6)` | Insight generation ~10× lebih cepat |
| FIX-3 | `insight_box` PDF: 2 kolom → 1 kolom 2 baris | Fix crash `ReportLab colWidths mismatch` |
| FIX-4 | `CoverPage` inherit `_Flowable` + `draw()/self.canv` | Fix halaman cover PDF kosong |
| FIX-5 | Helper `_bar_labels()` & `_barh_labels()` | Eliminasi copy-paste `ax.text()` di 8 chart |
| FIX-6 | Excel helpers `_hdr()` & `_drow()` | Kode Excel 40% lebih ringkas |
| FIX-7 | CSS variables + konsolidasi class | File HTML ~18KB lebih kecil |
| FIX-8 | `_last` simpan `best_model` string langsung | Eliminasi lookup redundan |

### ✨ Fitur Baru

| ID | Fitur | Deskripsi |
|---|---|---|
| NEW-9 | **Chat with Your Data** | Floating chat multi-turn, konteks dataset penuh, NVIDIA NIM |
| NEW-10 | **Dark Topbar** | Header profesional gelap (sebelumnya putih) |
| NEW-11 | **Bar Labels Semua Chart** | Nilai tampil di atas/samping semua bar di seluruh dashboard |
| NEW-12 | **Toast Notification** | Notifikasi centered-bottom untuk feedback aksi |
| NEW-13 | **Sidebar Badge Auto-hide** | Badge "NEW" hilang setelah data berhasil dimuat |

---

## 👩‍💻 Tentang Pembuat

<div align="center">

<!-- Ganti dengan foto GitHub kamu -->
<!-- <img src="https://github.com/GinantiRiski1.png" width="130" style="border-radius:50%"/> -->

### Ginanti Riski
**Deep Learning & NLP Practitioner**

</div>

Seorang praktisi **Deep Learning dan Natural Language Processing** yang juga membangun
sistem analitik full-stack berbasis data. Proyek **Lonsum LEAP v5.0** ini membuktikan
kemampuan mengintegrasikan **machine learning klasik, LLM generatif (NVIDIA NIM / Llama 4)**,
dan **pengembangan web production-ready** dalam satu pipeline end-to-end.

Ketertarikan utama meliputi: arsitektur model deep learning, aplikasi NLP di dunia industri,
dan membangun sistem AI yang tidak hanya akurat secara teknis — tetapi juga dapat digunakan
langsung oleh pengguna bisnis non-teknis.


<div align="center">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Ginanti_Riski-0A66C2?style=for-the-badge&logo=linkedin)](https://id.linkedin.com/in/ginanti-riski-483b7a362)
[![GitHub](https://img.shields.io/badge/GitHub-GinantiRiski1-181717?style=for-the-badge&logo=github)](https://github.com/GinantiRiski1)
[![Email](https://img.shields.io/badge/Email-Hubungi_Saya-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:ginantiriski@gmail.com)

</div>
## 📄 Lisensi

```
MIT License

Copyright (c) 2024 Ginanti Riski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.
```

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=1a6b3c&height=120&section=footer&text=PT%20London%20Sumatra%20Indonesia%20%C2%B7%20LEAP%20v5.0&fontSize=14&fontColor=c9a84c&fontAlignY=65" width="100%"/>

**Jika proyek ini bermanfaat, pertimbangkan untuk memberi ⭐ di repository ini.**

*"From raw CSV to boardroom-ready intelligence — in 30 seconds."*

</div>
