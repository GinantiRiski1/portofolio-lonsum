"""
Lonsum LEAP — Plantation Intelligence Platform v4.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEW in v4.0:
  1. PDF Annual Report One-Click  (ReportLab — cover page + 6 sections + charts)
  2. Comparative Period Analysis  (2 CSV upload OR auto-split by year)
  3. Alert Banner Real-time       (🔴 Kritis / 🟡 Perlu Perhatian / 🟢 Normal per estate)
  4. Multi-Month Forecast         (3 bulan ke depan dengan widening confidence interval)
  5. Estate Detail Drilldown      (modal per estate — tren, ranking, faktor dominan)
  6. What-If Simulator            (input manual → prediksi ML real-time)
  7. Data Quality Score           (completeness, outlier %, duplikat — gauge chart)
  8. Export Chart PNG             (tombol download di setiap chart card)
"""

import io, base64, json, warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import httpx
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                 Table, TableStyle, Image as RLImage, HRFlowable,
                                 KeepTogether)
from reportlab.pdfgen import canvas as rl_canvas

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse, StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware

warnings.filterwarnings("ignore")

# ── Credentials ──────────────────────────────────────────────────────────────
NVIDIA_API_KEY  = "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"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL    = "meta/llama-4-maverick-17b-128e-instruct"

# ── Color palette ─────────────────────────────────────────────────────────────
C_DARK   = "#0a1628"; C_NAVY   = "#0d2137"; C_GREEN  = "#1a6b3c"
C_TEAL   = "#0e7c6e"; C_GOLD   = "#c9a84c"; C_LIME   = "#3dba6f"
C_RED    = "#d64045"; C_ORANGE = "#e07b39"; C_LIGHT  = "#e8f5ee"
C_GRAY   = "#94a3b8"
PALETTE  = [C_GREEN, C_TEAL, C_GOLD, C_LIME, C_ORANGE, C_RED, "#457b9d", "#7b5ea7"]

app = FastAPI(title="Lonsum LEAP v4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_last_result: dict = {}   # primary dataset result
_comp_result: dict = {}   # comparative analysis result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HTML PAGE  (single-file frontend)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Lonsum LEAP v4.0 — Plantation Intelligence Platform</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,300&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --navy:#0d2137;--dark:#0a1628;--green:#1a6b3c;--teal:#0e7c6e;
  --gold:#c9a84c;--lime:#3dba6f;--red:#d64045;--orange:#e07b39;
  --light:#e8f5ee;--bg:#f2f5f9;--card:#ffffff;
  --border:#dde3ec;--text:#18243a;--muted:#637289;
  --sidebar-w:260px;
  --shadow-xs:0 1px 3px rgba(0,0,0,.06);
  --shadow-sm:0 2px 8px rgba(13,33,55,.08);
  --shadow:0 4px 20px rgba(13,33,55,.11);
  --shadow-lg:0 12px 48px rgba(13,33,55,.16);
  --radius:10px;--radius-lg:14px;--radius-xl:18px;
}
html{scroll-behavior:smooth}
body{font-family:'Plus Jakarta Sans',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;-webkit-font-smoothing:antialiased}

/* ══ LANDING ══════════════════════════════════════════════════ */
#landing{position:fixed;inset:0;z-index:9999;overflow-y:auto;background:var(--dark)}
#landing.exit{animation:lpOut .6s cubic-bezier(.4,0,.2,1) forwards;pointer-events:none}
@keyframes lpOut{to{opacity:0;transform:scale(1.04)}}
.lp-bg{position:fixed;inset:0;pointer-events:none;z-index:0}
.lp-bg::before{content:'';position:absolute;inset:-40%;
  background:radial-gradient(ellipse 65% 55% at 18% 28%,rgba(26,107,60,.38) 0%,transparent 60%),
    radial-gradient(ellipse 55% 65% at 82% 72%,rgba(14,124,110,.28) 0%,transparent 60%),
    radial-gradient(ellipse 45% 40% at 65% 18%,rgba(201,168,76,.14) 0%,transparent 55%);
  animation:meshMove 20s ease-in-out infinite alternate}
@keyframes meshMove{0%{transform:translate(0,0)}100%{transform:translate(3%,2.5%)}}
.lp-grid-bg{position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);
  background-size:52px 52px}
.lp-orb{position:fixed;border-radius:50%;pointer-events:none;z-index:0;filter:blur(70px)}
.lp-orb1{width:420px;height:420px;background:rgba(26,107,60,.22);top:-100px;left:-80px}
.lp-orb2{width:320px;height:320px;background:rgba(14,124,110,.2);bottom:5%;right:-60px}
.lp-orb3{width:220px;height:220px;background:rgba(201,168,76,.1);top:38%;left:58%}
.lp-wrap{position:relative;z-index:10;min-height:100vh;display:flex;flex-direction:column}
.lp-topbar{display:flex;align-items:center;justify-content:space-between;padding:1.4rem 3rem;border-bottom:1px solid rgba(255,255,255,.06);flex-shrink:0}
.lp-brand{display:flex;align-items:center;gap:13px}
.lp-brand-icon{width:44px;height:44px;border-radius:12px;overflow:hidden;flex-shrink:0;background:linear-gradient(135deg,#1a6b3c,#0e7c6e);display:flex;align-items:center;justify-content:center;box-shadow:0 4px 20px rgba(26,107,60,.5)}
.lp-brand-txt h1{font-family:'Fraunces',serif;font-size:1rem;font-weight:600;color:#fff;letter-spacing:-.01em}
.lp-brand-txt p{font-size:.58rem;color:var(--gold);font-weight:700;text-transform:uppercase;letter-spacing:.16em;margin-top:1px}
.lp-topbar-right{display:flex;align-items:center;gap:.6rem}
.lp-pill{font-size:.63rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;padding:5px 13px;border-radius:20px}
.lp-pill.neutral{color:rgba(255,255,255,.4);border:1px solid rgba(255,255,255,.1)}
.lp-pill.gold{color:var(--gold);border:1px solid rgba(201,168,76,.3);background:rgba(201,168,76,.07)}
.lp-main{flex:1;display:flex;flex-direction:column;align-items:center;padding:4rem 2rem 3rem}
.lp-eyebrow{display:inline-flex;align-items:center;gap:9px;background:rgba(26,107,60,.18);border:1px solid rgba(26,107,60,.38);color:var(--lime);font-size:.7rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:6px 18px;border-radius:20px;margin-bottom:2rem;animation:floatUp .7s .05s both}
.lp-dot{width:7px;height:7px;border-radius:50%;background:var(--lime);animation:blink 2s infinite;flex-shrink:0}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
@keyframes floatUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
.lp-title{font-family:'Fraunces',serif;font-size:clamp(2.8rem,6vw,5.2rem);font-weight:600;color:#fff;letter-spacing:-.04em;line-height:1.07;text-align:center;margin-bottom:.8rem;animation:floatUp .7s .12s both}
.lp-title-accent{background:linear-gradient(130deg,var(--gold) 0%,var(--lime) 65%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.lp-title-italic{font-style:italic;font-weight:300;color:rgba(255,255,255,.65)}
.lp-tagline{font-size:clamp(.88rem,1.8vw,1.05rem);color:rgba(255,255,255,.48);max-width:560px;text-align:center;line-height:1.82;margin-bottom:2.8rem;animation:floatUp .7s .2s both}
.lp-tagline strong{color:rgba(255,255,255,.8);font-weight:600}
.lp-cta-wrap{animation:floatUp .7s .28s both;margin-bottom:3.5rem}
.btn-mulai{background:linear-gradient(135deg,#1a6b3c,#0e7c6e);color:#fff;padding:16px 48px;border-radius:12px;font-size:.98rem;font-weight:700;border:none;cursor:pointer;font-family:'Plus Jakarta Sans',sans-serif;letter-spacing:.02em;position:relative;overflow:hidden;box-shadow:0 8px 32px rgba(26,107,60,.5);transition:all .25s;display:inline-flex;align-items:center;gap:10px}
.btn-mulai:hover{transform:translateY(-3px);box-shadow:0 14px 44px rgba(26,107,60,.62)}
.bm-arrow{transition:transform .2s;font-size:1.1rem}
.btn-mulai:hover .bm-arrow{transform:translateX(5px)}
.lp-features{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;width:100%;max-width:960px;margin-bottom:2.5rem;animation:floatUp .7s .35s both}
@media(max-width:760px){.lp-features{grid-template-columns:repeat(2,1fr)}}
.lp-feat{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:1.2rem 1.1rem;transition:all .22s}
.lp-feat:hover{background:rgba(255,255,255,.07);border-color:rgba(255,255,255,.15);transform:translateY(-3px)}
.lf-icon{font-size:1.4rem;margin-bottom:.6rem}
.lf-title{font-size:.8rem;font-weight:700;color:#fff;margin-bottom:.25rem}
.lf-desc{font-size:.7rem;color:rgba(255,255,255,.38);line-height:1.65}
.lf-new{display:inline-block;font-size:.55rem;font-weight:800;text-transform:uppercase;letter-spacing:.1em;background:rgba(201,168,76,.2);color:var(--gold);border:1px solid rgba(201,168,76,.4);padding:2px 7px;border-radius:20px;margin-left:5px;vertical-align:middle}
.lp-howto{width:100%;max-width:860px;margin-bottom:1.8rem;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:1.8rem 2rem;animation:floatUp .7s .41s both}
.lp-sec-lbl{font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.15em;color:var(--gold);margin-bottom:1.2rem;display:flex;align-items:center;gap:8px}
.lp-sec-lbl::before{content:'';display:inline-block;width:16px;height:2px;background:var(--gold);border-radius:1px}
.lp-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:1.2rem}
@media(max-width:580px){.lp-steps{grid-template-columns:repeat(2,1fr)}}
.lp-step{position:relative}
.lp-step:not(:last-child)::after{content:'→';position:absolute;right:-.7rem;top:.2rem;color:rgba(255,255,255,.1);font-size:.8rem}
@media(max-width:580px){.lp-step:not(:last-child)::after{display:none}}
.step-num{width:30px;height:30px;border-radius:9px;margin-bottom:.55rem;background:linear-gradient(135deg,var(--green),var(--teal));display:inline-flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:800;color:#fff}
.step-title{font-size:.78rem;font-weight:700;color:rgba(255,255,255,.85);margin-bottom:.22rem}
.step-desc{font-size:.68rem;color:rgba(255,255,255,.37);line-height:1.6}
.lp-format{width:100%;max-width:860px;margin-bottom:1.8rem;animation:floatUp .7s .46s both}
.lp-format-inner{background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.2);border-radius:14px;padding:1.1rem 1.7rem}
.lp-cols{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:.65rem}
.lp-col-chip{display:flex;align-items:center;gap:7px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:.38rem .85rem}
.lp-col-chip code{font-family:'JetBrains Mono',monospace;font-size:.67rem;color:var(--lime)}
.lp-col-chip span{font-size:.63rem;color:rgba(255,255,255,.28)}
.lp-footer{border-top:1px solid rgba(255,255,255,.06);padding:1rem 3rem;flex-shrink:0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem}
.lp-footer p{font-size:.67rem;color:rgba(255,255,255,.22)}
.lp-footer strong{color:rgba(255,255,255,.45)}
.lp-stack-row{display:flex;gap:.4rem;flex-wrap:wrap}
.lp-stag{font-family:'JetBrains Mono',monospace;font-size:.58rem;color:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.07);padding:3px 8px;border-radius:20px}

/* ══ SIDEBAR ═══════════════════════════════════════════════════ */
#sidebar{width:var(--sidebar-w);min-height:100vh;flex-shrink:0;background:var(--dark);display:flex;flex-direction:column;position:fixed;top:0;left:0;bottom:0;z-index:300;border-right:1px solid rgba(255,255,255,.06);transition:transform .3s cubic-bezier(.4,0,.2,1);overflow:hidden}
.sb-top{padding:1.5rem 1.4rem 1.2rem;border-bottom:1px solid rgba(255,255,255,.07)}
.sb-logo{display:flex;align-items:center;gap:12px;margin-bottom:1.1rem}
.sb-logo-img{width:42px;height:42px;border-radius:10px;overflow:hidden;flex-shrink:0;background:linear-gradient(135deg,var(--green),var(--teal));display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(26,107,60,.45)}
.sb-brand h1{font-family:'Fraunces',serif;font-size:1.1rem;font-weight:600;color:#fff;letter-spacing:-.01em}
.sb-brand p{font-size:.62rem;color:var(--gold);font-weight:600;text-transform:uppercase;letter-spacing:.13em;margin-top:2px}
.sb-meta{display:flex;flex-direction:column;gap:4px}
.sb-meta-item{font-size:.7rem;color:rgba(255,255,255,.4);display:flex;align-items:center;gap:6px}
.sb-meta-item span:first-child{color:rgba(255,255,255,.2)}
.sb-nav{flex:1;padding:1.2rem .8rem;overflow-y:auto;scrollbar-width:none}
.sb-nav::-webkit-scrollbar{display:none}
.sb-section{margin-bottom:1.4rem}
.sb-section-label{font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:rgba(255,255,255,.25);padding:.2rem .7rem .5rem;display:block}
.sb-item{display:flex;align-items:center;gap:10px;width:100%;padding:.65rem .85rem;border-radius:var(--radius);color:rgba(255,255,255,.55);font-size:.8rem;font-weight:500;cursor:pointer;border:none;background:transparent;text-align:left;transition:all .18s;position:relative;font-family:'Plus Jakarta Sans',sans-serif}
.sb-item:hover{background:rgba(255,255,255,.06);color:rgba(255,255,255,.9)}
.sb-item.active{background:rgba(26,107,60,.25);color:#fff;border-left:3px solid var(--lime)}
.sb-item.active .sb-icon{color:var(--lime)}
.sb-icon{font-size:1rem;width:20px;text-align:center;flex-shrink:0}
.sb-item .badge{margin-left:auto;font-size:.58rem;background:rgba(201,168,76,.2);color:var(--gold);padding:2px 7px;border-radius:20px;font-weight:700}
.sb-item .badge-new{margin-left:auto;font-size:.55rem;background:rgba(61,186,111,.2);color:var(--lime);padding:2px 7px;border-radius:20px;font-weight:800;text-transform:uppercase;letter-spacing:.05em}
.sb-bottom{padding:1rem .8rem 1.4rem;border-top:1px solid rgba(255,255,255,.07)}
#clock-sb{font-family:'JetBrains Mono',monospace;font-size:.65rem;color:rgba(255,255,255,.3);text-align:center;padding:.5rem}
.sb-version{font-size:.6rem;color:rgba(255,255,255,.2);text-align:center;margin-top:4px}

/* ══ MAIN ═══════════════════════════════════════════════════════ */
#main-wrap{margin-left:var(--sidebar-w);flex:1;min-height:100vh;display:flex;flex-direction:column}
#topbar{background:#fff;border-bottom:1px solid var(--border);height:62px;display:flex;align-items:center;justify-content:space-between;padding:0 2rem;position:sticky;top:0;z-index:100;box-shadow:var(--shadow-xs)}
.tb-left{display:flex;align-items:center;gap:1rem}
.tb-left h2{font-family:'Fraunces',serif;font-size:1.2rem;font-weight:600;color:var(--dark);letter-spacing:-.01em}
.tb-breadcrumb{font-size:.75rem;color:var(--muted)}
.tb-right{display:flex;align-items:center;gap:.7rem}
.badge-ai{background:linear-gradient(135deg,var(--gold),#e8c45a);color:var(--dark);font-size:.65rem;font-weight:700;padding:4px 12px;border-radius:20px;letter-spacing:.04em;text-transform:uppercase}
.btn-sm{background:transparent;border:1px solid var(--border);color:var(--muted);padding:6px 14px;border-radius:var(--radius);font-size:.76rem;cursor:pointer;font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;transition:all .2s;display:none}
.btn-sm:hover{background:var(--bg);color:var(--dark)}
#content{flex:1;padding:2rem 2rem 4rem}

/* ══ UPLOAD ═════════════════════════════════════════════════════ */
#upload-section{max-width:800px;margin:3rem auto 0}
.upload-tabs{display:flex;gap:.5rem;margin-bottom:1.5rem}
.upload-tab{padding:9px 20px;border-radius:var(--radius);font-size:.8rem;font-weight:700;cursor:pointer;border:1px solid var(--border);background:#fff;color:var(--muted);transition:all .2s;font-family:'Plus Jakarta Sans',sans-serif}
.upload-tab.active{background:var(--dark);color:#fff;border-color:var(--dark)}
.upload-pane{display:none}
.upload-pane.active{display:block}
.upload-card{background:#fff;border:2px dashed var(--border);border-radius:var(--radius-xl);padding:3rem 2.5rem;text-align:center;cursor:pointer;transition:all .25s;box-shadow:var(--shadow-sm)}
.upload-card:hover,.upload-card.dragover{border-color:var(--green);border-style:solid;background:var(--light);box-shadow:var(--shadow);transform:translateY(-3px)}
.up-icon{font-size:3rem;margin-bottom:1rem}
.upload-card h2{font-family:'Fraunces',serif;font-size:1.5rem;font-weight:600;color:var(--dark);margin-bottom:.5rem}
.upload-card p{color:var(--muted);font-size:.85rem;line-height:1.7}
.col-hint{display:flex;flex-wrap:wrap;justify-content:center;gap:6px;margin-top:1rem}
.col-hint code{font-family:'JetBrains Mono',monospace;font-size:.7rem;background:var(--light);color:var(--green);padding:4px 10px;border-radius:6px;border:1px solid rgba(26,107,60,.2)}
#file-input,#file-input-a,#file-input-b{display:none}
.btn-primary{background:linear-gradient(135deg,var(--green),var(--teal));color:#fff;padding:12px 32px;border-radius:var(--radius);margin-top:1.5rem;font-weight:700;font-size:.88rem;cursor:pointer;border:none;font-family:'Plus Jakarta Sans',sans-serif;letter-spacing:.02em;box-shadow:0 4px 18px rgba(26,107,60,.3);transition:all .2s;display:inline-flex;align-items:center;gap:8px}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 6px 24px rgba(26,107,60,.4)}
.btn-primary:disabled{opacity:.5;pointer-events:none}
.err-banner{background:#fff5f5;border:1px solid #fecaca;border-radius:var(--radius);padding:12px 16px;margin-bottom:16px;color:var(--red);font-size:.85rem;display:flex;align-items:center;gap:8px}
.comp-pair{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem}
.comp-slot{background:var(--bg);border:2px dashed var(--border);border-radius:var(--radius-lg);padding:1.2rem;text-align:center;cursor:pointer;transition:all .2s}
.comp-slot:hover{border-color:var(--green)}
.comp-slot.filled{border-color:var(--green);border-style:solid;background:var(--light)}
.comp-slot-icon{font-size:1.8rem;margin-bottom:.4rem}
.comp-slot-label{font-size:.75rem;font-weight:700;color:var(--dark);margin-bottom:.2rem}
.comp-slot-file{font-size:.7rem;color:var(--green);font-weight:600}

/* ══ LOADING ════════════════════════════════════════════════════ */
#loading{display:none;flex-direction:column;align-items:center;padding:5rem 2rem;gap:1.5rem}
.spinner-wrap{position:relative;width:72px;height:72px}
.spinner{width:72px;height:72px;border:3px solid var(--border);border-top-color:var(--green);border-radius:50%;animation:spin .8s linear infinite}
.spinner-inner{position:absolute;top:12px;left:12px;width:48px;height:48px;border:3px solid transparent;border-top-color:var(--gold);border-radius:50%;animation:spin 1.2s linear infinite reverse}
@keyframes spin{to{transform:rotate(360deg)}}
#load-msg{font-family:'Fraunces',serif;font-size:1.2rem;color:var(--dark);text-align:center}
.progress-bar{width:320px;height:5px;background:var(--border);border-radius:3px;overflow:hidden}
.progress-fill{height:100%;background:linear-gradient(90deg,var(--green),var(--gold));border-radius:3px;animation:progress 28s ease-out forwards}
@keyframes progress{0%{width:2%}50%{width:60%}90%{width:88%}100%{width:95%}}
.load-steps{display:flex;flex-direction:column;gap:4px;width:340px}
.ls{font-size:.78rem;color:var(--muted);padding:6px 12px;border-radius:8px;transition:all .3s;display:flex;align-items:center;gap:8px}
.ls.active{color:var(--green);background:var(--light);font-weight:700}
.ls.done{color:#aab4c0;text-decoration:line-through}
.ls .dot{width:6px;height:6px;border-radius:50%;background:currentColor;flex-shrink:0}

/* ══ DASHBOARD ══════════════════════════════════════════════════ */
#dashboard{display:none;animation:fadeUp .45s ease}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}

/* ── Alert Banners ── */
#alert-banner-section{margin-bottom:1.5rem;display:none}
.alert-strip{border-radius:var(--radius-lg);padding:.9rem 1.2rem;margin-bottom:.6rem;display:flex;align-items:flex-start;gap:12px;border:1px solid}
.alert-strip.crit{background:#fff1f1;border-color:#fecaca;color:#991b1b}
.alert-strip.warn{background:#fffbeb;border-color:#fde68a;color:#92400e}
.alert-strip.ok{background:#f0fdf4;border-color:#bbf7d0;color:#166534}
.alert-strip-icon{font-size:1.2rem;flex-shrink:0;margin-top:1px}
.alert-strip-body h4{font-size:.82rem;font-weight:700;margin-bottom:2px}
.alert-strip-body p{font-size:.76rem;line-height:1.6}

.page-header{margin-bottom:1.8rem}
.page-header .ph-label{font-size:.65rem;font-weight:700;color:var(--gold);text-transform:uppercase;letter-spacing:.14em;margin-bottom:.3rem}
.page-header h2{font-family:'Fraunces',serif;font-size:1.7rem;font-weight:600;color:var(--dark);line-height:1.2}
.page-header p{color:var(--muted);font-size:.84rem;margin-top:.3rem}

/* ── Data Quality Gauge ── */
.dq-row{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.8rem}
.dq-card{background:#fff;border-radius:var(--radius-lg);padding:1.1rem;border:1px solid var(--border);box-shadow:var(--shadow-xs);text-align:center}
.dq-score{font-family:'Fraunces',serif;font-size:2rem;font-weight:600;line-height:1}
.dq-label{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin-top:.3rem}
.dq-bar-track{height:5px;background:var(--light);border-radius:3px;margin-top:.5rem;overflow:hidden}
.dq-bar-fill{height:100%;border-radius:3px;transition:width 1s ease}

.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.8rem}
@media(max-width:1200px){.kpi-grid{grid-template-columns:repeat(2,1fr)}}
.kpi{background:#fff;border-radius:var(--radius-lg);padding:1.4rem 1.3rem 1.2rem;box-shadow:var(--shadow-xs);border:1px solid var(--border);position:relative;overflow:hidden;transition:all .22s}
.kpi:hover{box-shadow:var(--shadow);transform:translateY(-2px)}
.kpi-accent{position:absolute;top:0;left:0;right:0;height:4px;border-radius:var(--radius-lg) var(--radius-lg) 0 0}
.kpi-accent.g{background:linear-gradient(90deg,var(--green),var(--teal))}
.kpi-accent.gold{background:linear-gradient(90deg,var(--gold),#e8c45a)}
.kpi-accent.teal{background:linear-gradient(90deg,var(--teal),var(--lime))}
.kpi-accent.red{background:linear-gradient(90deg,var(--orange),var(--red))}
.kpi-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:.7rem;margin-top:.2rem}
.kpi-icon-wrap{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;background:var(--light)}
.kpi-change{font-size:.68rem;font-weight:700;padding:3px 8px;border-radius:20px}
.kpi-change.pos{background:#dcfce7;color:#16a34a}
.kpi-change.neg{background:#fee2e2;color:#dc2626}
.kpi-change.neu{background:#f1f5f9;color:var(--muted)}
.kpi-val{font-family:'Fraunces',serif;font-size:1.9rem;font-weight:600;color:var(--dark);line-height:1;margin-bottom:.3rem}
.kpi-label{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.kpi-sub{font-size:.72rem;color:var(--muted);margin-top:.2rem}

.section-sep{margin:2.2rem 0 1.4rem;display:flex;align-items:center;gap:12px}
.section-sep .sl{font-size:.63rem;font-weight:700;color:var(--gold);text-transform:uppercase;letter-spacing:.14em;white-space:nowrap}
.section-sep .line{flex:1;height:1px;background:var(--border)}

/* ── Download Bar ── */
.dl-bar{background:var(--dark);border-radius:var(--radius-lg);padding:1.3rem 1.6rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.8rem;margin-bottom:1.8rem;box-shadow:var(--shadow)}
.dl-bar-left{display:flex;align-items:center;gap:14px}
.dl-bar-left .icon{font-size:1.5rem}
.dl-bar-left h3{font-size:.92rem;font-weight:700;color:#fff}
.dl-bar-left p{font-size:.73rem;color:rgba(255,255,255,.45);margin-top:1px}
.dl-btns{display:flex;gap:.6rem;flex-wrap:wrap}
.dl-btn{display:flex;align-items:center;gap:7px;padding:8px 15px;border-radius:var(--radius);font-size:.75rem;font-weight:700;cursor:pointer;border:none;font-family:'Plus Jakarta Sans',sans-serif;transition:all .2s;text-decoration:none}
.dl-btn:hover{transform:translateY(-1px);filter:brightness(1.08)}
.dl-excel{background:linear-gradient(135deg,#1a6b3c,#0e7c6e);color:#fff}
.dl-stats{background:linear-gradient(135deg,#c9a84c,#e8c45a);color:var(--dark)}
.dl-alert{background:linear-gradient(135deg,#d64045,#e07b39);color:#fff}
.dl-forecast{background:linear-gradient(135deg,#457b9d,#7b5ea7);color:#fff}
.dl-pdf{background:linear-gradient(135deg,#0a1628,#0d2137);color:#fff;border:1px solid rgba(255,255,255,.15)}

/* ── Chart Cards ── */
.ana-card{background:#fff;border-radius:var(--radius-xl);border:1px solid var(--border);box-shadow:var(--shadow-xs);overflow:hidden;transition:box-shadow .2s;margin-bottom:1.2rem}
.ana-card:hover{box-shadow:var(--shadow-sm)}
.ac-header{display:flex;align-items:center;justify-content:space-between;padding:1rem 1.4rem .8rem;border-bottom:1px solid var(--border)}
.ac-header-left{display:flex;align-items:center;gap:10px}
.ac-icon{font-size:1.1rem}
.ac-header h3{font-size:.9rem;font-weight:700;color:var(--dark)}
.ac-header p{font-size:.72rem;color:var(--muted);margin-top:1px}
.ac-header-right{display:flex;align-items:center;gap:.5rem}
.ac-tag{font-size:.62rem;background:var(--light);color:var(--green);padding:3px 10px;border-radius:20px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;white-space:nowrap}
.btn-dl-chart{background:transparent;border:1px solid var(--border);color:var(--muted);padding:4px 10px;border-radius:8px;font-size:.65rem;font-weight:700;cursor:pointer;font-family:'Plus Jakarta Sans',sans-serif;transition:all .2s;display:flex;align-items:center;gap:4px}
.btn-dl-chart:hover{background:var(--light);color:var(--green);border-color:var(--green)}
.ac-chart{width:100%;display:block;padding:.6rem .6rem .2rem}
.chart-ph{min-height:200px;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:.8rem;flex-direction:column;gap:.5rem;padding:2rem}
.chart-ph .phi{font-size:2rem;opacity:.3}
.ac-insight{margin:.2rem 1rem 1rem;background:linear-gradient(135deg,#f3fbf6,#edf7f2);border:1px solid rgba(26,107,60,.13);border-radius:var(--radius);padding:1rem 1.2rem}
.ac-insight-hdr{display:flex;align-items:center;gap:8px;margin-bottom:.6rem}
.ai-pill{font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--green);background:rgba(26,107,60,.1);padding:3px 10px;border-radius:20px;display:inline-flex;align-items:center;gap:4px}
.ac-insight p{font-size:.82rem;color:#253b2d;line-height:1.8;white-space:pre-wrap}

.cgrid-2{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem}
@media(max-width:1100px){.cgrid-2{grid-template-columns:1fr}}

/* ── Model Table ── */
.model-table-wrap{background:#fff;border-radius:var(--radius-xl);border:1px solid var(--border);box-shadow:var(--shadow-xs);overflow:hidden;margin-bottom:1.2rem}
.model-table-wrap table{width:100%;border-collapse:collapse;font-size:.83rem}
.model-table-wrap thead{background:var(--dark)}
.model-table-wrap thead th{padding:.85rem 1.2rem;text-align:left;font-size:.67rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,.65)}
.model-table-wrap tbody tr{border-bottom:1px solid var(--border);transition:background .15s}
.model-table-wrap tbody tr:last-child{border:none}
.model-table-wrap tbody tr:hover{background:#f8fbff}
.model-table-wrap tbody td{padding:.8rem 1.2rem;color:var(--text)}
.badge-best{background:linear-gradient(135deg,var(--green),var(--teal));color:#fff;font-size:.6rem;padding:2px 9px;border-radius:20px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;margin-left:8px}
.r2bar{display:flex;align-items:center;gap:10px}
.r2track{height:6px;width:80px;background:var(--light);border-radius:3px;overflow:hidden;flex-shrink:0}
.r2fill{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--teal),var(--green))}

/* ── Forecast ── */
.forecast-table-wrap{background:#fff;border-radius:var(--radius-xl);border:1px solid var(--border);box-shadow:var(--shadow-xs);overflow:hidden;margin-bottom:.8rem}
.forecast-table-wrap table{width:100%;border-collapse:collapse;font-size:.83rem}
.forecast-table-wrap thead{background:linear-gradient(135deg,#1a6b3c,#0e7c6e)}
.forecast-table-wrap thead th{padding:.8rem 1.1rem;text-align:left;font-size:.67rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,.8)}
.forecast-table-wrap tbody tr{border-bottom:1px solid var(--border);transition:background .15s}
.forecast-table-wrap tbody tr:last-child{border:none}
.forecast-table-wrap tbody tr:hover{background:#f0faf5}
.forecast-table-wrap tbody td{padding:.75rem 1.1rem;color:var(--text)}
.chg-pos{color:#16a34a;font-weight:700}
.chg-neg{color:var(--red);font-weight:700}

/* ── What-If Simulator ── */
#sec-simulator{margin-bottom:2rem}
.simulator-card{background:#fff;border-radius:var(--radius-xl);border:1px solid var(--border);box-shadow:var(--shadow-xs);overflow:hidden}
.sim-body{padding:1.5rem}
.sim-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.2rem}
@media(max-width:900px){.sim-grid{grid-template-columns:repeat(2,1fr)}}
.sim-field{display:flex;flex-direction:column;gap:5px}
.sim-field label{font-size:.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.07em}
.sim-field input,.sim-field select{border:1px solid var(--border);border-radius:var(--radius);padding:9px 12px;font-size:.88rem;font-family:'Plus Jakarta Sans',sans-serif;color:var(--text);background:#fff;transition:border-color .2s;outline:none}
.sim-field input:focus,.sim-field select:focus{border-color:var(--green);box-shadow:0 0 0 3px rgba(26,107,60,.1)}
.sim-result{background:linear-gradient(135deg,var(--dark),var(--navy));border-radius:var(--radius-lg);padding:1.5rem 2rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem}
.sim-result-left h4{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:rgba(255,255,255,.4);margin-bottom:.3rem}
.sim-result-val{font-family:'Fraunces',serif;font-size:2.8rem;font-weight:600;color:#fff;line-height:1}
.sim-result-unit{font-size:.8rem;color:rgba(255,255,255,.5);margin-top:.2rem}
.sim-result-right{text-align:right}
.sim-result-range{font-size:.75rem;color:rgba(255,255,255,.45);margin-bottom:.3rem}
.sim-result-pha{font-size:.9rem;color:var(--lime);font-weight:700}
.btn-sim{background:linear-gradient(135deg,var(--green),var(--teal));color:#fff;padding:11px 28px;border-radius:var(--radius);font-size:.85rem;font-weight:700;border:none;cursor:pointer;font-family:'Plus Jakarta Sans',sans-serif;transition:all .2s;display:inline-flex;align-items:center;gap:8px}
.btn-sim:hover{transform:translateY(-2px);box-shadow:0 4px 16px rgba(26,107,60,.35)}
.btn-sim:disabled{opacity:.5;pointer-events:none}

/* ── Comparative ── */
#sec-comparative{margin-bottom:2rem}
.comp-card{background:#fff;border-radius:var(--radius-xl);border:1px solid var(--border);box-shadow:var(--shadow-xs);padding:1.5rem;margin-bottom:1rem}
.comp-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:1.2rem}
.comp-period-badge{display:flex;align-items:center;gap:.4rem}
.period-chip{font-size:.72rem;font-weight:700;padding:4px 12px;border-radius:20px}
.period-chip.a{background:#dcfce7;color:#166534}
.period-chip.b{background:#dbeafe;color:#1e40af}
.comp-vs{font-size:.7rem;color:var(--muted);font-weight:600}

/* ── Estate Drilldown Modal ── */
#estate-modal{display:none;position:fixed;inset:0;z-index:1000;background:rgba(10,22,40,.7);backdrop-filter:blur(4px);overflow-y:auto}
#estate-modal.show{display:flex;align-items:flex-start;justify-content:center;padding:3rem 1rem}
.modal-box{background:#fff;border-radius:var(--radius-xl);width:100%;max-width:900px;overflow:hidden;box-shadow:var(--shadow-lg);animation:fadeUp .3s ease}
.modal-header{background:linear-gradient(135deg,var(--dark),var(--navy));padding:1.4rem 1.8rem;display:flex;align-items:center;justify-content:space-between}
.modal-header h3{font-family:'Fraunces',serif;font-size:1.3rem;font-weight:600;color:#fff}
.modal-header p{font-size:.75rem;color:rgba(255,255,255,.5);margin-top:2px}
.btn-close-modal{background:rgba(255,255,255,.1);border:none;color:rgba(255,255,255,.7);width:32px;height:32px;border-radius:8px;font-size:1.1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;flex-shrink:0}
.btn-close-modal:hover{background:rgba(255,255,255,.2);color:#fff}
.modal-body{padding:1.5rem 1.8rem}
.modal-kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:.8rem;margin-bottom:1.2rem}
@media(max-width:700px){.modal-kpis{grid-template-columns:repeat(2,1fr)}}
.modal-kpi{background:var(--bg);border-radius:var(--radius);padding:.8rem 1rem;text-align:center}
.mkpi-val{font-family:'Fraunces',serif;font-size:1.4rem;font-weight:600;color:var(--dark)}
.mkpi-lbl{font-size:.68rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;margin-top:.2rem}
.modal-chart-img{width:100%;border-radius:var(--radius-lg);margin-bottom:1rem;display:block}

/* ── Clickable estate rows ── */
.estate-link{cursor:pointer;text-decoration:underline;text-underline-offset:2px;color:var(--green);transition:color .15s}
.estate-link:hover{color:var(--teal)}

.meta-row{background:#fff;border-radius:var(--radius-lg);padding:.9rem 1.4rem;border:1px solid var(--border);display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem;font-size:.72rem;color:var(--muted);align-items:center;margin-top:1.5rem}
.meta-row strong{color:var(--dark)}

@media(max-width:900px){
  #sidebar{transform:translateX(-100%)}
  #sidebar.open{transform:translateX(0)}
  #main-wrap{margin-left:0}
}

#toast{position:fixed;bottom:24px;right:24px;background:var(--dark);color:#fff;padding:12px 20px;border-radius:var(--radius);font-size:.8rem;font-weight:600;opacity:0;transition:all .3s;pointer-events:none;z-index:9998;border-left:3px solid var(--lime);box-shadow:var(--shadow-lg);max-width:300px}
#toast.show{opacity:1;transform:translateY(-3px)}
#toast.err{border-left-color:var(--red)}
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
</style>
</head>
<body>

<!-- ══ LANDING ══════════════════════════════════════════════════ -->
<div id="landing">
  <div class="lp-bg"></div><div class="lp-grid-bg"></div>
  <div class="lp-orb lp-orb1"></div><div class="lp-orb lp-orb2"></div><div class="lp-orb lp-orb3"></div>
  <div class="lp-wrap">
    <div class="lp-topbar">
      <div class="lp-brand">
        <div class="lp-brand-icon">
          <svg width="44" height="44" viewBox="0 0 44 44" fill="none"><rect width="44" height="44" rx="12" fill="url(#lpg)"/><text x="21" y="30" text-anchor="middle" font-family="Georgia,serif" font-size="21" font-weight="bold" fill="white">L</text><path d="M27 10 Q36 8 34 19 Q31 13 24 15 Z" fill="rgba(255,255,255,0.7)"/><defs><linearGradient id="lpg" x1="0" y1="0" x2="44" y2="44"><stop offset="0%" stop-color="#1a6b3c"/><stop offset="100%" stop-color="#0e7c6e"/></linearGradient></defs></svg>
        </div>
        <div class="lp-brand-txt"><h1>PT London Sumatra Indonesia</h1><p>Lonsum · Tbk · Est. 1906</p></div>
      </div>
      <div class="lp-topbar-right"><span class="lp-pill neutral">LEAP v4.0</span><span class="lp-pill gold">⚡ AI-Powered</span></div>
    </div>
    <div class="lp-main">
      <div class="lp-eyebrow"><span class="lp-dot"></span>Platform Analitik Perkebunan Enterprise — v4.0</div>
      <h1 class="lp-title">LEAP<br/><span class="lp-title-italic">Plantation</span><span class="lp-title-accent"> Intelligence</span></h1>
      <p class="lp-tagline">Dashboard kecerdasan buatan untuk <strong>memantau, menganalisis, dan memprediksi</strong> produksi kebun Lonsum — kini dengan <strong>laporan PDF eksekutif</strong>, analisis komparatif YoY, prediksi 3 bulan, dan simulator What-If interaktif.</p>
      <div class="lp-cta-wrap">
        <button class="btn-mulai" onclick="enterDashboard()">Mulai Analisis <span class="bm-arrow">→</span></button>
      </div>
      <div class="lp-features">
        <div class="lp-feat"><div class="lf-icon">📄</div><div class="lf-title">PDF Annual Report <span class="lf-new">NEW</span></div><div class="lf-desc">Cover page + 6 seksi + semua chart. Satu klik untuk laporan eksekutif siap rapat</div></div>
        <div class="lp-feat"><div class="lf-icon">📊</div><div class="lf-title">Perbandingan YoY <span class="lf-new">NEW</span></div><div class="lf-desc">Upload 2 CSV atau pakai 1 CSV multi-tahun untuk analisis komparatif otomatis</div></div>
        <div class="lp-feat"><div class="lf-icon">🔮</div><div class="lf-title">Forecast 3 Bulan <span class="lf-new">NEW</span></div><div class="lf-desc">Prediksi produksi 3 bulan ke depan dengan confidence interval yang melebar</div></div>
        <div class="lp-feat"><div class="lf-icon">⚗️</div><div class="lf-title">What-If Simulator <span class="lf-new">NEW</span></div><div class="lf-desc">"Jika curah hujan 250mm, 80 pekerja → produksi berapa?" — interaktif real-time</div></div>
        <div class="lp-feat"><div class="lf-icon">🔔</div><div class="lf-title">Alert Real-time <span class="lf-new">NEW</span></div><div class="lf-desc">Banner 🔴 Kritis / 🟡 Perlu Perhatian / 🟢 Normal per estate langsung di dashboard</div></div>
        <div class="lp-feat"><div class="lf-icon">🏭</div><div class="lf-title">Estate Drilldown <span class="lf-new">NEW</span></div><div class="lf-desc">Klik estate → analisis mendalam: tren historis, peringkat fleet, faktor dominan</div></div>
        <div class="lp-feat"><div class="lf-icon">✅</div><div class="lf-title">Data Quality Score <span class="lf-new">NEW</span></div><div class="lf-desc">Skor kualitas data otomatis sebelum analisis: completeness, outlier, duplikat</div></div>
        <div class="lp-feat"><div class="lf-icon">🖼️</div><div class="lf-title">Export Chart PNG <span class="lf-new">NEW</span></div><div class="lf-desc">Tombol download di setiap grafik untuk PowerPoint presentasi</div></div>
      </div>
      <div class="lp-howto">
        <div class="lp-sec-lbl">Cara Penggunaan</div>
        <div class="lp-steps">
          <div class="lp-step"><div class="step-num">1</div><div class="step-title">Siapkan CSV</div><div class="step-desc">Data produksi dengan 7 kolom yang diperlukan, atau 2 file CSV untuk perbandingan periode</div></div>
          <div class="lp-step"><div class="step-num">2</div><div class="step-title">Upload &amp; Proses</div><div class="step-desc">Pilih mode Single atau Comparative, upload file, sistem proses otomatis ~30 detik</div></div>
          <div class="lp-step"><div class="step-num">3</div><div class="step-title">Explore Dashboard</div><div class="step-desc">Baca insight AI per grafik, klik estate untuk drilldown, coba What-If simulator</div></div>
          <div class="lp-step"><div class="step-num">4</div><div class="step-title">Unduh Laporan</div><div class="step-desc">Export PDF annual report atau Excel untuk arsip dan rapat eksekutif</div></div>
        </div>
      </div>
      <div class="lp-format">
        <div class="lp-format-inner">
          <div class="lp-sec-lbl">Kolom CSV yang Diperlukan</div>
          <div class="lp-cols">
            <div class="lp-col-chip"><code>date</code><span>Tanggal (YYYY-MM-DD)</span></div>
            <div class="lp-col-chip"><code>estate</code><span>Nama kebun</span></div>
            <div class="lp-col-chip"><code>plantation_area_ha</code><span>Luas lahan (ha)</span></div>
            <div class="lp-col-chip"><code>rainfall_mm</code><span>Curah hujan (mm)</span></div>
            <div class="lp-col-chip"><code>workers</code><span>Jumlah tenaga kerja</span></div>
            <div class="lp-col-chip"><code>fertilizer_kg</code><span>Pupuk (kg)</span></div>
            <div class="lp-col-chip"><code>production_tons</code><span>Produksi (ton)</span></div>
          </div>
        </div>
      </div>
    </div>
    <div class="lp-footer">
      <p><strong>Lonsum LEAP v4.0</strong> — Enterprise Analytics Platform · Confidential</p>
      <div class="lp-stack-row">
        <span class="lp-stag">FastAPI</span><span class="lp-stag">scikit-learn</span><span class="lp-stag">Matplotlib</span>
        <span class="lp-stag">ReportLab</span><span class="lp-stag">NVIDIA NIM</span><span class="lp-stag">openpyxl</span>
      </div>
    </div>
  </div>
</div>

<!-- ══ SIDEBAR ══════════════════════════════════════════════════ -->
<nav id="sidebar">
  <div class="sb-top">
    <div class="sb-logo">
      <div class="sb-logo-img"><svg width="42" height="42" viewBox="0 0 42 42" fill="none"><rect width="42" height="42" rx="10" fill="url(#sbg)"/><text x="21" y="28" text-anchor="middle" font-family="serif" font-size="20" font-weight="bold" fill="white">L</text><path d="M26 12 Q32 10 30 18 Q28 14 22 15 Z" fill="rgba(255,255,255,0.7)"/><defs><linearGradient id="sbg" x1="0" y1="0" x2="42" y2="42"><stop offset="0%" stop-color="#1a6b3c"/><stop offset="100%" stop-color="#0e7c6e"/></linearGradient></defs></svg></div>
      <div class="sb-brand"><h1>LONSUM LEAP</h1><p>Intelligence Platform</p></div>
    </div>
    <div class="sb-meta">
      <div class="sb-meta-item"><span>⏰</span><span id="clock-sb">—</span></div>
      <div class="sb-meta-item"><span>📍</span><span>PT London Sumatra Indonesia</span></div>
    </div>
  </div>
  <div class="sb-nav">
    <div class="sb-section">
      <button class="sb-item" onclick="goHome()" style="margin-bottom:.4rem;border:1px solid rgba(255,255,255,.1)"><span class="sb-icon">🏠</span>Kembali ke Beranda</button>
    </div>
    <div class="sb-section">
      <span class="sb-section-label">Ringkasan</span>
      <button class="sb-item active" onclick="navTo('sec-overview',this)"><span class="sb-icon">📊</span>Overview &amp; KPI</button>
      <button class="sb-item" onclick="navTo('sec-alerts',this)"><span class="sb-icon">🔔</span>Alert Produksi<span class="badge-new">NEW</span></button>
      <button class="sb-item" onclick="navTo('sec-dq',this)"><span class="sb-icon">✅</span>Data Quality<span class="badge-new">NEW</span></button>
      <button class="sb-item" onclick="navTo('sec-downloads',this)"><span class="sb-icon">📦</span>Unduh Laporan<span class="badge">5</span></button>
    </div>
    <div class="sb-section">
      <span class="sb-section-label">Analisis Produksi</span>
      <button class="sb-item" onclick="navTo('sec-trend',this)"><span class="sb-icon">📈</span>Tren &amp; Musiman</button>
      <button class="sb-item" onclick="navTo('sec-estate',this)"><span class="sb-icon">🏭</span>Perbandingan Estate</button>
      <button class="sb-item" onclick="navTo('sec-productivity',this)"><span class="sb-icon">🌱</span>Produktivitas / Ha</button>
    </div>
    <div class="sb-section">
      <span class="sb-section-label">Analisis Faktor</span>
      <button class="sb-item" onclick="navTo('sec-correlation',this)"><span class="sb-icon">🔗</span>Korelasi &amp; Driver</button>
    </div>
    <div class="sb-section">
      <span class="sb-section-label">Prediksi AI</span>
      <button class="sb-item" onclick="navTo('sec-model',this)"><span class="sb-icon">🤖</span>Performa Model ML</button>
      <button class="sb-item" onclick="navTo('sec-featimp',this)"><span class="sb-icon">🏆</span>Faktor Terpenting</button>
      <button class="sb-item" onclick="navTo('sec-forecast',this)"><span class="sb-icon">🔮</span>Forecast 3 Bulan<span class="badge-new">NEW</span></button>
      <button class="sb-item" onclick="navTo('sec-simulator',this)"><span class="sb-icon">⚗️</span>What-If Simulator<span class="badge-new">NEW</span></button>
    </div>
    <div class="sb-section">
      <span class="sb-section-label">Analisis Lanjutan</span>
      <button class="sb-item" onclick="navTo('sec-comparative',this)"><span class="sb-icon">📊</span>Perbandingan YoY<span class="badge-new">NEW</span></button>
    </div>
  </div>
  <div class="sb-bottom">
    <div class="sb-version">LEAP v4.0 · scikit-learn · NVIDIA NIM · ReportLab</div>
  </div>
</nav>

<!-- ══ MAIN ══════════════════════════════════════════════════════ -->
<div id="main-wrap">
  <div id="topbar">
    <div class="tb-left">
      <h2 id="topbar-title">Plantation Analytics</h2>
      <span class="tb-breadcrumb" id="topbar-sub">Upload CSV untuk memulai analisis</span>
    </div>
    <div class="tb-right">
      <span class="badge-ai">⚡ AI-Powered</span>
      <button class="btn-sm" id="btn-reset" onclick="resetDash()">↺ Upload Baru</button>
    </div>
  </div>

  <div id="content">

    <!-- UPLOAD SECTION -->
    <div id="upload-section">
      <div class="upload-tabs">
        <button class="upload-tab active" onclick="switchTab('single',this)">📁 Single Dataset</button>
        <button class="upload-tab" onclick="switchTab('comparative',this)">📊 Comparative (2 Periode)</button>
      </div>

      <!-- Single Upload -->
      <div class="upload-pane active" id="pane-single">
        <div class="upload-card" id="upload-zone"
             onclick="document.getElementById('file-input').click()"
             ondragover="onDrag(event)" ondragleave="this.classList.remove('dragover')" ondrop="onDrop(event)">
          <div class="up-icon">🌿</div>
          <h2>Upload Data Produksi</h2>
          <p>Drag &amp; drop file CSV ke sini, atau klik untuk pilih file</p>
          <div class="col-hint">
            <code>date</code><code>estate</code><code>plantation_area_ha</code>
            <code>rainfall_mm</code><code>workers</code><code>fertilizer_kg</code><code>production_tons</code>
          </div>
          <button class="btn-primary" onclick="event.stopPropagation();document.getElementById('file-input').click()">📁 Pilih File CSV</button>
          <input type="file" id="file-input" accept=".csv" onchange="onFileSelect(event)"/>
        </div>
      </div>

      <!-- Comparative Upload -->
      <div class="upload-pane" id="pane-comparative">
        <div style="background:#fff;border-radius:var(--radius-xl);padding:2rem;border:1px solid var(--border);box-shadow:var(--shadow-sm)">
          <div style="margin-bottom:1.2rem">
            <div style="font-family:'Fraunces',serif;font-size:1.4rem;font-weight:600;color:var(--dark);margin-bottom:.3rem">Analisis Perbandingan Periode</div>
            <p style="font-size:.83rem;color:var(--muted)">Upload 2 file CSV (misalnya 2023 vs 2024), atau 1 file multi-tahun yang akan di-split otomatis per tahun.</p>
          </div>
          <div class="comp-pair">
            <div class="comp-slot" id="slot-a" onclick="document.getElementById('file-input-a').click()">
              <div class="comp-slot-icon">📅</div>
              <div class="comp-slot-label">Periode A (Lebih Lama)</div>
              <div class="comp-slot-file" id="slot-a-name">Klik untuk upload</div>
              <input type="file" id="file-input-a" accept=".csv" onchange="onCompFile('a',event)"/>
            </div>
            <div class="comp-slot" id="slot-b" onclick="document.getElementById('file-input-b').click()">
              <div class="comp-slot-icon">📅</div>
              <div class="comp-slot-label">Periode B (Lebih Baru)</div>
              <div class="comp-slot-file" id="slot-b-name">Klik untuk upload</div>
              <input type="file" id="file-input-b" accept=".csv" onchange="onCompFile('b',event)"/>
            </div>
          </div>
          <div style="text-align:center;margin:1rem 0;font-size:.75rem;color:var(--muted)">— atau —</div>
          <div style="text-align:center;margin-bottom:1.2rem">
            <div class="comp-slot" style="max-width:300px;display:inline-block;cursor:pointer" onclick="document.getElementById('file-input').click()" id="slot-auto">
              <div class="comp-slot-icon">🔄</div>
              <div class="comp-slot-label">1 CSV Multi-Tahun (Auto Split)</div>
              <div class="comp-slot-file" id="slot-auto-name">Klik untuk upload</div>
            </div>
          </div>
          <div style="text-align:center">
            <button class="btn-primary" id="btn-run-comp" onclick="runComparative()" disabled>📊 Jalankan Analisis Komparatif</button>
          </div>
        </div>
      </div>
    </div>

    <!-- LOADING -->
    <div id="loading">
      <div class="spinner-wrap"><div class="spinner"></div><div class="spinner-inner"></div></div>
      <div id="load-msg">Memulai pipeline analisis…</div>
      <div class="progress-bar"><div class="progress-fill"></div></div>
      <div class="load-steps">
        <div class="ls" id="s1"><span class="dot"></span>Membaca &amp; menilai kualitas data</div>
        <div class="ls" id="s2"><span class="dot"></span>Membuat grafik &amp; visualisasi</div>
        <div class="ls" id="s3"><span class="dot"></span>Melatih model prediksi ML</div>
        <div class="ls" id="s4"><span class="dot"></span>Menghasilkan insight AI via LLM</div>
        <div class="ls" id="s5"><span class="dot"></span>Menyiapkan laporan &amp; download</div>
      </div>
    </div>

    <!-- DASHBOARD -->
    <div id="dashboard">

      <!-- ALERT BANNERS -->
      <div id="sec-alerts">
        <div id="alert-banner-section"></div>
      </div>

      <!-- DATA QUALITY -->
      <div id="sec-dq" style="margin-bottom:1.8rem;display:none">
        <div class="section-sep"><span class="sl">✅ Data Quality Score</span><div class="line"></div></div>
        <div class="dq-row" id="dq-row"></div>
        <div class="ana-card">
          <div class="ac-header">
            <div class="ac-header-left"><span class="ac-icon">✅</span>
              <div><h3>Laporan Kualitas Data</h3><p>Evaluasi completeness, outlier, dan duplikasi sebelum analisis</p></div>
            </div><span class="ac-tag">Pre-Analysis</span>
          </div>
          <img id="c-dq" alt="" class="ac-chart" style="display:none"/>
          <div class="chart-ph" id="c-dq-ph"><div class="phi">✅</div><span>Memuat…</span></div>
        </div>
      </div>

      <!-- OVERVIEW & KPI -->
      <div id="sec-overview">
        <div class="page-header">
          <div class="ph-label">Executive Overview</div>
          <h2>Ringkasan Performa Produksi</h2>
          <p id="kpi-sub"></p>
        </div>
        <div class="kpi-grid" id="kpi-grid"></div>
      </div>

      <!-- DOWNLOADS -->
      <div id="sec-downloads">
        <div class="section-sep"><span class="sl">📦 Unduh Laporan Operasional</span><div class="line"></div></div>
        <div class="dl-bar">
          <div class="dl-bar-left">
            <div class="icon">📂</div>
            <div><h3>Laporan Otomatis Siap Diunduh</h3><p>PDF Annual Report, Excel, dan data mentah — format profesional siap rapat</p></div>
          </div>
          <div class="dl-btns">
            <a class="dl-btn dl-pdf" href="/api/download/pdf" download="Lonsum_AnnualReport.pdf">📄 Annual Report PDF</a>
            <a class="dl-btn dl-excel" href="/api/download/excel" download="Lonsum_ProduksiBulanan.xlsx">📊 Produksi Bulanan Excel</a>
            <a class="dl-btn dl-stats" href="/api/download/stats" download="Lonsum_StatistikEstate.xlsx">📋 Statistik Estate</a>
            <a class="dl-btn dl-alert" href="/api/download/alerts" download="Lonsum_AlertProduktivitas.xlsx">⚠️ Alert Produktivitas</a>
            <a class="dl-btn dl-forecast" href="/api/download/forecast" download="Lonsum_Forecast.xlsx">🔮 Forecast Excel</a>
          </div>
        </div>
      </div>

      <!-- TREND -->
      <div id="sec-trend">
        <div class="section-sep"><span class="sl">📈 Tren &amp; Pola Musiman</span><div class="line"></div></div>
        <div class="ana-card">
          <div class="ac-header">
            <div class="ac-header-left"><span class="ac-icon">📈</span><div><h3>Tren Produksi Bulanan</h3><p>Total produksi per bulan dari seluruh estate + rata-rata bergulir 3 bulan</p></div></div>
            <div class="ac-header-right"><span class="ac-tag">Time Series</span><button class="btn-dl-chart" onclick="dlChart('c-trend','trend_produksi')">⬇ PNG</button></div>
          </div>
          <img id="c-trend" alt="" class="ac-chart" style="display:none"/>
          <div class="chart-ph" id="c-trend-ph"><div class="phi">📈</div><span>Memuat…</span></div>
          <div class="ac-insight" id="ai-trend-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis…</p></div>
        </div>
        <div class="cgrid-2">
          <div class="ana-card">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">📅</span><div><h3>Profil Musiman</h3><p>Rata-rata produksi per bulan dalam setahun</p></div></div>
              <div class="ac-header-right"><span class="ac-tag">Seasonality</span><button class="btn-dl-chart" onclick="dlChart('c-seasonal','seasonal')">⬇ PNG</button></div>
            </div>
            <img id="c-seasonal" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-seasonal-ph"><div class="phi">📅</div><span>Memuat…</span></div>
            <div class="ac-insight" id="ai-seasonal-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis…</p></div>
          </div>
          <div class="ana-card" id="sec-estate">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">🏭</span><div><h3>Produksi Tahunan per Estate</h3><p>Kontribusi setiap estate per tahun</p></div></div>
              <div class="ac-header-right"><span class="ac-tag">Stacked Bar</span><button class="btn-dl-chart" onclick="dlChart('c-annual','annual_estate')">⬇ PNG</button></div>
            </div>
            <img id="c-annual" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-annual-ph"><div class="phi">🏭</div><span>Memuat…</span></div>
            <div class="ac-insight" id="ai-annual-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis…</p></div>
          </div>
        </div>
      </div>

      <!-- PRODUCTIVITY -->
      <div id="sec-productivity">
        <div class="section-sep"><span class="sl">🌱 Produktivitas &amp; Distribusi</span><div class="line"></div></div>
        <div class="cgrid-2">
          <div class="ana-card">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">📦</span><div><h3>Distribusi Produksi per Estate</h3><p>Sebaran data produksi bulanan — klik nama estate untuk detail</p></div></div>
              <div class="ac-header-right"><span class="ac-tag">Box Plot</span><button class="btn-dl-chart" onclick="dlChart('c-boxplot','boxplot_estate')">⬇ PNG</button></div>
            </div>
            <img id="c-boxplot" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-boxplot-ph"><div class="phi">📦</div><span>Memuat…</span></div>
            <div class="ac-insight" id="ai-boxplot-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis…</p></div>
          </div>
          <div class="ana-card">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">🌱</span><div><h3>Produktivitas per Hektar</h3><p>Klik nama estate di bawah untuk drilldown detail</p></div></div>
              <div class="ac-header-right"><span class="ac-tag">Benchmark</span><button class="btn-dl-chart" onclick="dlChart('c-prodha','prodha_estate')">⬇ PNG</button></div>
            </div>
            <img id="c-prodha" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-prodha-ph"><div class="phi">🌱</div><span>Memuat…</span></div>
            <div class="ac-insight" id="ai-prodha-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis…</p></div>
          </div>
        </div>
        <!-- Estate Drilldown Links -->
        <div id="estate-links" style="background:#fff;border-radius:var(--radius-lg);padding:1rem 1.4rem;border:1px solid var(--border);margin-bottom:1rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
          <span style="font-size:.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em">Drilldown Estate →</span>
          <div id="estate-link-btns" style="display:flex;flex-wrap:wrap;gap:.4rem"></div>
        </div>
      </div>

      <!-- CORRELATION -->
      <div id="sec-correlation">
        <div class="section-sep"><span class="sl">🔗 Korelasi &amp; Driver Produksi</span><div class="line"></div></div>
        <div class="cgrid-2">
          <div class="ana-card">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">🔗</span><div><h3>Matriks Korelasi</h3><p>Kekuatan hubungan antara setiap variabel operasional</p></div></div>
              <div class="ac-header-right"><span class="ac-tag">Heatmap</span><button class="btn-dl-chart" onclick="dlChart('c-corr','korelasi_heatmap')">⬇ PNG</button></div>
            </div>
            <img id="c-corr" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-corr-ph"><div class="phi">🔗</div><span>Memuat…</span></div>
            <div class="ac-insight" id="ai-corr-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis…</p></div>
          </div>
          <div class="ana-card">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">⚙️</span><div><h3>Driver vs Produksi</h3><p>Scatter antara input operasional dan output produksi</p></div></div>
              <div class="ac-header-right"><span class="ac-tag">Scatter</span><button class="btn-dl-chart" onclick="dlChart('c-scatter','scatter_driver')">⬇ PNG</button></div>
            </div>
            <img id="c-scatter" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-scatter-ph"><div class="phi">⚙️</div><span>Memuat…</span></div>
            <div class="ac-insight" id="ai-scatter-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis…</p></div>
          </div>
        </div>
      </div>

      <!-- MODEL ML -->
      <div id="sec-model">
        <div class="section-sep"><span class="sl">🤖 Model Machine Learning</span><div class="line"></div></div>
        <div class="model-table-wrap" style="margin-bottom:1.2rem">
          <table><thead><tr><th>Model</th><th>Akurasi (R²)</th><th>MAE (ton)</th><th>RMSE (ton)</th><th>CV R²</th><th>Status</th></tr></thead>
          <tbody id="mtable"></tbody></table>
        </div>
        <div class="ana-card">
          <div class="ac-header">
            <div class="ac-header-left"><span class="ac-icon">🎯</span><div><h3>Evaluasi Model Terbaik</h3><p>Prediksi vs Aktual, Residual, dan Distribusi Residual</p></div></div>
            <div class="ac-header-right"><span class="ac-tag">Evaluation</span><button class="btn-dl-chart" onclick="dlChart('c-model','model_evaluation')">⬇ PNG</button></div>
          </div>
          <img id="c-model" alt="" class="ac-chart" style="display:none"/>
          <div class="chart-ph" id="c-model-ph"><div class="phi">🎯</div><span>Memuat…</span></div>
          <div class="ac-insight" id="ai-model-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis…</p></div>
        </div>
      </div>

      <!-- FEATURE IMPORTANCE -->
      <div id="sec-featimp">
        <div class="section-sep"><span class="sl">🏆 Faktor Paling Berpengaruh</span><div class="line"></div></div>
        <div class="ana-card">
          <div class="ac-header">
            <div class="ac-header-left"><span class="ac-icon">🏆</span><div><h3>Feature Importance</h3><p>Faktor yang paling menentukan hasil produksi menurut model AI</p></div></div>
            <div class="ac-header-right"><span class="ac-tag">Importance</span><button class="btn-dl-chart" onclick="dlChart('c-fi','feature_importance')">⬇ PNG</button></div>
          </div>
          <img id="c-fi" alt="" class="ac-chart" style="display:none"/>
          <div class="chart-ph" id="c-fi-ph"><div class="phi">🏆</div><span>Memuat…</span></div>
          <div class="ac-insight" id="ai-fi-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis…</p></div>
        </div>
      </div>

      <!-- FORECAST 3 BULAN -->
      <div id="sec-forecast">
        <div class="section-sep"><span class="sl">🔮 Forecast Produksi 3 Bulan ke Depan</span><div class="line"></div></div>
        <div class="ana-card">
          <div class="ac-header">
            <div class="ac-header-left"><span class="ac-icon">🔮</span><div><h3>Prediksi Produksi — 3 Bulan ke Depan</h3><p>Confidence interval melebar sesuai jangkauan prediksi (uncertainty propagation)</p></div></div>
            <div class="ac-header-right"><span class="ac-tag">3-Month Forecast</span><button class="btn-dl-chart" onclick="dlChart('c-forecast','forecast_3bulan')">⬇ PNG</button></div>
          </div>
          <img id="c-forecast" alt="" class="ac-chart" style="display:none"/>
          <div class="chart-ph" id="c-forecast-ph"><div class="phi">🔮</div><span>Memuat…</span></div>
        </div>
        <div class="forecast-table-wrap" id="forecast-table-wrap" style="display:none">
          <table><thead><tr><th>Estate</th><th>Bulan +1 (ton)</th><th>Bulan +2 (ton)</th><th>Bulan +3 (ton)</th><th>Aktual Terakhir</th><th>Tren 3 Bulan</th></tr></thead>
          <tbody id="forecast-tbody"></tbody></table>
        </div>
        <div class="ac-insight" id="ai-forecast-box" style="margin-top:.5rem">
          <div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis…</p>
        </div>
      </div>

      <!-- WHAT-IF SIMULATOR -->
      <div id="sec-simulator">
        <div class="section-sep"><span class="sl">⚗️ What-If Simulator — Prediksi Produksi Manual</span><div class="line"></div></div>
        <div class="simulator-card">
          <div class="ac-header">
            <div class="ac-header-left"><span class="ac-icon">⚗️</span><div><h3>What-If Scenario Simulator</h3><p>Input kondisi operasional → prediksi produksi real-time menggunakan model ML terlatih</p></div></div>
            <span class="ac-tag">Interactive ML</span>
          </div>
          <div class="sim-body">
            <div class="sim-grid">
              <div class="sim-field"><label>Estate</label><select id="sim-estate"></select></div>
              <div class="sim-field"><label>Bulan Target</label><select id="sim-month"><option value="1">Januari</option><option value="2">Februari</option><option value="3">Maret</option><option value="4">April</option><option value="5">Mei</option><option value="6">Juni</option><option value="7">Juli</option><option value="8">Agustus</option><option value="9">September</option><option value="10">Oktober</option><option value="11">November</option><option value="12">Desember</option></select></div>
              <div class="sim-field"><label>Luas Lahan (ha)</label><input type="number" id="sim-area" placeholder="contoh: 500" min="1"/></div>
              <div class="sim-field"><label>Curah Hujan (mm)</label><input type="number" id="sim-rainfall" placeholder="contoh: 200" min="0"/></div>
              <div class="sim-field"><label>Jumlah Pekerja</label><input type="number" id="sim-workers" placeholder="contoh: 80" min="1"/></div>
              <div class="sim-field"><label>Pupuk (kg)</label><input type="number" id="sim-fertilizer" placeholder="contoh: 5000" min="0"/></div>
            </div>
            <button class="btn-sim" id="btn-sim" onclick="runSimulator()">⚗️ Hitung Prediksi</button>
            <div class="sim-result" id="sim-result" style="margin-top:1.2rem;display:none">
              <div class="sim-result-left">
                <h4>Prediksi Produksi</h4>
                <div class="sim-result-val" id="sim-val">—</div>
                <div class="sim-result-unit">ton / bulan</div>
              </div>
              <div class="sim-result-right">
                <div class="sim-result-range" id="sim-range">Rentang: — — —</div>
                <div class="sim-result-pha" id="sim-pha">— t/ha</div>
                <div style="font-size:.72rem;color:rgba(255,255,255,.4);margin-top:.3rem" id="sim-compare"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- COMPARATIVE YoY -->
      <div id="sec-comparative">
        <div class="section-sep"><span class="sl">📊 Analisis Perbandingan Periode</span><div class="line"></div></div>
        <div id="comp-content">
          <div style="background:#fff;border-radius:var(--radius-xl);padding:2rem;border:1px solid var(--border);text-align:center">
            <div style="font-size:2rem;margin-bottom:.8rem">📊</div>
            <div style="font-size:.9rem;color:var(--muted)">Gunakan tab <strong>Comparative</strong> di bagian upload untuk menjalankan analisis perbandingan periode.</div>
          </div>
        </div>
      </div>

      <div class="meta-row">
        <span>Dibuat: <strong id="meta-date"></strong></span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:.68rem">PT London Sumatra Indonesia · LEAP Analytics v4.0</span>
        <span id="meta-records"></span>
      </div>
    </div><!-- /dashboard -->
  </div><!-- /content -->
</div>

<!-- ══ ESTATE DRILLDOWN MODAL ═══════════════════════════════════ -->
<div id="estate-modal">
  <div class="modal-box">
    <div class="modal-header">
      <div>
        <h3 id="modal-estate-name">Estate Detail</h3>
        <p id="modal-estate-sub">Analisis mendalam performa estate</p>
      </div>
      <button class="btn-close-modal" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">
      <div class="modal-kpis" id="modal-kpis"></div>
      <img id="modal-chart" alt="" class="modal-chart-img" style="display:none"/>
      <div class="ac-insight" id="modal-insight">
        <div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI — Estate Spesifik</span></div>
        <p>Memuat analisis…</p>
      </div>
    </div>
  </div>
</div>

<div id="toast"></div>

<script>
// ─── Global state ───────────────────────────────────────────
var _charts = {};
var _kpis   = {};
var _estates = [];
var _mae    = 0;
var _compFileA = null, _compFileB = null, _compFileAuto = null;
var _compMode = null; // 'pair' or 'auto'

// ─── Clock ──────────────────────────────────────────────────
(function tick(){
  var d=new Date();
  var s=d.toLocaleDateString('id-ID',{weekday:'short',day:'2-digit',month:'short',year:'numeric'})
    +' · '+d.toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
  var e=document.getElementById('clock-sb');if(e)e.textContent=s;
  setTimeout(tick,1000);
})();

// ─── Navigation ─────────────────────────────────────────────
function navTo(id,btn){
  var el=document.getElementById(id);if(!el)return;
  var topH=document.getElementById('topbar').offsetHeight||62;
  window.scrollTo({top:el.getBoundingClientRect().top+window.scrollY-topH-20,behavior:'smooth'});
  document.querySelectorAll('.sb-item').forEach(function(b){b.classList.remove('active')});
  if(btn)btn.classList.add('active');
}
function toast(msg,type){
  var t=document.getElementById('toast');
  t.textContent=msg;t.className='show'+(type?' '+type:'');
  setTimeout(function(){t.className='';},4500);
}
function esc(s){
  if(s==null||s===undefined)return '—';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function fmt(v){var n=parseFloat(v);return isNaN(n)?String(v==null?'—':v):n.toLocaleString('id-ID',{maximumFractionDigits:1});}
function setImg(id,b64){
  var img=document.getElementById(id),ph=document.getElementById(id+'-ph');
  if(!img)return;
  if(b64&&typeof b64==='string'&&b64.length>200){
    img.onload=function(){img.style.display='block';if(ph)ph.style.display='none';};
    img.src='data:image/png;base64,'+b64;
  }else{
    img.style.display='none';
    if(ph){ph.querySelector('span').textContent='Data tidak tersedia.';ph.style.display='flex';}
  }
}
function setInsight(boxId,text){
  var box=document.getElementById(boxId);if(!box)return;
  var t=(text&&text.length>10)?text:'Insight AI tidak tersedia.';
  box.innerHTML='<div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI Analyst</span></div><p>'+esc(t)+'</p>';
}

// ─── Tab switching ──────────────────────────────────────────
function switchTab(mode,btn){
  document.querySelectorAll('.upload-tab').forEach(function(b){b.classList.remove('active')});
  btn.classList.add('active');
  document.querySelectorAll('.upload-pane').forEach(function(p){p.classList.remove('active')});
  document.getElementById('pane-'+mode).classList.add('active');
}

// ─── Loading steps ──────────────────────────────────────────
function animateSteps(){
  var ids=['s1','s2','s3','s4','s5'],delays=[0,8000,18000,28000,36000];
  ids.forEach(function(id,i){
    setTimeout(function(){
      ids.forEach(function(x,j){
        var el=document.getElementById(x);
        if(j<i)el.className='ls done';else if(j===i)el.className='ls active';else el.className='ls';
      });
    },delays[i]);
  });
}
function clearSteps(){['s1','s2','s3','s4','s5'].forEach(function(id){document.getElementById(id).className='ls';});}

// ─── File handling ──────────────────────────────────────────
function onDrag(e){e.preventDefault();document.getElementById('upload-zone').classList.add('dragover');}
function onDrop(e){e.preventDefault();document.getElementById('upload-zone').classList.remove('dragover');var f=e.dataTransfer.files[0];if(f)doUpload(f);}
function onFileSelect(e){
  var f=e.target.files[0];if(!f)return;
  // If comparative auto mode
  if(document.getElementById('pane-comparative').classList.contains('active')){
    _compFileAuto=f;_compMode='auto';
    document.getElementById('slot-auto-name').textContent=f.name;
    document.getElementById('slot-auto').classList.add('filled');
    document.getElementById('btn-run-comp').disabled=false;
  }else{
    doUpload(f);
  }
}
function onCompFile(slot,e){
  var f=e.target.files[0];if(!f)return;
  if(slot==='a'){_compFileA=f;document.getElementById('slot-a-name').textContent=f.name;document.getElementById('slot-a').classList.add('filled');}
  else{_compFileB=f;document.getElementById('slot-b-name').textContent=f.name;document.getElementById('slot-b').classList.add('filled');}
  if(_compFileA&&_compFileB){_compMode='pair';document.getElementById('btn-run-comp').disabled=false;}
}

function showErr(msg){
  var z=document.getElementById('upload-zone');
  var old=z.querySelector('.err-banner');if(old)old.remove();
  var d=document.createElement('div');d.className='err-banner';
  d.innerHTML='⚠️ '+esc(msg);z.insertBefore(d,z.firstChild);
}

// ─── Primary upload ─────────────────────────────────────────
function doUpload(file){
  if(!file.name.toLowerCase().endsWith('.csv')){toast('Hanya file CSV yang didukung.','err');return;}
  var old=document.querySelector('#upload-zone .err-banner');if(old)old.remove();
  document.getElementById('upload-section').style.display='none';
  document.getElementById('loading').style.display='flex';
  document.getElementById('dashboard').style.display='none';
  clearSteps();animateSteps();
  document.getElementById('topbar-sub').textContent='Menganalisis data…';
  var fd=new FormData();fd.append('file',file);
  fetch('/api/analyze',{method:'POST',body:fd})
    .then(function(res){var st=res.status;return res.text().then(function(txt){return{st:st,txt:txt};});})
    .then(function(obj){
      if(obj.st!==200){var em='Server error '+obj.st;try{var p=JSON.parse(obj.txt);em=p.detail||em;}catch(e){}throw new Error(em);}
      var data;try{data=JSON.parse(obj.txt);}catch(e){throw new Error('Response parse gagal.');}
      renderDash(data);
    })
    .catch(function(err){
      clearSteps();document.getElementById('loading').style.display='none';
      document.getElementById('upload-section').style.display='';
      showErr(err.message);toast(err.message,'err');
    });
}

// ─── Comparative upload ─────────────────────────────────────
function runComparative(){
  var fd=new FormData();
  if(_compMode==='pair'){
    fd.append('file_a',_compFileA);fd.append('file_b',_compFileB);fd.append('mode','pair');
  }else if(_compMode==='auto'&&_compFileAuto){
    fd.append('file',_compFileAuto);fd.append('mode','auto');
  }else{toast('Pilih file terlebih dahulu.','err');return;}
  document.getElementById('upload-section').style.display='none';
  document.getElementById('loading').style.display='flex';
  clearSteps();animateSteps();
  fetch('/api/analyze/comparative',{method:'POST',body:fd})
    .then(function(res){return res.json();})
    .then(function(data){renderComparative(data);})
    .catch(function(err){
      clearSteps();document.getElementById('loading').style.display='none';
      document.getElementById('upload-section').style.display='';
      toast(err.message,'err');
    });
}

// ─── Render Dashboard ───────────────────────────────────────
function renderDash(data){
  try{
    var k=data.kpis||{};
    _kpis=k; _estates=k.estates||[]; _mae=data.model_results&&data.model_results[0]?data.model_results[0].mae:0;
    _charts=data.charts||{};

    document.getElementById('topbar-title').textContent='Dashboard Produksi';
    document.getElementById('topbar-sub').textContent='Periode: '+(k.date_range||'—')+' · '+(k.num_estates||0)+' Estate';
    document.getElementById('kpi-sub').textContent='Periode: '+(k.date_range||'—')+'  ·  '+(k.num_estates||0)+' Estate  ·  '+fmt(k.total_records)+' Record';

    // KPI Cards
    var cards=[
      {icon:'🌿',lbl:'Total Produksi',val:fmt(k.total_production_tons)+' ton',sub:'Seluruh estate',acc:'g'},
      {icon:'📐',lbl:'Produktivitas Rata-rata',val:fmt(k.avg_productivity_t_ha)+' t/ha',sub:'Ton per hektar',acc:'gold'},
      {icon:'🏆',lbl:'Estate Terbaik',val:esc(k.best_estate||'—'),sub:'Produksi tertinggi',acc:'teal'},
      {icon:'📅',lbl:'Bulan Puncak',val:esc(k.peak_month||'—'),sub:'Rata-rata tertinggi',acc:'g'},
      {icon:'🏭',lbl:'Jumlah Estate',val:k.num_estates||0,sub:'Kebun dipantau',acc:'teal'},
      {icon:'📋',lbl:'Total Record',val:fmt(k.total_records),sub:'Data diproses',acc:'red'},
    ];
    document.getElementById('kpi-grid').innerHTML=cards.map(function(c){
      return '<div class="kpi"><div class="kpi-accent '+c.acc+'"></div>'+
        '<div class="kpi-top"><div class="kpi-icon-wrap">'+c.icon+'</div><span class="kpi-change neu">—</span></div>'+
        '<div class="kpi-val">'+c.val+'</div><div class="kpi-label">'+c.lbl+'</div><div class="kpi-sub">'+c.sub+'</div></div>';
    }).join('');

    // Alert Banners
    var alertSec=document.getElementById('alert-banner-section');
    var alertBanners=document.getElementById('alert-banner-section').parentElement;
    var alerts=data.alert_data||[];
    if(alerts.length>0){
      alertSec.style.display='block';
      alertSec.innerHTML=alerts.map(function(a){
        var cls=a.level==='crit'?'crit':a.level==='warn'?'warn':'ok';
        var ico=a.level==='crit'?'🔴':a.level==='warn'?'🟡':'🟢';
        return '<div class="alert-strip '+cls+'"><div class="alert-strip-icon">'+ico+'</div>'+
          '<div class="alert-strip-body"><h4>'+esc(a.estate)+' — '+esc(a.level_label)+'</h4>'+
          '<p>'+esc(a.message)+'</p></div></div>';
      }).join('');
    }

    // Data Quality
    var dq=data.data_quality||{};
    if(dq.score!==undefined){
      document.getElementById('sec-dq').style.display='';
      var dqCards=[
        {lbl:'Completeness',val:dq.completeness+'%',color:dq.completeness>95?'#1a6b3c':dq.completeness>85?'#c9a84c':'#d64045',w:dq.completeness},
        {lbl:'Outlier Rate',val:dq.outlier_rate+'%',color:dq.outlier_rate<5?'#1a6b3c':dq.outlier_rate<15?'#c9a84c':'#d64045',w:100-dq.outlier_rate},
        {lbl:'Duplikat',val:dq.duplicate_count,color:dq.duplicate_count===0?'#1a6b3c':'#e07b39',w:dq.duplicate_count===0?100:80},
        {lbl:'Overall Score',val:dq.score+'/100',color:dq.score>=80?'#1a6b3c':dq.score>=60?'#c9a84c':'#d64045',w:dq.score},
      ];
      document.getElementById('dq-row').innerHTML=dqCards.map(function(c){
        return '<div class="dq-card"><div class="dq-score" style="color:'+c.color+'">'+c.val+'</div>'+
          '<div class="dq-label">'+c.lbl+'</div>'+
          '<div class="dq-bar-track"><div class="dq-bar-fill" style="width:'+c.w+'%;background:'+c.color+'"></div></div></div>';
      }).join('');
      setImg('c-dq',_charts.dq);
    }

    // Charts
    var ch=_charts;
    setImg('c-trend',ch.trend);setImg('c-seasonal',ch.seasonal);setImg('c-annual',ch.annual);
    setImg('c-boxplot',ch.boxplot);setImg('c-prodha',ch.prodha);setImg('c-corr',ch.corr);
    setImg('c-scatter',ch.scatter);setImg('c-model',ch.model_eval);
    setImg('c-fi',ch.feature_imp);setImg('c-forecast',ch.forecast);

    // AI Insights
    var ai=data.ai_insights||{};
    setInsight('ai-trend-box',ai.trend);setInsight('ai-seasonal-box',ai.seasonal);
    setInsight('ai-annual-box',ai.annual);setInsight('ai-boxplot-box',ai.boxplot);
    setInsight('ai-prodha-box',ai.prodha);setInsight('ai-corr-box',ai.correlation);
    setInsight('ai-scatter-box',ai.scatter);setInsight('ai-model-box',ai.model);
    setInsight('ai-fi-box',ai.feature_importance);setInsight('ai-forecast-box',ai.forecast);

    // Model Table
    var best=data.best_model||'';
    document.getElementById('mtable').innerHTML=(data.model_results||[]).map(function(m){
      var r2=m.r2||0,pct=(r2*100).toFixed(1),bw=Math.round(Math.max(0,Math.min(1,r2))*80);
      var isBest=m.model===best;
      return '<tr style="'+(isBest?'background:#f0faf5;':'')+'">'+
        '<td><strong>'+esc(m.model)+'</strong>'+(isBest?'<span class="badge-best">★ Terbaik</span>':'')+'</td>'+
        '<td><div class="r2bar"><div class="r2track"><div class="r2fill" style="width:'+bw+'px"></div></div>'+
        '<span style="font-weight:700;color:'+(r2>0.85?'#1a6b3c':r2>0.6?'#c9a84c':'#d64045')+'">'+pct+'%</span></div></td>'+
        '<td>'+fmt(m.mae)+' ton</td><td>'+fmt(m.rmse)+' ton</td>'+
        '<td>'+((m.cv_r2||0)*100).toFixed(1)+'%</td>'+
        '<td><span style="font-size:.7rem;padding:3px 10px;border-radius:20px;background:'+(isBest?'#d1fae5':'#f1f5f9')+';color:'+(isBest?'#065f46':'#64748b')+';font-weight:700;">'+(isBest?'✓ Dipilih':'Dievaluasi')+'</span></td>'+
        '</tr>';
    }).join('');

    // Forecast 3 months table
    var fcData=data.forecast_3m||[];
    if(fcData.length>0){
      document.getElementById('forecast-table-wrap').style.display='';
      document.getElementById('forecast-tbody').innerHTML=fcData.map(function(r){
        var chg3=parseFloat(r.chg_m3||0);
        var trend=chg3>5?'📈 Naik':chg3<-5?'📉 Turun':'➡ Stabil';
        return '<tr><td><span class="estate-link" onclick="openModal(\''+esc(r.estate)+'\')">'+esc(r.estate)+'</span></td>'+
          '<td><strong>'+fmt(r.m1)+'</strong></td>'+
          '<td>'+fmt(r.m2)+'</td><td>'+fmt(r.m3)+'</td>'+
          '<td>'+fmt(r.last_actual)+'</td>'+
          '<td class="'+(chg3>=0?'chg-pos':'chg-neg')+'">'+trend+' ('+Math.abs(chg3).toFixed(1)+'%)</td></tr>';
      }).join('');
    }

    // Estate Drilldown links
    document.getElementById('estate-link-btns').innerHTML=_estates.map(function(e){
      return '<button onclick="openModal(\''+esc(e)+'\')" style="background:var(--light);border:1px solid rgba(26,107,60,.2);color:var(--green);padding:5px 14px;border-radius:20px;font-size:.75rem;font-weight:700;cursor:pointer;font-family:\'Plus Jakarta Sans\',sans-serif;transition:all .2s" onmouseover="this.style.background=\'var(--green)\';this.style.color=\'#fff\'" onmouseout="this.style.background=\'var(--light)\';this.style.color=\'var(--green)\'">🏭 '+esc(e)+'</button>';
    }).join('');

    // Simulator estate list
    document.getElementById('sim-estate').innerHTML=_estates.map(function(e){
      return '<option value="'+esc(e)+'">'+esc(e)+'</option>';
    }).join('');

    // Prefill simulator with avg values
    if(data.estate_stats){
      var first=data.estate_stats[_estates[0]]||{};
      if(first.avg_area)document.getElementById('sim-area').value=Math.round(first.avg_area);
      if(first.avg_rainfall)document.getElementById('sim-rainfall').value=Math.round(first.avg_rainfall);
      if(first.avg_workers)document.getElementById('sim-workers').value=Math.round(first.avg_workers);
      if(first.avg_fertilizer)document.getElementById('sim-fertilizer').value=Math.round(first.avg_fertilizer);
    }

    document.getElementById('meta-date').textContent=data.generated_at||'—';
    document.getElementById('meta-records').textContent='Model: '+esc(best);
    clearSteps();
    document.getElementById('loading').style.display='none';
    document.getElementById('dashboard').style.display='block';
    document.getElementById('btn-reset').style.display='inline-flex';
    window.scrollTo({top:0,behavior:'smooth'});
    toast('Dashboard berhasil dimuat — '+Object.keys(ch).length+' grafik · '+_estates.length+' estate');
  }catch(err){
    console.error('[renderDash]',err);
    clearSteps();document.getElementById('loading').style.display='none';
    document.getElementById('upload-section').style.display='';
    showErr('Render error: '+err.message);toast('Render error: '+err.message,'err');
  }
}

// ─── Render Comparative ─────────────────────────────────────
function renderComparative(data){
  clearSteps();document.getElementById('loading').style.display='none';
  document.getElementById('dashboard').style.display='block';
  document.getElementById('btn-reset').style.display='inline-flex';

  var compContent=document.getElementById('comp-content');
  if(!data||!data.summary){compContent.innerHTML='<p style="color:var(--muted)">Data komparatif tidak tersedia.</p>';return;}
  var s=data.summary;
  compContent.innerHTML=
    '<div class="comp-card">'+
    '<div class="comp-header">'+
    '<div><div style="font-family:\'Fraunces\',serif;font-size:1.1rem;font-weight:600;color:var(--dark)">Perbandingan '+esc(s.period_a)+' vs '+esc(s.period_b)+'</div>'+
    '<div style="font-size:.75rem;color:var(--muted);margin-top:2px">Analisis year-over-year otomatis dari dataset Anda</div></div>'+
    '<div class="comp-period-badge"><span class="period-chip a">'+esc(s.period_a)+'</span><span class="comp-vs">VS</span><span class="period-chip b">'+esc(s.period_b)+'</span></div>'+
    '</div>'+
    '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1rem">'+
    '<div style="background:var(--bg);border-radius:var(--radius);padding:1rem;text-align:center"><div style="font-family:\'Fraunces\',serif;font-size:1.5rem;font-weight:600;color:var(--dark)">'+fmt(s.total_a)+' ton</div><div style="font-size:.7rem;color:var(--muted);font-weight:700;text-transform:uppercase;margin-top:.2rem">Total '+esc(s.period_a)+'</div></div>'+
    '<div style="background:var(--bg);border-radius:var(--radius);padding:1rem;text-align:center"><div style="font-family:\'Fraunces\',serif;font-size:1.5rem;font-weight:600;color:var(--dark)">'+fmt(s.total_b)+' ton</div><div style="font-size:.7rem;color:var(--muted);font-weight:700;text-transform:uppercase;margin-top:.2rem">Total '+esc(s.period_b)+'</div></div>'+
    '<div style="background:'+(s.change_pct>=0?'#f0fdf4':'#fff1f0')+';border-radius:var(--radius);padding:1rem;text-align:center">'+
    '<div style="font-family:\'Fraunces\',serif;font-size:1.5rem;font-weight:600;color:'+(s.change_pct>=0?'#166534':'#991b1b')+'">'+(s.change_pct>=0?'▲':'▼')+Math.abs(s.change_pct).toFixed(1)+'%</div>'+
    '<div style="font-size:.7rem;color:var(--muted);font-weight:700;text-transform:uppercase;margin-top:.2rem">Perubahan YoY</div></div>'+
    '</div>'+
    (data.charts&&data.charts.comparative?'<img src="data:image/png;base64,'+data.charts.comparative+'" style="width:100%;border-radius:var(--radius-lg);margin-bottom:1rem"/>':'')+'</div>'+
    '<div class="ac-insight"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>'+esc(data.ai_insight||'—')+'</p></div>';

  navTo('sec-comparative',null);
  toast('Analisis komparatif selesai — '+esc(s.period_a)+' vs '+esc(s.period_b));
}

// ─── What-If Simulator ──────────────────────────────────────
function runSimulator(){
  var btn=document.getElementById('btn-sim');
  btn.disabled=true;btn.textContent='⏳ Menghitung…';
  var payload={
    estate:document.getElementById('sim-estate').value,
    month:parseInt(document.getElementById('sim-month').value),
    area_ha:parseFloat(document.getElementById('sim-area').value)||0,
    rainfall_mm:parseFloat(document.getElementById('sim-rainfall').value)||0,
    workers:parseInt(document.getElementById('sim-workers').value)||0,
    fertilizer_kg:parseFloat(document.getElementById('sim-fertilizer').value)||0,
  };
  fetch('/api/predict',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(payload)
  })
  .then(function(r){return r.json();})
  .then(function(d){
    var res=document.getElementById('sim-result');res.style.display='flex';
    document.getElementById('sim-val').textContent=fmt(d.prediction)+' ton';
    document.getElementById('sim-range').textContent='Rentang: '+fmt(d.lower)+' — '+fmt(d.upper)+' ton';
    var pha=payload.area_ha>0?(d.prediction/payload.area_ha).toFixed(4):0;
    document.getElementById('sim-pha').textContent=pha+' t/ha';
    var avgFleet=_kpis.avg_productivity_t_ha||0;
    var diff=(pha-avgFleet);
    document.getElementById('sim-compare').textContent=(diff>=0?'▲ ':'▼ ')+Math.abs(diff).toFixed(4)+' t/ha vs rata-rata fleet';
    btn.disabled=false;btn.textContent='⚗️ Hitung Prediksi';
  })
  .catch(function(err){
    toast('Simulator error: '+err.message,'err');
    btn.disabled=false;btn.textContent='⚗️ Hitung Prediksi';
  });
}

// ─── Estate Drilldown Modal ──────────────────────────────────
function openModal(estate){
  document.getElementById('modal-estate-name').textContent=estate;
  document.getElementById('modal-estate-sub').textContent='Analisis mendalam performa kebun '+estate;
  document.getElementById('estate-modal').classList.add('show');
  document.getElementById('modal-insight').innerHTML='<div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Memuat analisis…</p>';
  document.getElementById('modal-chart').style.display='none';
  fetch('/api/estate/'+encodeURIComponent(estate))
    .then(function(r){return r.json();})
    .then(function(d){
      document.getElementById('modal-kpis').innerHTML=[
        {lbl:'Total Produksi',val:fmt(d.total_production)+' ton'},
        {lbl:'Avg Bulanan',val:fmt(d.avg_monthly)+' ton'},
        {lbl:'Produktivitas',val:d.avg_productivity+' t/ha'},
        {lbl:'Peringkat Fleet',val:'#'+d.fleet_rank+' / '+d.fleet_total},
      ].map(function(k){
        return '<div class="modal-kpi"><div class="mkpi-val">'+k.val+'</div><div class="mkpi-lbl">'+k.lbl+'</div></div>';
      }).join('');
      if(d.chart){var mc=document.getElementById('modal-chart');mc.src='data:image/png;base64,'+d.chart;mc.style.display='block';}
      document.getElementById('modal-insight').innerHTML='<div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI — '+esc(estate)+'</span></div><p>'+esc(d.ai_insight)+'</p>';
    })
    .catch(function(){document.getElementById('modal-insight').innerHTML='<div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Gagal memuat analisis estate.</p>';});
}
function closeModal(){
  document.getElementById('estate-modal').classList.remove('show');
}
document.getElementById('estate-modal').addEventListener('click',function(e){if(e.target===this)closeModal();});

// ─── Download Chart PNG ─────────────────────────────────────
function dlChart(imgId,filename){
  var img=document.getElementById(imgId);
  if(!img||!img.src||img.style.display==='none'){toast('Grafik belum tersedia.','err');return;}
  var a=document.createElement('a');
  a.href=img.src;
  a.download='Lonsum_'+filename+'_'+new Date().toISOString().slice(0,10)+'.png';
  a.click();
  toast('📥 Mengunduh '+filename+'.png');
}

// ─── Page controls ──────────────────────────────────────────
function enterDashboard(){var lp=document.getElementById('landing');lp.classList.add('exit');setTimeout(function(){lp.style.display='none';},620);}
function goHome(){var lp=document.getElementById('landing');lp.style.display='';lp.classList.remove('exit');window.scrollTo({top:0,behavior:'smooth'});}
function resetDash(){
  document.getElementById('upload-section').style.display='';
  document.getElementById('dashboard').style.display='none';
  document.getElementById('btn-reset').style.display='none';
  document.getElementById('file-input').value='';
  document.getElementById('topbar-title').textContent='Plantation Analytics';
  document.getElementById('topbar-sub').textContent='Upload CSV untuk memulai analisis';
  window.scrollTo({top:0,behavior:'smooth'});
}
</script>
</body>
</html>"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM HELPER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def ask_llm(prompt: str, max_tokens: int = 500) -> str:
    payload = {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": (
                "Anda adalah konsultan analitik perkebunan senior PT London Sumatra Indonesia (Lonsum). "
                "Berikan insight singkat, padat, dan actionable dalam Bahasa Indonesia formal. "
                "Maks 3 paragraf pendek. Langsung ke inti. Sertakan angka spesifik dari data. "
                "Akhiri dengan 1 rekomendasi konkret yang bisa dilakukan segera."
            )},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.45, "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=60.0) as client:
            r = client.post(NVIDIA_BASE_URL, json=payload, headers=headers)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"AI insight tidak tersedia ({type(e).__name__})."


def fig_b64(fig, dpi=130) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=dpi)
    buf.seek(0); enc = base64.b64encode(buf.read()).decode()
    plt.close(fig); buf.close()
    return enc


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXCEL HELPERS (unchanged from v3.1)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _hfont(color="FFFFFF"): return Font(bold=True,color=color,name="Calibri",size=10)
def _hfill(hex_color:str)->PatternFill: return PatternFill("solid",fgColor=hex_color.lstrip("#"))
def _dfill(alt=False)->PatternFill: return PatternFill("solid",fgColor="F0FAF5" if alt else "FFFFFF")
_CENTER=Alignment(horizontal="center",vertical="center")
_THIN=Border(left=Side(style="thin",color="D1DDE8"),right=Side(style="thin",color="D1DDE8"),
              top=Side(style="thin",color="D1DDE8"),bottom=Side(style="thin",color="D1DDE8"))
def _apply_header(ws,row_num,cols,fill_hex):
    for c in range(1,cols+1):
        cell=ws.cell(row=row_num,column=c);cell.font=_hfont();cell.fill=_hfill(fill_hex)
        cell.alignment=_CENTER;cell.border=_THIN
def _apply_data_row(ws,row_num,cols,alt=False):
    for c in range(1,cols+1):
        cell=ws.cell(row=row_num,column=c);cell.fill=_dfill(alt);cell.border=_THIN;cell.alignment=_CENTER
def _set_widths(ws,widths):
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w
def _title_row(ws,text,cols,fill_hex="0a1628",row=1,height=30):
    ws.merge_cells(f"A{row}:{get_column_letter(cols)}{row}")
    cell=ws.cell(row=row,column=1,value=text)
    cell.font=Font(bold=True,name="Calibri",size=13,color="FFFFFF")
    cell.fill=_hfill(fill_hex);cell.alignment=_CENTER;ws.row_dimensions[row].height=height
def _subtitle_row(ws,text,cols,row=2):
    ws.merge_cells(f"A{row}:{get_column_letter(cols)}{row}")
    cell=ws.cell(row=row,column=1,value=text)
    cell.font=Font(italic=True,name="Calibri",size=9,color="64748b")
    cell.alignment=_CENTER;ws.row_dimensions[row].height=16


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MATPLOTLIB STYLE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def setup_mpl():
    plt.rcParams.update({
        "font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False,
        "axes.grid":True,"grid.alpha":.22,"grid.color":"#94a3b8","grid.linestyle":"--",
        "axes.labelcolor":"#1a2535","xtick.color":"#64748b","ytick.color":"#64748b",
        "axes.titlepad":12,"axes.titlesize":12,"axes.labelsize":9,
        "figure.facecolor":"white","axes.facecolor":"#fafbfd",
    })
    sns.set_palette(PALETTE)

MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 7: DATA QUALITY SCORE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def compute_data_quality(df_raw: pd.DataFrame) -> dict:
    total = len(df_raw)
    missing_cells = int(df_raw.isnull().sum().sum())
    total_cells = total * len(df_raw.columns)
    completeness = round((1 - missing_cells / total_cells) * 100, 1) if total_cells > 0 else 100.0
    duplicate_count = int(df_raw.duplicated().sum())

    numeric_cols = ["plantation_area_ha","rainfall_mm","workers","fertilizer_kg","production_tons"]
    outlier_count = 0
    col_outliers = {}
    for col in numeric_cols:
        if col not in df_raw.columns: continue
        q1, q3 = df_raw[col].quantile(0.25), df_raw[col].quantile(0.75)
        iqr = q3 - q1
        n = int(((df_raw[col] < q1 - 1.5*iqr) | (df_raw[col] > q3 + 1.5*iqr)).sum())
        outlier_count += n
        col_outliers[col] = n

    outlier_rate = round(outlier_count / total * 100, 1) if total > 0 else 0.0
    score = round(
        completeness * 0.4
        + max(0, 100 - outlier_rate * 3) * 0.35
        + (100 if duplicate_count == 0 else max(0, 100 - duplicate_count * 2)) * 0.25
    )
    score = min(100, max(0, score))

    # DQ chart
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("Data Quality Report", fontsize=13, fontweight="bold", color=C_DARK)

    # Completeness bar
    axes[0].bar(["Completeness"], [completeness], color=C_GREEN if completeness > 95 else C_GOLD, width=0.4)
    axes[0].bar(["Completeness"], [100 - completeness], bottom=[completeness], color="#f1f5f9", width=0.4)
    axes[0].set_ylim(0, 110); axes[0].set_title("Data Completeness (%)", fontweight="bold")
    axes[0].text(0, completeness + 3, f"{completeness}%", ha="center", fontweight="bold", fontsize=14)

    # Outlier per column
    oc_keys = list(col_outliers.keys()); oc_vals = list(col_outliers.values())
    short_keys = [k.replace("plantation_area_ha","luas").replace("_mm","").replace("_kg","").replace("_tons","").replace("workers","pekerja") for k in oc_keys]
    axes[1].bar(short_keys, oc_vals, color=[C_RED if v > total*0.1 else C_GOLD if v > 0 else C_GREEN for v in oc_vals])
    axes[1].set_title("Outlier Count per Kolom", fontweight="bold")
    axes[1].set_xlabel("Kolom"); axes[1].set_ylabel("Jumlah Outlier")
    axes[1].tick_params(axis="x", rotation=25)

    # Overall score gauge (simple horizontal bar)
    gauge_color = C_GREEN if score >= 80 else (C_GOLD if score >= 60 else C_RED)
    axes[2].barh(["Score"], [score], color=gauge_color, height=0.4)
    axes[2].barh(["Score"], [100 - score], left=[score], color="#f1f5f9", height=0.4)
    axes[2].set_xlim(0, 110); axes[2].set_title("Overall Quality Score", fontweight="bold")
    axes[2].text(score + 2, 0, f"{score}/100", va="center", fontweight="bold", fontsize=13, color=gauge_color)
    axes[2].axvline(80, color=C_GREEN, ls="--", lw=1, alpha=0.5, label="Target (80)")
    axes[2].legend(fontsize=8)

    fig.tight_layout(pad=1.5)
    dq_chart = fig_b64(fig, dpi=130)

    return {
        "completeness": completeness, "duplicate_count": duplicate_count,
        "outlier_rate": outlier_rate, "outlier_count": outlier_count,
        "col_outliers": col_outliers, "score": score, "chart": dq_chart,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 3: ALERT DATA (real-time severity per estate)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def compute_alerts(df: pd.DataFrame) -> list:
    avg_fleet = float(df["productivity_ton_per_ha"].mean())
    estate_avg = df.groupby("estate")["productivity_ton_per_ha"].mean()
    alerts = []
    for estate, val in estate_avg.items():
        ratio = val / avg_fleet if avg_fleet > 0 else 1.0
        if ratio < 0.70:
            level = "crit"; label = "🔴 Kritis"
            msg = (f"Produktivitas {val:.4f} t/ha — {((1-ratio)*100):.1f}% di bawah rata-rata fleet "
                   f"({avg_fleet:.4f} t/ha). Diperlukan investigasi segera: cek kondisi lahan, tenaga kerja, dan pupuk.")
        elif ratio < 0.88:
            level = "warn"; label = "🟡 Perlu Perhatian"
            msg = (f"Produktivitas {val:.4f} t/ha — {((1-ratio)*100):.1f}% di bawah rata-rata fleet. "
                   f"Monitor tren 2 bulan ke depan dan evaluasi program pemupukan.")
        else:
            level = "ok"; label = "🟢 Normal"
            msg = f"Produktivitas {val:.4f} t/ha — performa sesuai atau di atas rata-rata fleet ({avg_fleet:.4f} t/ha)."
        alerts.append({"estate": str(estate), "level": level, "level_label": label,
                       "message": msg, "productivity": round(float(val), 4)})
    alerts.sort(key=lambda x: {"crit": 0, "warn": 1, "ok": 2}[x["level"]])
    return alerts


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 4: MULTI-MONTH FORECAST (3 months with widening CI)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def compute_forecast_3m(df: pd.DataFrame, best_mdl, le: LabelEncoder,
                        FEATURES: list, mae_val: float) -> tuple:
    last_date = df["date"].max()
    estates   = sorted(df["estate"].unique().tolist())
    rows_3m   = []

    for est in estates:
        sub = df[df["estate"] == est]; last_row = sub.sort_values("date").iloc[-1]
        preds = []
        for horizon in range(1, 4):
            next_d = (last_date + timedelta(days=32 * horizon)).replace(day=1)
            feat_vec = pd.DataFrame([{
                "plantation_area_ha": last_row["plantation_area_ha"],
                "rainfall_mm": sub["rainfall_mm"].mean(),
                "workers": last_row["workers"],
                "fertilizer_kg": sub["fertilizer_kg"].mean(),
                "month": next_d.month,
                "quarter": (next_d.month - 1) // 3 + 1,
                "estate_encoded": int(last_row["estate_encoded"]),
            }])
            p = float(best_mdl.predict(feat_vec[FEATURES])[0])
            preds.append(p)

        last_actual = float(last_row["production_tons"])
        rows_3m.append({
            "estate": est,
            "m1": round(preds[0], 2), "m2": round(preds[1], 2), "m3": round(preds[2], 2),
            "last_actual": round(last_actual, 2),
            "chg_m1": round((preds[0] - last_actual) / last_actual * 100, 1) if last_actual else 0,
            "chg_m3": round((preds[2] - last_actual) / last_actual * 100, 1) if last_actual else 0,
        })

    # 3-month forecast chart with widening CI
    fig, ax = plt.subplots(figsize=(16, 7))
    fig.suptitle("Forecast Produksi 3 Bulan ke Depan (dengan Widening Confidence Interval)",
                 fontsize=13, fontweight="bold", color=C_DARK)
    x = np.arange(len(estates))
    w = 0.22
    ci_mult = [1.0, 1.5, 2.2]  # widening CI
    ci_labels = ["Bulan +1", "Bulan +2", "Bulan +3"]
    colors_fc = [C_GREEN, C_TEAL, C_GOLD]

    for i, (horizon, col, lbl) in enumerate(zip(range(3), colors_fc, ci_labels)):
        vals = [r[f"m{horizon+1}"] for r in rows_3m]
        ci   = mae_val * ci_mult[i]
        ax.bar(x + (i - 1) * w, vals, width=w*0.9, color=col, alpha=0.85,
               label=lbl, edgecolor="white", zorder=3)
        ax.errorbar(x + (i - 1) * w, vals, yerr=ci,
                    fmt="none", color=C_DARK, capsize=5, capthick=1.5, elinewidth=1.5, zorder=5)

    last_vals = [r["last_actual"] for r in rows_3m]
    ax.plot(x, last_vals, "D--", color=C_RED, lw=2, markersize=7, zorder=6, label="Aktual Terakhir")
    ax.set_xticks(x); ax.set_xticklabels(estates, rotation=15, ha="right")
    ax.set_ylabel("Produksi (ton)"); ax.legend(fontsize=9)
    ax.set_title(f"CI Bulan +1: ±{mae_val:.1f} | +2: ±{mae_val*1.5:.1f} | +3: ±{mae_val*2.2:.1f} ton",
                 fontsize=10, color=C_GRAY, pad=6)
    fig.tight_layout(pad=1.5)
    chart_3m = fig_b64(fig, dpi=135)
    return rows_3m, chart_3m


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 1: PDF ANNUAL REPORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_pdf_report(kpis: dict, model_results: list, forecast_3m: list,
                     alert_data: list, charts: dict, ai_insights: dict) -> bytes:
    buf = io.BytesIO()
    W, H = A4

    # ── Custom canvas for header/footer ──
    class LonsumCanvas(rl_canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._page_num = 0
        def showPage(self):
            self._page_num += 1
            self._draw_chrome()
            super().showPage()
        def save(self):
            self._page_num += 1
            self._draw_chrome()
            super().save()
        def _draw_chrome(self):
            if self._page_num <= 1:
                return  # no header/footer on cover
            self.saveState()
            # Header bar
            self.setFillColorRGB(0.1, 0.42, 0.24)
            self.rect(0, H - 28*mm, W, 10*mm, fill=1, stroke=0)
            self.setFillColorRGB(1, 1, 1)
            self.setFont("Helvetica-Bold", 8)
            self.drawString(20*mm, H - 22*mm, "PT London Sumatra Indonesia — LEAP Analytics Report")
            self.setFont("Helvetica", 8)
            self.drawRightString(W - 20*mm, H - 22*mm,
                                 kpis.get("generated_at", datetime.now().strftime("%d %B %Y")))
            # Footer
            self.setFillColorRGB(0.58, 0.7, 0.8)
            self.setFont("Helvetica", 7)
            self.drawString(20*mm, 12*mm, "Confidential — PT London Sumatra Indonesia · Lonsum LEAP v4.0")
            self.drawRightString(W - 20*mm, 12*mm, f"Halaman {self._page_num - 1}")
            self.restoreState()

    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=32*mm, bottomMargin=22*mm,
                            canvasmaker=LonsumCanvas)

    styles = getSampleStyleSheet()
    # Custom styles
    cov_title = ParagraphStyle("CovTitle", fontName="Helvetica-Bold", fontSize=36,
                               textColor=colors.white, alignment=TA_CENTER, leading=44)
    cov_sub   = ParagraphStyle("CovSub", fontName="Helvetica", fontSize=13,
                               textColor=colors.Color(0.78, 0.83, 0.88), alignment=TA_CENTER, leading=20)
    cov_label = ParagraphStyle("CovLabel", fontName="Helvetica-Bold", fontSize=8,
                               textColor=colors.Color(0.79, 0.66, 0.3), alignment=TA_CENTER,
                               letterSpacing=2, spaceAfter=4)
    sec_head  = ParagraphStyle("SecHead", fontName="Helvetica-Bold", fontSize=16,
                               textColor=colors.Color(0.1, 0.42, 0.24), spaceBefore=14, spaceAfter=6)
    sub_head  = ParagraphStyle("SubHead", fontName="Helvetica-Bold", fontSize=11,
                               textColor=colors.Color(0.06, 0.13, 0.25), spaceBefore=10, spaceAfter=4)
    body_s    = ParagraphStyle("Body", fontName="Helvetica", fontSize=9.5,
                               textColor=colors.Color(0.24, 0.35, 0.47), leading=15,
                               alignment=TA_JUSTIFY, spaceAfter=6)
    insight_s = ParagraphStyle("Insight", fontName="Helvetica", fontSize=9,
                               textColor=colors.Color(0.18, 0.3, 0.2), leading=14,
                               leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=4)
    caption   = ParagraphStyle("Caption", fontName="Helvetica-Oblique", fontSize=8,
                               textColor=colors.Color(0.55, 0.62, 0.7), alignment=TA_CENTER, spaceAfter=8)

    def h_rule():
        return HRFlowable(width="100%", thickness=1, color=colors.Color(0.86, 0.89, 0.93),
                          spaceBefore=8, spaceAfter=8)

    def section_label(txt):
        return Paragraph(f"<font color='#c9a84c'>◆</font> {txt}", sec_head)

    def insight_box(text, title="AI Insight"):
        rows = [[Paragraph(f"<b>🤖 {title}</b>", ParagraphStyle("IH", fontName="Helvetica-Bold",
                           fontSize=8, textColor=colors.Color(0.1,0.42,0.24))),
                 Paragraph(text or "—", insight_s)]]
        t = Table(rows, colWidths=[None])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.Color(0.95,0.99,0.97)),
            ("BACKGROUND", (0,1), (-1,-1), colors.Color(0.97,0.995,0.98)),
            ("BOX", (0,0), (-1,-1), 0.5, colors.Color(0.1,0.42,0.24,0.25)),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("RIGHTPADDING", (0,0), (-1,-1), 10),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        return t

    def b64_to_rl_image(b64: str, width_mm=170) -> RLImage:
        raw = base64.b64decode(b64)
        return RLImage(io.BytesIO(raw), width=width_mm*mm, height=width_mm*mm * 0.42)

    story = []

    # ═══════════════════════════ COVER PAGE ═══════════════════════════
    # We build cover using a custom flowable that draws on canvas
    class CoverPage(object):
        def wrap(self, aW, aH): return aW, aH
        def drawOn(self, canvas, x, y):
            canvas.saveState()
            # Full dark bg
            canvas.setFillColorRGB(0.04, 0.09, 0.16)
            canvas.rect(0, 0, W, H, fill=1, stroke=0)
            # Green gradient bar top
            canvas.setFillColorRGB(0.1, 0.42, 0.24)
            canvas.rect(0, H - 12*mm, W, 12*mm, fill=1, stroke=0)
            # Teal accent stripe
            canvas.setFillColorRGB(0.055, 0.49, 0.43)
            canvas.rect(0, H - 16*mm, W, 4*mm, fill=1, stroke=0)
            # Side accent left
            canvas.setFillColorRGB(0.1, 0.42, 0.24)
            canvas.rect(0, 0, 8*mm, H, fill=1, stroke=0)
            # Gold accent bar
            canvas.setFillColorRGB(0.79, 0.66, 0.3)
            canvas.rect(8*mm, 0, 3*mm, H, fill=1, stroke=0)

            # Logo circle
            cx, cy = W/2, H*0.72
            canvas.setFillColorRGB(0.1, 0.42, 0.24)
            canvas.circle(cx, cy, 28*mm, fill=1, stroke=0)
            canvas.setFillColorRGB(0.055, 0.49, 0.43)
            canvas.circle(cx, cy, 24*mm, fill=1, stroke=0)
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 36)
            canvas.drawCentredString(cx, cy - 6*mm, "L")
            canvas.setFont("Helvetica", 10)
            canvas.drawCentredString(cx, cy - 14*mm, "PT London Sumatra")

            # Title
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 42)
            canvas.drawCentredString(W/2, H*0.52, "PLANTATION")
            canvas.setFont("Helvetica-Bold", 42)
            canvas.drawCentredString(W/2, H*0.45, "ANNUAL REPORT")

            # Subtitle
            canvas.setFillColorRGB(0.79, 0.66, 0.3)
            canvas.setFont("Helvetica-Bold", 11)
            canvas.drawCentredString(W/2, H*0.40, f"LONSUM LEAP ANALYTICS · PERIOD: {kpis.get('date_range','—').upper()}")

            # KPI pills
            kpi_items = [
                ("Total Produksi", f"{kpis.get('total_production_tons',0):,.0f} ton"),
                ("Avg Produktivitas", f"{kpis.get('avg_productivity_t_ha',0):.4f} t/ha"),
                ("Estate Dipantau", str(kpis.get('num_estates',0))),
                ("Model Terbaik", str(model_results[0]['model'] if model_results else '—')),
            ]
            pill_w, pill_h = 38*mm, 16*mm
            start_x = W/2 - (len(kpi_items)/2 * (pill_w + 4*mm)) + pill_w/2
            for i, (lbl, val) in enumerate(kpi_items):
                px = start_x + i * (pill_w + 4*mm)
                py = H*0.29
                canvas.setFillColorRGB(0.06, 0.14, 0.25)
                canvas.roundRect(px - pill_w/2, py, pill_w, pill_h, 3*mm, fill=1, stroke=0)
                canvas.setFillColorRGB(0.79, 0.66, 0.3)
                canvas.setFont("Helvetica-Bold", 7)
                canvas.drawCentredString(px, py + pill_h - 6*mm, lbl.upper())
                canvas.setFillColor(colors.white)
                canvas.setFont("Helvetica-Bold", 10)
                canvas.drawCentredString(px, py + 3*mm, val)

            # Bottom info
            canvas.setFillColorRGB(0.35, 0.45, 0.55)
            canvas.setFont("Helvetica", 8)
            canvas.drawCentredString(W/2, 30*mm, f"Dibuat: {kpis.get('generated_at','—')}   ·   Confidential — Internal Use Only")
            canvas.drawCentredString(W/2, 24*mm, "PT London Sumatra Indonesia Tbk · Lonsum LEAP v4.0")

            canvas.restoreState()
        def split(self, aW, aH): return []

    story.append(CoverPage())
    story.append(PageBreak())

    # ═══════════════════════════ SECTION 1: EXECUTIVE SUMMARY ═══════
    story.append(section_label("1. Ringkasan Eksekutif"))
    story.append(h_rule())

    kpi_table_data = [
        ["Indikator", "Nilai", "Keterangan"],
        ["Total Produksi", f"{kpis.get('total_production_tons',0):,.1f} ton", "Seluruh estate & periode"],
        ["Rata-rata Produktivitas", f"{kpis.get('avg_productivity_t_ha',0):.4f} ton/ha", "Fleet average"],
        ["Estate Terbaik", str(kpis.get('best_estate','—')), "Berdasarkan total produksi"],
        ["Bulan Puncak", str(kpis.get('peak_month','—')), "Rata-rata tertinggi"],
        ["Jumlah Estate", str(kpis.get('num_estates',0)), "Dipantau dalam dataset"],
        ["Total Record Data", f"{kpis.get('total_records',0):,}", "Baris data diproses"],
        ["Periode Data", str(kpis.get('date_range','—')), "Rentang waktu analisis"],
    ]
    t_kpi = Table(kpi_table_data, colWidths=[60*mm, 55*mm, 55*mm])
    t_kpi.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.Color(0.04,0.09,0.16)),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 8),
        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,1), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.Color(0.97,0.995,0.98), colors.white]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.Color(0.86,0.89,0.93)),
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 8*mm))

    # Alert summary
    crit_count = sum(1 for a in alert_data if a["level"] == "crit")
    warn_count = sum(1 for a in alert_data if a["level"] == "warn")
    ok_count   = sum(1 for a in alert_data if a["level"] == "ok")
    story.append(Paragraph("Status Alert Estate:", sub_head))
    alert_rows = [["Estate", "Level", "Produktivitas (t/ha)", "Status"]]
    for a in alert_data:
        alert_rows.append([a["estate"], a["level_label"],
                           f"{a.get('productivity',0):.4f}", a["message"][:60] + "…"])
    t_alert = Table(alert_rows, colWidths=[35*mm, 30*mm, 35*mm, 70*mm])
    t_alert.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.Color(0.1,0.42,0.24)),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.4, colors.Color(0.86,0.89,0.93)),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.Color(0.98,0.98,0.98), colors.white]),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(t_alert)
    story.append(Spacer(1, 6*mm))
    story.append(insight_box(ai_insights.get("trend", "—"), "AI Executive Summary"))
    story.append(PageBreak())

    # ═══════════════════════════ SECTION 2: TREN PRODUKSI ═══════════
    story.append(section_label("2. Tren & Pola Produksi"))
    story.append(h_rule())
    if charts.get("trend"):
        story.append(b64_to_rl_image(charts["trend"], 170))
        story.append(Paragraph("Gambar 2.1 — Tren produksi bulanan seluruh estate dengan rata-rata bergulir 3 bulan", caption))
    story.append(insight_box(ai_insights.get("trend", "—"), "Analisis Tren Produksi"))
    story.append(Spacer(1, 4*mm))
    if charts.get("seasonal"):
        story.append(b64_to_rl_image(charts["seasonal"], 170))
        story.append(Paragraph("Gambar 2.2 — Profil musiman: rata-rata produksi per bulan kalender", caption))
    story.append(insight_box(ai_insights.get("seasonal", "—"), "Analisis Musiman"))
    story.append(PageBreak())

    # ═══════════════════════════ SECTION 3: PERBANDINGAN ESTATE ═════
    story.append(section_label("3. Perbandingan Performa Estate"))
    story.append(h_rule())
    if charts.get("annual"):
        story.append(b64_to_rl_image(charts["annual"], 170))
        story.append(Paragraph("Gambar 3.1 — Total produksi tahunan per estate (stacked bar)", caption))
    story.append(insight_box(ai_insights.get("annual", "—"), "Analisis Distribusi Estate"))
    story.append(Spacer(1, 4*mm))
    if charts.get("prodha"):
        story.append(b64_to_rl_image(charts["prodha"], 170))
        story.append(Paragraph("Gambar 3.2 — Produktivitas rata-rata per hektar per estate", caption))
    story.append(insight_box(ai_insights.get("prodha", "—"), "Analisis Produktivitas Lahan"))
    story.append(PageBreak())

    # ═══════════════════════════ SECTION 4: ANALISIS FAKTOR ══════════
    story.append(section_label("4. Analisis Faktor Produksi"))
    story.append(h_rule())
    if charts.get("corr"):
        story.append(b64_to_rl_image(charts["corr"], 170))
        story.append(Paragraph("Gambar 4.1 — Matriks korelasi dan koefisien Pearson antar faktor", caption))
    story.append(insight_box(ai_insights.get("correlation", "—"), "Analisis Korelasi Faktor"))
    story.append(PageBreak())

    # ═══════════════════════════ SECTION 5: MODEL ML ══════════════════
    story.append(section_label("5. Model Machine Learning & Prediksi"))
    story.append(h_rule())
    story.append(Paragraph("5.1 Perbandingan Model", sub_head))
    ml_rows = [["Model", "R² (%)", "MAE (ton)", "RMSE (ton)", "CV R²", "Status"]]
    for i, m in enumerate(model_results):
        ml_rows.append([
            m["model"], f"{m['r2']*100:.1f}%",
            f"{m['mae']:.3f}", f"{m['rmse']:.3f}",
            f"{m['cv_r2']*100:.1f}%",
            "★ Terbaik" if i == 0 else "Dievaluasi",
        ])
    t_ml = Table(ml_rows, colWidths=[50*mm, 25*mm, 25*mm, 25*mm, 22*mm, 23*mm])
    t_ml.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.Color(0.04,0.09,0.16)),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.Color(0.95,0.99,0.97), colors.white]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.Color(0.86,0.89,0.93)),
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(t_ml)
    story.append(Spacer(1, 5*mm))
    if charts.get("model_eval"):
        story.append(b64_to_rl_image(charts["model_eval"], 170))
        story.append(Paragraph("Gambar 5.1 — Evaluasi model terbaik: aktual vs prediksi, residual plot, distribusi residual", caption))
    story.append(insight_box(ai_insights.get("model", "—"), "Interpretasi Performa Model"))
    story.append(PageBreak())

    # ═══════════════════════════ SECTION 6: FORECAST ══════════════════
    story.append(section_label("6. Forecast Produksi 3 Bulan ke Depan"))
    story.append(h_rule())
    if charts.get("forecast"):
        story.append(b64_to_rl_image(charts["forecast"], 170))
        story.append(Paragraph("Gambar 6.1 — Prediksi produksi 3 bulan ke depan per estate dengan confidence interval", caption))
    story.append(Spacer(1, 4*mm))
    fc_rows = [["Estate", "Bulan +1 (ton)", "Bulan +2 (ton)", "Bulan +3 (ton)", "Aktual Terakhir", "Tren"]]
    for r in forecast_3m:
        chg = r.get("chg_m3", 0)
        fc_rows.append([r["estate"],
                        f"{r['m1']:,.1f}", f"{r['m2']:,.1f}", f"{r['m3']:,.1f}",
                        f"{r['last_actual']:,.1f}",
                        ("▲ +" if chg >= 0 else "▼ ") + f"{abs(chg):.1f}%"])
    t_fc = Table(fc_rows, colWidths=[35*mm, 28*mm, 28*mm, 28*mm, 30*mm, 21*mm])
    t_fc.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.Color(0.1,0.42,0.24)),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.Color(0.95,0.99,0.97), colors.white]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.Color(0.86,0.89,0.93)),
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(t_fc)
    story.append(Spacer(1, 5*mm))
    story.append(insight_box(ai_insights.get("forecast", "—"), "AI Forecast Analysis"))

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXCEL (same as v3.1, condensed)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_excel(df, kpis, model_results, forecast_df, alerts_df) -> bytes:
    generated_at = kpis.get("generated_at", datetime.now().strftime("%d %B %Y, %H:%M"))
    date_range   = kpis.get("date_range", "—")
    best_model   = model_results[0]["model"] if model_results else "—"
    wb = Workbook()

    # Sheet 1 — Monthly
    ws1 = wb.active; ws1.title = "Laporan Produksi Bulanan"; ws1.sheet_properties.tabColor = "1a6b3c"
    _title_row(ws1, "PT LONDON SUMATRA INDONESIA — LAPORAN PRODUKSI BULANAN", 8, "1a6b3c")
    _subtitle_row(ws1, f"Periode: {date_range}  |  Dibuat: {generated_at}", 8)
    hdrs = ["Tahun","Bulan","Estate","Luas (ha)","Curah Hujan (mm)","Tenaga Kerja","Pupuk (kg)","Produksi (ton)"]
    for i,h in enumerate(hdrs,1): ws1.cell(4,i,h)
    _apply_header(ws1,4,8,"1a6b3c")
    md = df[["year","month","month_name","estate","plantation_area_ha","rainfall_mm","workers","fertilizer_kg","production_tons"]].copy()
    md = md.sort_values(["year","month","estate"]).reset_index(drop=True)
    for ri,row in md.iterrows():
        r=ri+5
        ws1.cell(r,1,int(row["year"]));ws1.cell(r,2,str(row["month_name"]))
        ws1.cell(r,3,str(row["estate"]));ws1.cell(r,4,round(float(row["plantation_area_ha"]),2))
        ws1.cell(r,5,round(float(row["rainfall_mm"]),1));ws1.cell(r,6,int(row["workers"]))
        ws1.cell(r,7,round(float(row["fertilizer_kg"]),1));ws1.cell(r,8,round(float(row["production_tons"]),2))
        _apply_data_row(ws1,r,8,alt=(ri%2==0))
    _set_widths(ws1,[8,10,20,16,18,15,14,18])

    # Sheet 2 — Estate Stats
    ws2 = wb.create_sheet("Statistik Estate"); ws2.sheet_properties.tabColor = "0e7c6e"
    _title_row(ws2,"STATISTIK ESTATE — PT LONDON SUMATRA INDONESIA",10,"0e7c6e")
    _subtitle_row(ws2,f"Dibuat: {generated_at} | Periode: {date_range}",10)
    hdrs2=["Estate","Total (ton)","Avg Bulanan","Maks","Min","Std","Prod/ha","Hujan mm","Pekerja","Record"]
    for i,h in enumerate(hdrs2,1): ws2.cell(4,i,h)
    _apply_header(ws2,4,10,"0e7c6e")
    stats=df.groupby("estate").agg(total=("production_tons","sum"),avg=("production_tons","mean"),
        mx=("production_tons","max"),mn=("production_tons","min"),std=("production_tons","std"),
        ph=("productivity_ton_per_ha","mean"),rain=("rainfall_mm","mean"),
        wk=("workers","mean"),cnt=("production_tons","count")).round(2).reset_index()
    for ri,row in stats.iterrows():
        r=ri+5
        for ci,v in enumerate([row["estate"],row["total"],row["avg"],row["mx"],row["mn"],row["std"],row["ph"],row["rain"],round(float(row["wk"]),0),int(row["cnt"])],1):
            ws2.cell(r,ci,v)
        _apply_data_row(ws2,r,10,alt=(ri%2==0))
    _set_widths(ws2,[20,16,16,14,14,12,16,16,14,10])

    # Sheet 3 — Alerts
    ws3 = wb.create_sheet("Alert Produktivitas"); ws3.sheet_properties.tabColor = "d64045"
    _title_row(ws3,"ALERT PRODUKTIVITAS — PT LONDON SUMATRA INDONESIA",7,"d64045")
    avg_ph = float(df["productivity_ton_per_ha"].mean()); thr = avg_ph * 0.75
    _subtitle_row(ws3,f"Threshold: < {thr:.3f} t/ha | Fleet avg: {avg_ph:.3f} t/ha | Dibuat: {generated_at}",7)
    hdrs3=["Tanggal","Estate","Produksi (ton)","Luas (ha)","Produktivitas (t/ha)","Fleet Avg (t/ha)","Defisit (%)"]
    for i,h in enumerate(hdrs3,1): ws3.cell(4,i,h)
    _apply_header(ws3,4,7,"d64045")
    if len(alerts_df)>0:
        for ri,(_, row) in enumerate(alerts_df.iterrows()):
            r=ri+5; pv=float(row["productivity_ton_per_ha"]); deficit=round((avg_ph-pv)/avg_ph*100,1)
            try: ds=row["date"].strftime("%b %Y")
            except: ds=str(row["date"])
            for ci,v in enumerate([ds,str(row["estate"]),round(float(row["production_tons"]),2),round(float(row["plantation_area_ha"]),2),round(pv,4),round(avg_ph,4),deficit],1):
                ws3.cell(r,ci,v)
            _apply_data_row(ws3,r,7,alt=(ri%2==0))
    _set_widths(ws3,[14,18,16,14,20,20,14])

    # Sheet 4 — Forecast
    ws4 = wb.create_sheet("Forecast 3 Bulan"); ws4.sheet_properties.tabColor = "c9a84c"
    _title_row(ws4,"FORECAST PRODUKSI 3 BULAN — PT LONDON SUMATRA INDONESIA",8,"c9a84c")
    _subtitle_row(ws4,f"Model: {best_model} | Dibuat: {generated_at}",8)
    hdrs4=["Estate","Bulan +1 (ton)","Bulan +2 (ton)","Bulan +3 (ton)","Aktual Terakhir","Tren M1","Tren M3"]
    for i,h in enumerate(hdrs4,1): ws4.cell(4,i,h)
    _apply_header(ws4,4,8,"c9a84c")
    for ri,row in forecast_df.iterrows():
        r=ri+5
        for ci,v in enumerate([row.get("estate",""),row.get("m1",0),row.get("m2",0),row.get("m3",0),
                                row.get("last_actual",0),f"{row.get('chg_m1',0):+.1f}%",f"{row.get('chg_m3',0):+.1f}%"],1):
            ws4.cell(r,ci,v)
        _apply_data_row(ws4,r,8,alt=(ri%2==0))
    _set_widths(ws4,[20,18,18,18,20,14,14])

    # Sheet 5 — ML
    ws5 = wb.create_sheet("Hasil Model ML"); ws5.sheet_properties.tabColor = "457b9d"
    _title_row(ws5,"MODEL ML — PT LONDON SUMATRA INDONESIA",6)
    _subtitle_row(ws5,f"Dibuat: {generated_at} | Model terbaik: {best_model}",6)
    hdrs5=["Model","R²","MAE (ton)","RMSE (ton)","CV R²","Peringkat"]
    for i,h in enumerate(hdrs5,1): ws5.cell(4,i,h)
    _apply_header(ws5,4,6,"0a1628")
    for ri,m in enumerate(model_results):
        r=ri+5
        for ci,v in enumerate([m["model"],m["r2"],m["mae"],m["rmse"],m["cv_r2"],ri+1],1): ws5.cell(r,ci,v)
        _apply_data_row(ws5,r,6,alt=(ri%2==0))
        if ri==0:
            for c in range(1,7): ws5.cell(r,c).fill=_hfill("D1FAE5");ws5.cell(r,c).font=Font(bold=True,name="Calibri",color="065f46")
    _set_widths(ws5,[26,12,14,14,12,12])

    buf=io.BytesIO(); wb.save(buf); buf.seek(0); return buf.read()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CORE PIPELINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def process_dataset(raw: pd.DataFrame) -> dict:
    global _last_result
    setup_mpl()

    # ── Feature 7: Data Quality (before cleaning) ──
    dq = compute_data_quality(raw)

    # ── Cleaning ──
    df = raw.copy()
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(df[col]): df[col].fillna(df[col].median(), inplace=True)
            else: df[col].fillna(df[col].mode()[0], inplace=True)
    df = df.drop_duplicates().reset_index(drop=True)
    df["date"]       = pd.to_datetime(df["date"])
    df               = df.sort_values("date").reset_index(drop=True)
    df["year"]       = df["date"].dt.year
    df["month"]      = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    df["quarter"]    = df["date"].dt.quarter
    df["productivity_ton_per_ha"] = (df["production_tons"] / df["plantation_area_ha"]).round(4)
    df["production_per_worker"]   = (df["production_tons"] / df["workers"]).round(4)
    df["fertilizer_per_ha"]       = (df["fertilizer_kg"]   / df["plantation_area_ha"]).round(4)
    le = LabelEncoder()
    df["estate_encoded"] = le.fit_transform(df["estate"])

    estates      = sorted(df["estate"].unique().tolist())
    total_prod   = float(df["production_tons"].sum())
    avg_prod_ha  = float(df["productivity_ton_per_ha"].mean())
    best_estate  = str(df.groupby("estate")["production_tons"].sum().idxmax())
    peak_m_num   = int(df.groupby("month")["production_tons"].mean().idxmax())
    peak_month   = MONTH_LABELS[peak_m_num - 1]
    date_range   = df["date"].min().strftime("%b %Y") + " – " + df["date"].max().strftime("%b %Y")
    generated_at = datetime.now().strftime("%d %B %Y, %H:%M")

    kpis = dict(
        total_production_tons=round(total_prod, 1), avg_productivity_t_ha=round(avg_prod_ha, 4),
        best_estate=best_estate, peak_month=peak_month,
        total_records=int(len(df)), date_range=date_range,
        estates=estates, num_estates=int(len(estates)), generated_at=generated_at,
    )

    # ── Feature 3: Real-time alerts ──
    alert_data = compute_alerts(df)

    # ── ML ──
    FEATURES = ["plantation_area_ha","rainfall_mm","workers","fertilizer_kg","month","quarter","estate_encoded"]
    X, y = df[FEATURES], df["production_tons"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    mdict = {
        "Linear Regression" : LinearRegression(),
        "Random Forest"     : RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
        "Gradient Boosting" : GradientBoostingRegressor(n_estimators=200, random_state=42),
    }
    results, trained = [], {}
    for nm, mdl in mdict.items():
        mdl.fit(Xtr, ytr); yp = mdl.predict(Xte)
        results.append(dict(model=nm, mae=round(float(mean_absolute_error(yte,yp)),3),
                            rmse=round(float(np.sqrt(mean_squared_error(yte,yp))),3),
                            r2=round(float(r2_score(yte,yp)),4),
                            cv_r2=round(float(cross_val_score(mdl,X,y,cv=5,scoring="r2").mean()),4)))
        trained[nm] = (mdl, yp)
    results_sorted = sorted(results, key=lambda x: x["r2"], reverse=True)
    best_name = results_sorted[0]["model"]
    best_mdl, best_pred = trained[best_name]
    mae_val = results_sorted[0]["mae"]

    fi_series = None; fi_out = {}
    if hasattr(best_mdl, "feature_importances_"):
        fi_series = pd.Series(best_mdl.feature_importances_, index=FEATURES)
    elif hasattr(best_mdl, "coef_"):
        c = np.abs(best_mdl.coef_); c = c/c.sum()
        fi_series = pd.Series(c, index=FEATURES)
    if fi_series is not None:
        fi_out = {k: float(v) for k, v in fi_series.sort_values(ascending=False).items()}

    # ── Feature 4: 3-month forecast ──
    forecast_3m_rows, chart_3m = compute_forecast_3m(df, best_mdl, le, FEATURES, mae_val)
    forecast_3m_df = pd.DataFrame(forecast_3m_rows)

    # ── Alerts Excel df ──
    threshold = avg_prod_ha * 0.75
    alerts_df = df[df["productivity_ton_per_ha"] < threshold].sort_values("productivity_ton_per_ha").reset_index(drop=True)

    # ── Estate stats for simulator prefill ──
    estate_stats = {}
    for est in estates:
        sub = df[df["estate"] == est]
        estate_stats[est] = {
            "avg_area": float(sub["plantation_area_ha"].mean()),
            "avg_rainfall": float(sub["rainfall_mm"].mean()),
            "avg_workers": float(sub["workers"].mean()),
            "avg_fertilizer": float(sub["fertilizer_kg"].mean()),
        }

    # ─────────── CHARTS ───────────
    # 1 — Trend
    monthly = df.groupby("date")["production_tons"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(18, 5.5))
    ax.fill_between(monthly["date"], monthly["production_tons"], alpha=0.1, color=C_GREEN)
    ax.plot(monthly["date"], monthly["production_tons"], color=C_GREEN, lw=2, marker="o", markersize=3.5, zorder=4, label="Total Bulanan")
    roll = monthly["production_tons"].rolling(3, min_periods=1).mean()
    ax.plot(monthly["date"], roll, color=C_GOLD, lw=2.5, ls="--", zorder=5, label="Rolling Avg 3 Bulan")
    ax.set_title("Tren Produksi Bulanan & Rata-rata Bergulir", fontsize=13, fontweight="bold", color=C_DARK)
    ax.set_xlabel("Tanggal"); ax.set_ylabel("Produksi (ton)"); ax.legend(fontsize=9)
    ax.tick_params(axis="x", rotation=25); fig.tight_layout(pad=1.5)
    c_trend = fig_b64(fig, dpi=140)

    # 2 — Seasonal
    mavg = df.groupby("month")["production_tons"].mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(mavg.index, mavg.values, width=0.65, edgecolor="white",
                  color=[C_RED if v==mavg.min() else (C_LIME if v==mavg.max() else C_TEAL) for v in mavg.values], zorder=3)
    ax.set_xticks(range(1,13)); ax.set_xticklabels(MONTH_LABELS)
    ax.axhline(mavg.mean(), color=C_GOLD, ls="--", lw=1.5, label=f"Rata-rata ({mavg.mean():.1f}t)", zorder=4)
    ax.set_title("Profil Musiman — Avg Produksi per Bulan", fontsize=13, fontweight="bold", color=C_DARK)
    ax.set_ylabel("Produksi (ton)"); ax.legend(fontsize=9)
    for bar, val in zip(bars, mavg.values):
        ax.text(bar.get_x()+bar.get_width()/2, val+mavg.max()*0.01, f"{val:.0f}", ha="center", va="bottom", fontsize=8, fontweight="600")
    fig.tight_layout(pad=1.5); c_seasonal = fig_b64(fig, dpi=140)

    # 3 — Annual stacked
    piv = df.groupby(["year","estate"])["production_tons"].sum().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    piv.plot(kind="bar", stacked=True, ax=ax, color=PALETTE[:len(piv.columns)], edgecolor="white", width=0.6)
    ax.set_title("Produksi Tahunan per Estate", fontsize=13, fontweight="bold", color=C_DARK)
    ax.set_xlabel("Tahun"); ax.set_ylabel("Total Produksi (ton)"); ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Estate", bbox_to_anchor=(1.01,1), loc="upper left", fontsize=9)
    fig.tight_layout(pad=1.5); c_annual = fig_b64(fig, dpi=140)

    # 4 — Boxplot
    eo = df.groupby("estate")["production_tons"].median().sort_values(ascending=False).index
    fig, ax = plt.subplots(figsize=(10, 5))
    bp = ax.boxplot([df[df["estate"]==e]["production_tons"].values for e in eo],
                    patch_artist=True, labels=eo, widths=0.55,
                    medianprops=dict(color=C_GOLD, lw=2.5),
                    whiskerprops=dict(color=C_GRAY), capprops=dict(color=C_GRAY),
                    flierprops=dict(marker="o", color=C_RED, markersize=4, alpha=0.5))
    for i, p in enumerate(bp["boxes"]): p.set_facecolor(PALETTE[i%len(PALETTE)]); p.set_alpha(0.7)
    ax.set_title("Distribusi Produksi per Estate", fontsize=13, fontweight="bold", color=C_DARK)
    ax.set_xlabel("Estate"); ax.set_ylabel("Produksi (ton)"); ax.tick_params(axis="x", rotation=20)
    fig.tight_layout(pad=1.5); c_boxplot = fig_b64(fig, dpi=140)

    # 5 — Prod/ha
    pha = df.groupby("estate")["productivity_ton_per_ha"].mean().sort_values()
    thr2 = float(pha.mean())
    fig, ax = plt.subplots(figsize=(10, 5))
    bars_ph = ax.barh(pha.index, pha.values, color=[C_RED if v<thr2 else C_GREEN for v in pha.values], edgecolor="white", height=0.55)
    ax.axvline(thr2, color=C_GOLD, ls="--", lw=2, label=f"Rata-rata ({thr2:.3f})", zorder=4)
    ax.set_title("Produktivitas per Hektar per Estate", fontsize=13, fontweight="bold", color=C_DARK)
    ax.set_xlabel("Ton / Ha"); ax.legend(fontsize=9)
    for bar in bars_ph:
        v=bar.get_width(); ax.text(v+thr2*0.01, bar.get_y()+bar.get_height()/2, f"{v:.3f}", va="center", fontsize=8.5, fontweight="600")
    fig.tight_layout(pad=1.5); c_prodha = fig_b64(fig, dpi=140)

    # 6 — Correlation
    ccols = ["plantation_area_ha","rainfall_mm","workers","fertilizer_kg","productivity_ton_per_ha","production_tons"]
    corr = df[ccols].corr()
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(10, 150, s=80, as_cmap=True)
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap=cmap, ax=axes[0], linewidths=0.5, cbar_kws={"shrink":.8}, vmin=-1, vmax=1, annot_kws={"size":9,"weight":"600"})
    axes[0].set_title("Matriks Korelasi", fontsize=12, fontweight="bold", color=C_DARK)
    cp = corr["production_tons"].drop("production_tons").sort_values()
    axes[1].barh(cp.index, cp.values, color=[C_RED if v<0 else C_GREEN for v in cp.values], edgecolor="white", height=0.6)
    axes[1].axvline(0, color=C_DARK, lw=1)
    axes[1].set_title("Korelasi dengan Produksi", fontsize=12, fontweight="bold", color=C_DARK)
    axes[1].set_xlabel("Koefisien Pearson")
    for i, v in enumerate(cp.values):
        axes[1].text(v+(0.015 if v>=0 else -0.015), i, f"{v:+.3f}", va="center", ha="left" if v>=0 else "right", fontsize=9, fontweight="700", color=C_GREEN if v>=0 else C_RED)
    fig.tight_layout(pad=1.5); c_corr = fig_b64(fig, dpi=140)

    # 7 — Scatter
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Driver Produksi — Scatter Analysis", fontsize=14, fontweight="bold", color=C_DARK, y=1.01)
    pairs = [("rainfall_mm","Curah Hujan (mm)",C_TEAL),("fertilizer_kg","Pupuk (kg)",C_GOLD),
             ("workers","Jumlah Pekerja",C_NAVY),("plantation_area_ha","Luas Lahan (ha)",C_GREEN)]
    for ax, (x, xl, col) in zip(axes.flatten(), pairs):
        ax.scatter(df[x], df["production_tons"], alpha=0.45, color=col, s=18, zorder=3, edgecolors="white", linewidths=0.3)
        z = np.polyfit(df[x], df["production_tons"], 1)
        xr = np.linspace(float(df[x].min()), float(df[x].max()), 200)
        ax.plot(xr, np.poly1d(z)(xr), color=C_RED, lw=2, ls="--", label="Tren", zorder=4)
        r = float(df[[x,"production_tons"]].corr().iloc[0,1])
        ax.set_xlabel(xl); ax.set_ylabel("Produksi (ton)")
        ax.set_title(f"{xl}  (r={r:+.3f})", fontsize=10, fontweight="bold"); ax.legend(fontsize=8)
    fig.tight_layout(pad=1.5); c_scatter = fig_b64(fig, dpi=140)

    # 8 — Model eval
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f"Evaluasi Model — {best_name}", fontsize=13, fontweight="bold", color=C_DARK)
    mn2,mx2 = float(min(float(yte.min()),float(best_pred.min()))), float(max(float(yte.max()),float(best_pred.max())))
    axes[0].scatter(yte, best_pred, alpha=0.55, color=C_GREEN, s=22, zorder=3, edgecolors="white", linewidths=0.3)
    axes[0].plot([mn2,mx2],[mn2,mx2], color=C_RED, lw=2, ls="--", label="Ideal")
    axes[0].text(0.05, 0.90, f"R² = {results_sorted[0]['r2']:.4f}", transform=axes[0].transAxes, fontsize=12, color=C_RED, fontweight="bold")
    axes[0].set_xlabel("Aktual (ton)"); axes[0].set_ylabel("Prediksi (ton)"); axes[0].set_title("Aktual vs Prediksi", fontweight="bold"); axes[0].legend()
    resid = yte.values - best_pred
    axes[1].scatter(best_pred, resid, alpha=0.5, color=C_GOLD, s=22, zorder=3, edgecolors="white", linewidths=0.3)
    axes[1].axhline(0, color=C_RED, lw=2, ls="--"); axes[1].set_xlabel("Prediksi"); axes[1].set_ylabel("Residual"); axes[1].set_title("Plot Residual", fontweight="bold")
    axes[2].hist(resid, bins=28, color=C_TEAL, edgecolor="white", alpha=0.85); axes[2].axvline(0, color=C_RED, lw=2, ls="--")
    axes[2].set_xlabel("Residual"); axes[2].set_ylabel("Frekuensi"); axes[2].set_title("Distribusi Residual", fontweight="bold")
    fig.tight_layout(pad=1.5); c_model_eval = fig_b64(fig, dpi=140)

    # 9 — Feature importance
    c_fi = ""
    if fi_series is not None:
        fi_s = fi_series.sort_values(ascending=True)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.barh(fi_s.index, fi_s.values, color=[C_GREEN if v>=float(fi_s.median()) else C_TEAL for v in fi_s.values], edgecolor="white", height=0.6)
        ax.set_title(f"Feature Importance — {best_name}", fontsize=13, fontweight="bold", color=C_DARK)
        ax.set_xlabel("Skor Kepentingan")
        for bar in ax.patches: ax.text(bar.get_width()+fi_s.max()*0.01, bar.get_y()+bar.get_height()/2, f"{bar.get_width():.4f}", va="center", fontsize=9.5, fontweight="600")
        ax.set_xlim(0, fi_s.max()*1.18); fig.tight_layout(pad=1.5); c_fi = fig_b64(fig, dpi=140)

    # ── AI Insights ──
    estate_str = df.groupby("estate").agg(total=("production_tons","sum"),avg_prod_ha=("productivity_ton_per_ha","mean")).round(3).to_string()
    top3 = list(fi_out.keys())[:3] if fi_out else FEATURES[:3]

    ai_trend    = ask_llm(f"Data tren produksi Lonsum:\n- Total: {total_prod:,.1f} ton | Periode: {date_range}\n- Avg produktivitas: {avg_prod_ha:.4f} t/ha\n- Estate: {', '.join(estates)}\nAnalisis tren utama. 1 rekomendasi konkret.")
    ai_seasonal = ask_llm(f"Pola musiman produksi Lonsum:\n{df.groupby('month_name')['production_tons'].mean().round(1).to_string()}\nBulan puncak: {peak_month}.\nJelaskan pola musiman dan implikasinya. 1 rekomendasi.")
    ai_annual   = ask_llm(f"Produksi tahunan per estate:\n{estate_str}\nEstate terbaik: {best_estate}.\nBandingkan performa antar estate. 1 rekomendasi.")
    ai_boxplot  = ask_llm(f"Distribusi produksi per estate:\n{estate_str}\nAnalisis sebaran dan konsistensi. 1 rekomendasi.")
    ai_prodha   = ask_llm(f"Produktivitas/ha:\n{df.groupby('estate')['productivity_ton_per_ha'].mean().round(4).to_string()}\nFleet avg: {avg_prod_ha:.4f} t/ha.\nIdentifikasi estate di atas/bawah rata-rata. 1 rekomendasi.")
    ai_corr     = ask_llm(f"Korelasi dengan produksi:\n{df[ccols].corr()['production_tons'].drop('production_tons').round(3).to_string()}\nJelaskan hubungan antar faktor. 1 rekomendasi.")
    ai_scatter  = ask_llm(f"Driver produksi Lonsum: curah hujan, pupuk, pekerja, luas lahan.\nPeriode: {date_range}. Driver paling actionable? 1 rekomendasi konkret.")
    ai_model    = ask_llm(f"Model terbaik ({best_name}): R²={results_sorted[0]['r2']:.4f} | MAE={results_sorted[0]['mae']:.3f} ton | RMSE={results_sorted[0]['rmse']:.3f}.\nJelaskan maknanya. Seberapa bisa dipercaya? 1 rekomendasi penggunaan.")
    ai_fi       = ask_llm(f"Feature importance {best_name}:\n"+"\n".join([f"  {k}: {v:.4f}" for k,v in list(fi_out.items())[:5]])+"\nJelaskan mengapa faktor ini penting. 1 rekomendasi prioritas.")
    ai_forecast = ask_llm(f"Forecast 3 bulan:\n{pd.DataFrame(forecast_3m_rows)[['estate','m1','m2','m3']].to_string()}\nModel: {best_name} | MAE: {mae_val:.3f} ton\nAnalisis outlook. 1 rekomendasi tindakan segera.")

    ai_insights = {
        "trend": ai_trend, "seasonal": ai_seasonal, "annual": ai_annual,
        "boxplot": ai_boxplot, "prodha": ai_prodha, "correlation": ai_corr,
        "scatter": ai_scatter, "model": ai_model,
        "feature_importance": ai_fi, "forecast": ai_forecast,
    }

    charts = {
        "trend": c_trend, "seasonal": c_seasonal, "annual": c_annual,
        "boxplot": c_boxplot, "prodha": c_prodha, "corr": c_corr,
        "scatter": c_scatter, "model_eval": c_model_eval,
        "feature_imp": c_fi, "forecast": chart_3m,
        "dq": dq.get("chart", ""),
    }

    result = {
        "kpis": kpis, "model_results": results_sorted, "best_model": best_name,
        "feature_importance": fi_out, "forecast_3m": forecast_3m_rows,
        "alert_data": alert_data, "data_quality": dq,
        "charts": charts, "ai_insights": ai_insights,
        "generated_at": generated_at, "estate_stats": estate_stats,
    }

    _last_result = {
        **result,
        "_df": df, "_le": le, "_best_mdl": best_mdl,
        "_FEATURES": FEATURES, "_mae_val": mae_val,
        "_forecast_3m_df": forecast_3m_df, "_alerts_df": alerts_df,
    }
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 2: COMPARATIVE ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def compute_comparative(df_a: pd.DataFrame, df_b: pd.DataFrame,
                        label_a: str, label_b: str) -> dict:
    setup_mpl()
    for df in [df_a, df_b]:
        df["date"] = pd.to_datetime(df["date"])
        df["productivity_ton_per_ha"] = df["production_tons"] / df["plantation_area_ha"]
        for col in df.select_dtypes("number").columns:
            df[col].fillna(df[col].median(), inplace=True)

    total_a = float(df_a["production_tons"].sum())
    total_b = float(df_b["production_tons"].sum())
    chg = round((total_b - total_a) / total_a * 100, 1) if total_a else 0

    # Per-estate comparison
    ea = df_a.groupby("estate")["production_tons"].sum()
    eb = df_b.groupby("estate")["production_tons"].sum()
    all_estates = sorted(set(ea.index) | set(eb.index))
    ea = ea.reindex(all_estates, fill_value=0)
    eb = eb.reindex(all_estates, fill_value=0)
    estate_chg = ((eb - ea) / ea.replace(0, np.nan) * 100).round(1)

    # Chart
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(f"Analisis Komparatif: {label_a} vs {label_b}", fontsize=14, fontweight="bold", color=C_DARK)

    x = np.arange(len(all_estates)); w = 0.35
    axes[0].bar(x - w/2, ea.values, width=w, color=C_GREEN, label=label_a, edgecolor="white", alpha=0.85)
    axes[0].bar(x + w/2, eb.values, width=w, color="#457b9d", label=label_b, edgecolor="white", alpha=0.85)
    axes[0].set_xticks(x); axes[0].set_xticklabels(all_estates, rotation=20, ha="right")
    axes[0].set_title("Total Produksi per Estate", fontweight="bold")
    axes[0].set_ylabel("Produksi (ton)"); axes[0].legend()

    colors_chg = [C_LIME if v > 0 else C_RED for v in estate_chg.values]
    axes[1].bar(all_estates, estate_chg.values, color=colors_chg, edgecolor="white", alpha=0.85)
    axes[1].axhline(0, color=C_DARK, lw=1)
    axes[1].set_title(f"Perubahan YoY (%) — {label_a} → {label_b}", fontweight="bold")
    axes[1].set_ylabel("Perubahan (%)")
    axes[1].tick_params(axis="x", rotation=20)
    for i, (estate, val) in enumerate(zip(all_estates, estate_chg.values)):
        if not np.isnan(val):
            axes[1].text(i, val + (0.5 if val >= 0 else -1), f"{val:+.1f}%", ha="center", fontsize=8.5, fontweight="700", color=C_DARK)

    fig.tight_layout(pad=1.5)
    comp_chart = fig_b64(fig, dpi=135)

    ai_comp = ask_llm(
        f"Perbandingan produksi Lonsum:\n"
        f"- {label_a}: {total_a:,.1f} ton\n"
        f"- {label_b}: {total_b:,.1f} ton\n"
        f"- Perubahan total: {chg:+.1f}%\n"
        f"- Per estate:\n" + "\n".join([f"  {e}: {estate_chg.get(e,0):+.1f}%" for e in all_estates]) +
        "\nAnalisis perbandingan YoY. Estate mana yang tumbuh/decline? 1 rekomendasi konkret."
    )

    return {
        "summary": {"period_a": label_a, "period_b": label_b,
                    "total_a": round(total_a, 1), "total_b": round(total_b, 1),
                    "change_pct": chg, "estate_changes": {e: float(estate_chg.get(e, 0)) for e in all_estates}},
        "charts": {"comparative": comp_chart},
        "ai_insight": ai_comp,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 5: ESTATE DRILLDOWN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_estate_detail(estate_name: str) -> dict:
    if "_df" not in _last_result:
        return {}
    df = _last_result["_df"]
    sub = df[df["estate"] == estate_name]
    if len(sub) == 0:
        return {}
    setup_mpl()

    total  = float(sub["production_tons"].sum())
    avg_mo = float(sub["production_tons"].mean())
    avg_ph = float(sub["productivity_ton_per_ha"].mean())

    # Fleet rank
    fleet_avg = df.groupby("estate")["production_tons"].sum().sort_values(ascending=False)
    rank = int(fleet_avg.index.tolist().index(estate_name) + 1)

    # Estate chart: trend + production vs fleet avg
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"Detail Analisis Estate: {estate_name}", fontsize=13, fontweight="bold", color=C_DARK)

    monthly_e = sub.groupby("date")["production_tons"].sum().reset_index()
    axes[0].plot(monthly_e["date"], monthly_e["production_tons"], color=C_GREEN, lw=2, marker="o", markersize=4, zorder=4, label=estate_name)
    fleet_monthly = df.groupby("date")["production_tons"].mean().reset_index()
    axes[0].plot(fleet_monthly["date"], fleet_monthly["production_tons"], color=C_GOLD, lw=1.5, ls="--", alpha=0.7, label="Rata-rata Fleet")
    axes[0].set_title("Tren Produksi vs Rata-rata Fleet", fontweight="bold")
    axes[0].set_xlabel("Tanggal"); axes[0].set_ylabel("Produksi (ton)")
    axes[0].legend(fontsize=8); axes[0].tick_params(axis="x", rotation=25)

    # Radar-style bar comparing this estate vs fleet
    metrics = ["production_tons", "productivity_ton_per_ha", "rainfall_mm", "workers", "fertilizer_kg"]
    labels  = ["Produksi", "Produktiv/ha", "Curah Hujan", "Pekerja", "Pupuk"]
    estate_vals  = [sub[m].mean() for m in metrics]
    fleet_vals   = [df[m].mean()  for m in metrics]
    norm_e = [e/f if f > 0 else 1 for e, f in zip(estate_vals, fleet_vals)]
    x = np.arange(len(labels)); w = 0.35
    axes[1].bar(x - w/2, [1]*len(labels), width=w, color=C_GOLD, alpha=0.5, label="Fleet Avg (= 1.0)", edgecolor="white")
    axes[1].bar(x + w/2, norm_e, width=w, color=[C_GREEN if v >= 1 else C_RED for v in norm_e], alpha=0.8, label=estate_name, edgecolor="white")
    axes[1].set_xticks(x); axes[1].set_xticklabels(labels, rotation=20, ha="right")
    axes[1].set_title("Perbandingan vs Fleet (ternormalisasi)", fontweight="bold")
    axes[1].set_ylabel("Rasio vs Rata-rata Fleet"); axes[1].legend(fontsize=8)
    axes[1].axhline(1, color=C_GOLD, ls="--", lw=1)

    fig.tight_layout(pad=1.5)
    estate_chart = fig_b64(fig, dpi=130)

    ai = ask_llm(
        f"Analisis detail estate {estate_name} di Lonsum:\n"
        f"- Total produksi: {total:,.1f} ton\n"
        f"- Avg bulanan: {avg_mo:.1f} ton\n"
        f"- Produktivitas: {avg_ph:.4f} t/ha\n"
        f"- Peringkat fleet: #{rank} dari {len(fleet_avg)}\n"
        f"- Curah hujan avg: {sub['rainfall_mm'].mean():.1f} mm\n"
        f"- Pekerja avg: {sub['workers'].mean():.0f}\n"
        f"Berikan analisis mendalam untuk estate ini. Apa kekuatan dan kelemahan utamanya? 1 rekomendasi perbaikan konkret."
    )

    return {
        "estate": estate_name, "total_production": round(total, 1),
        "avg_monthly": round(avg_mo, 1), "avg_productivity": round(avg_ph, 4),
        "fleet_rank": rank, "fleet_total": int(len(fleet_avg)),
        "chart": estate_chart, "ai_insight": ai,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROUTES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@app.get("/", response_class=HTMLResponse)
async def root(): return HTMLResponse(HTML_PAGE)


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Only CSV files are accepted.")
    try:
        contents = await file.read()
        df_raw   = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(400, f"Failed to read CSV: {e}")
    required = {"date","estate","plantation_area_ha","rainfall_mm","workers","fertilizer_kg","production_tons"}
    missing  = required - set(df_raw.columns)
    if missing: raise HTTPException(422, f"Missing columns: {', '.join(sorted(missing))}")
    try:
        result = process_dataset(df_raw)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"Processing error: {e}")
    json_bytes = json.dumps(result, ensure_ascii=False).encode("utf-8")
    return StreamingResponse(iter([json_bytes]), media_type="application/json",
                             headers={"Content-Length": str(len(json_bytes))})


@app.post("/api/analyze/comparative")
async def analyze_comparative(
    mode: str = Form(...),
    file: UploadFile = File(None),
    file_a: UploadFile = File(None),
    file_b: UploadFile = File(None),
):
    try:
        if mode == "auto" and file:
            contents = await file.read()
            df_all = pd.read_csv(io.StringIO(contents.decode("utf-8")))
            df_all["date"] = pd.to_datetime(df_all["date"])
            years = sorted(df_all["date"].dt.year.unique())
            if len(years) < 2:
                raise HTTPException(422, "File harus memiliki minimal 2 tahun berbeda untuk mode auto.")
            df_a = df_all[df_all["date"].dt.year == years[-2]].copy()
            df_b = df_all[df_all["date"].dt.year == years[-1]].copy()
            label_a, label_b = str(years[-2]), str(years[-1])
        elif mode == "pair" and file_a and file_b:
            ca = await file_a.read(); cb = await file_b.read()
            df_a = pd.read_csv(io.StringIO(ca.decode("utf-8")))
            df_b = pd.read_csv(io.StringIO(cb.decode("utf-8")))
            df_a["date"] = pd.to_datetime(df_a["date"]); df_b["date"] = pd.to_datetime(df_b["date"])
            label_a = df_a["date"].dt.year.mode()[0]; label_b = df_b["date"].dt.year.mode()[0]
            label_a = str(label_a) if label_a != label_b else f"Periode A ({label_a})"
            label_b = f"Periode B ({label_b})" if label_a == label_b else str(label_b)
        else:
            raise HTTPException(400, "Invalid mode or missing files.")
        result = compute_comparative(df_a, df_b, str(label_a), str(label_b))
        _comp_result.update(result)
    except HTTPException: raise
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"Comparative error: {e}")
    return result


# ── Feature 6: What-If Simulator endpoint ──
@app.post("/api/predict")
async def predict_whatif(payload: dict):
    if "_best_mdl" not in _last_result:
        raise HTTPException(404, "Model belum dilatih. Upload CSV terlebih dahulu.")
    try:
        mdl      = _last_result["_best_mdl"]
        le       = _last_result["_le"]
        FEATURES = _last_result["_FEATURES"]
        mae_val  = _last_result["_mae_val"]
        estate   = payload.get("estate", "")
        if estate not in le.classes_:
            raise HTTPException(422, f"Estate '{estate}' tidak ada dalam data training.")
        feat_vec = pd.DataFrame([{
            "plantation_area_ha": float(payload.get("area_ha", 0)),
            "rainfall_mm":        float(payload.get("rainfall_mm", 0)),
            "workers":            int(payload.get("workers", 0)),
            "fertilizer_kg":      float(payload.get("fertilizer_kg", 0)),
            "month":              int(payload.get("month", 1)),
            "quarter":            (int(payload.get("month", 1)) - 1) // 3 + 1,
            "estate_encoded":     int(le.transform([estate])[0]),
        }])
        pred = float(mdl.predict(feat_vec[FEATURES])[0])
        return {"prediction": round(pred, 2),
                "lower": round(pred - mae_val, 2),
                "upper": round(pred + mae_val, 2)}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(500, f"Predict error: {e}")


# ── Feature 5: Estate drilldown endpoint ──
@app.get("/api/estate/{estate_name}")
async def estate_detail(estate_name: str):
    if "_df" not in _last_result:
        raise HTTPException(404, "Data belum tersedia.")
    try:
        detail = get_estate_detail(estate_name)
        if not detail: raise HTTPException(404, f"Estate '{estate_name}' tidak ditemukan.")
        return detail
    except HTTPException: raise
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"Estate detail error: {e}")


# ── Feature 1: PDF Download ──
@app.get("/api/download/pdf")
async def download_pdf():
    if "_df" not in _last_result:
        raise HTTPException(404, "Belum ada data.")
    try:
        pdf_bytes = build_pdf_report(
            kpis         = _last_result["kpis"],
            model_results= _last_result["model_results"],
            forecast_3m  = _last_result["forecast_3m"],
            alert_data   = _last_result["alert_data"],
            charts       = _last_result["charts"],
            ai_insights  = _last_result["ai_insights"],
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"PDF generation error: {e}")
    fname = f"Lonsum_AnnualReport_{datetime.now().strftime('%Y%m%d')}.pdf"
    return Response(content=pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})


# ── Excel Downloads (reusing same builder from v3.1) ──
@app.get("/api/download/excel")
async def download_excel():
    if "_df" not in _last_result: raise HTTPException(404, "Belum ada data.")
    try:
        xlsx = build_excel(_last_result["_df"], _last_result["kpis"],
                           _last_result["model_results"], _last_result["_forecast_3m_df"],
                           _last_result["_alerts_df"])
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"Excel error: {e}")
    fname = f"Lonsum_ProduksiBulanan_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return Response(content=xlsx, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})


@app.get("/api/download/stats")
async def download_stats():
    if "_df" not in _last_result: raise HTTPException(404, "Belum ada data.")
    try:
        df=_last_result["_df"]; kpis=_last_result["kpis"]
        generated_at=kpis.get("generated_at","—"); date_range=kpis.get("date_range","—")
        stats=df.groupby("estate").agg(total=("production_tons","sum"),avg=("production_tons","mean"),
            mx=("production_tons","max"),mn=("production_tons","min"),std=("production_tons","std"),
            ph=("productivity_ton_per_ha","mean"),rain=("rainfall_mm","mean"),
            wk=("workers","mean"),fert=("fertilizer_kg","mean"),cnt=("production_tons","count")).round(3).reset_index()
        wb=Workbook();ws=wb.active;ws.title="Statistik Estate";ws.sheet_properties.tabColor="0e7c6e"
        _title_row(ws,"STATISTIK ESTATE — PT LONDON SUMATRA INDONESIA",10,"0e7c6e")
        _subtitle_row(ws,f"Dibuat: {generated_at} | Periode: {date_range}",10)
        hdrs=["Estate","Total (ton)","Avg Bulanan","Maks","Min","Std","Prod/ha","Hujan mm","Pekerja","Record"]
        for i,h in enumerate(hdrs,1): ws.cell(3,i,h)
        _apply_header(ws,3,10,"0e7c6e")
        for ri,row in stats.iterrows():
            r=ri+4
            for ci,v in enumerate([row["estate"],row["total"],row["avg"],row["mx"],row["mn"],row["std"],row["ph"],row["rain"],round(float(row["wk"]),0),int(row["cnt"])],1): ws.cell(r,ci,v)
            _apply_data_row(ws,r,10,alt=(ri%2==0))
        _set_widths(ws,[18,16,16,14,14,12,16,16,14,10])
        buf=io.BytesIO();wb.save(buf);buf.seek(0)
    except Exception as e:
        import traceback; traceback.print_exc(); raise HTTPException(500,f"Stats error: {e}")
    fname=f"Lonsum_StatistikEstate_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return Response(content=buf.read(),media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition":f'attachment; filename="{fname}"'})


@app.get("/api/download/alerts")
async def download_alerts():
    if "_alerts_df" not in _last_result: raise HTTPException(404, "Belum ada data.")
    try:
        df=_last_result["_df"]; alerts_df=_last_result["_alerts_df"].copy(); kpis=_last_result["kpis"]
        generated_at=kpis.get("generated_at","—"); avg_prod=float(df["productivity_ton_per_ha"].mean()); thr=avg_prod*0.75
        alerts_df["fleet_avg_t_ha"]=round(avg_prod,4)
        alerts_df["deficit_pct"]=((avg_prod-alerts_df["productivity_ton_per_ha"])/avg_prod*100).round(1)
        wb=Workbook();ws=wb.active;ws.title="Alert Produktivitas";ws.sheet_properties.tabColor="d64045"
        _title_row(ws,"ALERT PRODUKTIVITAS — PT LONDON SUMATRA INDONESIA",7,"d64045")
        _subtitle_row(ws,f"Threshold: < {thr:.3f} t/ha | Dibuat: {generated_at}",7)
        hdrs=["Tanggal","Estate","Produksi (ton)","Luas (ha)","Produktivitas (t/ha)","Fleet Avg (t/ha)","Defisit (%)"]
        for i,h in enumerate(hdrs,1): ws.cell(4,i,h)
        _apply_header(ws,4,7,"d64045")
        if len(alerts_df)>0:
            for ri,(_,row) in enumerate(alerts_df.iterrows()):
                r=ri+5; pv=float(row["productivity_ton_per_ha"]); deficit=float(row["deficit_pct"])
                try: ds=row["date"].strftime("%b %Y")
                except: ds=str(row["date"])
                for ci,v in enumerate([ds,str(row["estate"]),round(float(row["production_tons"]),2),round(float(row["plantation_area_ha"]),2),round(pv,4),round(avg_prod,4),round(deficit,1)],1): ws.cell(r,ci,v)
                _apply_data_row(ws,r,7,alt=(ri%2==0))
                if deficit>40:
                    for c in range(1,8): ws.cell(r,c).fill=_hfill("FEE2E2")
        _set_widths(ws,[14,18,16,14,20,20,14])
        buf=io.BytesIO();wb.save(buf);buf.seek(0)
    except Exception as e:
        import traceback; traceback.print_exc(); raise HTTPException(500,f"Alerts error: {e}")
    fname=f"Lonsum_Alert_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return Response(content=buf.read(),media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition":f'attachment; filename="{fname}"'})


@app.get("/api/download/forecast")
async def download_forecast():
    if "_forecast_3m_df" not in _last_result: raise HTTPException(404, "Belum ada data.")
    try:
        fc=_last_result["_forecast_3m_df"].copy(); kpis=_last_result["kpis"]
        best=_last_result.get("best_model","—"); generated_at=kpis.get("generated_at","—"); date_range=kpis.get("date_range","—")
        wb=Workbook();ws=wb.active;ws.title="Forecast 3 Bulan";ws.sheet_properties.tabColor="c9a84c"
        _title_row(ws,"FORECAST 3 BULAN — PT LONDON SUMATRA INDONESIA",8,"c9a84c")
        _subtitle_row(ws,f"Model: {best} | Dibuat: {generated_at}",8)
        hdrs=["Estate","Bulan +1 (ton)","Bulan +2 (ton)","Bulan +3 (ton)","Aktual Terakhir","Tren M1 (%)","Tren M3 (%)"]
        for i,h in enumerate(hdrs,1): ws.cell(4,i,h)
        _apply_header(ws,4,8,"c9a84c")
        for ri,row in enumerate(fc.itertuples()):
            r=ri+5
            for ci,v in enumerate([row.estate,round(row.m1,2),round(row.m2,2),round(row.m3,2),round(row.last_actual,2),f"{row.chg_m1:+.1f}%",f"{row.chg_m3:+.1f}%"],1): ws.cell(r,ci,v)
            _apply_data_row(ws,r,8,alt=(ri%2==0))
        _set_widths(ws,[20,16,16,16,20,14,14])
        buf=io.BytesIO();wb.save(buf);buf.seek(0)
    except Exception as e:
        import traceback; traceback.print_exc(); raise HTTPException(500,f"Forecast error: {e}")
    fname=f"Lonsum_Forecast_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return Response(content=buf.read(),media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition":f'attachment; filename="{fname}"'})


@app.get("/api/health")
async def health():
    return {"status":"ok","has_data":"_df" in _last_result,"version":"4.0.0","timestamp":datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
