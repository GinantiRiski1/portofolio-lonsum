"""
Lonsum LEAP — Plantation Analytics Dashboard v3.1
Sidebar navigation · Per-card AI insights · Enterprise UI
Fix: generated_at ditambahkan ke kpis dict, error handling download diperbaiki
"""

import io, base64, json, warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import httpx
from openpyxl import Workbook
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side)
from openpyxl.utils import get_column_letter

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware

warnings.filterwarnings("ignore")

NVIDIA_API_KEY  = "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"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL    = "meta/llama-4-maverick-17b-128e-instruct"

C_DARK   = "#0a1628"
C_NAVY   = "#0d2137"
C_GREEN  = "#1a6b3c"
C_TEAL   = "#0e7c6e"
C_GOLD   = "#c9a84c"
C_LIME   = "#3dba6f"
C_RED    = "#d64045"
C_ORANGE = "#e07b39"
C_LIGHT  = "#e8f5ee"
C_GRAY   = "#94a3b8"
PALETTE  = [C_GREEN, C_TEAL, C_GOLD, C_LIME, C_ORANGE, C_RED, "#457b9d", "#7b5ea7"]

app = FastAPI(title="Lonsum LEAP Analytics", version="3.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Global state untuk menyimpan hasil analisis terakhir
_last_result: dict = {}

# ==============================================================================
# HTML PAGE
# ==============================================================================
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Lonsum LEAP — Plantation Intelligence Platform</title>
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
body{font-family:'Plus Jakarta Sans',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;-webkit-font-smoothing:antialiased;display:flex}

/* ══════════════════ LANDING PAGE ══════════════════ */
#landing{
  position:fixed;inset:0;z-index:9999;overflow-y:auto;
  background:var(--dark);
}
#landing.exit{animation:lpOut .6s cubic-bezier(.4,0,.2,1) forwards;pointer-events:none}
@keyframes lpOut{to{opacity:0;transform:scale(1.04)}}

.lp-bg{position:fixed;inset:0;pointer-events:none;z-index:0}
.lp-bg::before{
  content:'';position:absolute;inset:-40%;
  background:
    radial-gradient(ellipse 65% 55% at 18% 28%,rgba(26,107,60,.38) 0%,transparent 60%),
    radial-gradient(ellipse 55% 65% at 82% 72%,rgba(14,124,110,.28) 0%,transparent 60%),
    radial-gradient(ellipse 45% 40% at 65% 18%,rgba(201,168,76,.14) 0%,transparent 55%);
  animation:meshMove 20s ease-in-out infinite alternate;
}
@keyframes meshMove{0%{transform:translate(0,0)}100%{transform:translate(3%,2.5%)}}
.lp-grid-bg{
  position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);
  background-size:52px 52px;
}
.lp-orb{position:fixed;border-radius:50%;pointer-events:none;z-index:0;filter:blur(70px)}
.lp-orb1{width:420px;height:420px;background:rgba(26,107,60,.22);top:-100px;left:-80px}
.lp-orb2{width:320px;height:320px;background:rgba(14,124,110,.2);bottom:5%;right:-60px}
.lp-orb3{width:220px;height:220px;background:rgba(201,168,76,.1);top:38%;left:58%}

.lp-wrap{position:relative;z-index:10;min-height:100vh;display:flex;flex-direction:column}

.lp-topbar{
  display:flex;align-items:center;justify-content:space-between;
  padding:1.4rem 3rem;border-bottom:1px solid rgba(255,255,255,.06);flex-shrink:0;
}
.lp-brand{display:flex;align-items:center;gap:13px}
.lp-brand-icon{
  width:44px;height:44px;border-radius:12px;overflow:hidden;flex-shrink:0;
  background:linear-gradient(135deg,#1a6b3c,#0e7c6e);
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 4px 20px rgba(26,107,60,.5);
}
.lp-brand-txt h1{font-family:'Fraunces',serif;font-size:1rem;font-weight:600;color:#fff;letter-spacing:-.01em}
.lp-brand-txt p{font-size:.58rem;color:var(--gold);font-weight:700;text-transform:uppercase;letter-spacing:.16em;margin-top:1px}
.lp-topbar-right{display:flex;align-items:center;gap:.6rem}
.lp-pill{font-size:.63rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;padding:5px 13px;border-radius:20px}
.lp-pill.neutral{color:rgba(255,255,255,.4);border:1px solid rgba(255,255,255,.1)}
.lp-pill.gold{color:var(--gold);border:1px solid rgba(201,168,76,.3);background:rgba(201,168,76,.07)}

.lp-main{flex:1;display:flex;flex-direction:column;align-items:center;padding:4rem 2rem 3rem}

.lp-eyebrow{
  display:inline-flex;align-items:center;gap:9px;
  background:rgba(26,107,60,.18);border:1px solid rgba(26,107,60,.38);
  color:var(--lime);font-size:.7rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;
  padding:6px 18px;border-radius:20px;margin-bottom:2rem;
  animation:floatUp .7s .05s both;
}
.lp-dot{width:7px;height:7px;border-radius:50%;background:var(--lime);animation:blink 2s infinite;flex-shrink:0}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
@keyframes floatUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}

.lp-title{
  font-family:'Fraunces',serif;
  font-size:clamp(2.8rem,6vw,5.2rem);
  font-weight:600;color:#fff;letter-spacing:-.04em;
  line-height:1.07;text-align:center;margin-bottom:.8rem;
  animation:floatUp .7s .12s both;
}
.lp-title-accent{
  background:linear-gradient(130deg,var(--gold) 0%,var(--lime) 65%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.lp-title-italic{font-style:italic;font-weight:300;color:rgba(255,255,255,.65)}

.lp-tagline{
  font-size:clamp(.88rem,1.8vw,1.05rem);color:rgba(255,255,255,.48);
  max-width:540px;text-align:center;line-height:1.82;margin-bottom:2.8rem;
  animation:floatUp .7s .2s both;
}
.lp-tagline strong{color:rgba(255,255,255,.8);font-weight:600}

.lp-cta-wrap{animation:floatUp .7s .28s both;margin-bottom:3.5rem}
.btn-mulai{
  background:linear-gradient(135deg,#1a6b3c,#0e7c6e);color:#fff;
  padding:16px 48px;border-radius:12px;font-size:.98rem;font-weight:700;
  border:none;cursor:pointer;font-family:'Plus Jakarta Sans',sans-serif;
  letter-spacing:.02em;position:relative;overflow:hidden;
  box-shadow:0 8px 32px rgba(26,107,60,.5);transition:all .25s;
  display:inline-flex;align-items:center;gap:10px;
}
.btn-mulai::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(255,255,255,.15),transparent);opacity:0;transition:opacity .2s}
.btn-mulai:hover{transform:translateY(-3px);box-shadow:0 14px 44px rgba(26,107,60,.62)}
.btn-mulai:hover::before{opacity:1}
.bm-arrow{transition:transform .2s;font-size:1.1rem}
.btn-mulai:hover .bm-arrow{transform:translateX(5px)}

.lp-features{
  display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;
  width:100%;max-width:940px;margin-bottom:2.5rem;
  animation:floatUp .7s .35s both;
}
@media(max-width:760px){.lp-features{grid-template-columns:repeat(2,1fr)}}
.lp-feat{
  background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
  border-radius:14px;padding:1.2rem 1.1rem;transition:all .22s;
}
.lp-feat:hover{background:rgba(255,255,255,.07);border-color:rgba(255,255,255,.15);transform:translateY(-3px)}
.lf-icon{font-size:1.4rem;margin-bottom:.6rem}
.lf-title{font-size:.8rem;font-weight:700;color:#fff;margin-bottom:.25rem}
.lf-desc{font-size:.7rem;color:rgba(255,255,255,.38);line-height:1.65}

.lp-howto{
  width:100%;max-width:860px;margin-bottom:1.8rem;
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
  border-radius:16px;padding:1.8rem 2rem;
  animation:floatUp .7s .41s both;
}
.lp-sec-lbl{
  font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.15em;
  color:var(--gold);margin-bottom:1.2rem;display:flex;align-items:center;gap:8px;
}
.lp-sec-lbl::before{content:'';display:inline-block;width:16px;height:2px;background:var(--gold);border-radius:1px}
.lp-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:1.2rem}
@media(max-width:580px){.lp-steps{grid-template-columns:repeat(2,1fr)}}
.lp-step{position:relative}
.lp-step:not(:last-child)::after{content:'→';position:absolute;right:-.7rem;top:.2rem;color:rgba(255,255,255,.1);font-size:.8rem}
@media(max-width:580px){.lp-step:not(:last-child)::after{display:none}}
.step-num{
  width:30px;height:30px;border-radius:9px;margin-bottom:.55rem;
  background:linear-gradient(135deg,var(--green),var(--teal));
  display:inline-flex;align-items:center;justify-content:center;
  font-size:.72rem;font-weight:800;color:#fff;
}
.step-title{font-size:.78rem;font-weight:700;color:rgba(255,255,255,.85);margin-bottom:.22rem}
.step-desc{font-size:.68rem;color:rgba(255,255,255,.37);line-height:1.6}

.lp-format{width:100%;max-width:860px;margin-bottom:1.8rem;animation:floatUp .7s .46s both}
.lp-format-inner{background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.2);border-radius:14px;padding:1.1rem 1.7rem}
.lp-cols{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:.65rem}
.lp-col-chip{display:flex;align-items:center;gap:7px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:.38rem .85rem}
.lp-col-chip code{font-family:'JetBrains Mono',monospace;font-size:.67rem;color:var(--lime)}
.lp-col-chip span{font-size:.63rem;color:rgba(255,255,255,.28)}

.lp-portfolio-credit{
  display:inline-flex;align-items:center;gap:10px;
  background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);
  border-radius:20px;padding:8px 20px;margin-bottom:2rem;
  animation:floatUp .7s .5s both;
}
.port-pre{font-size:.62rem;color:rgba(255,255,255,.3);font-weight:500}
.port-sep{width:1px;height:12px;background:rgba(255,255,255,.15)}
.port-name{font-size:.75rem;font-weight:700;color:rgba(255,255,255,.8)}
.port-tag{font-size:.6rem;background:rgba(201,168,76,.15);color:var(--gold);border:1px solid rgba(201,168,76,.3);padding:2px 8px;border-radius:10px;font-weight:700}

.lp-footer{
  border-top:1px solid rgba(255,255,255,.06);padding:1rem 3rem;flex-shrink:0;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;
}
.lp-footer p{font-size:.67rem;color:rgba(255,255,255,.22)}
.lp-footer strong{color:rgba(255,255,255,.45)}
.lp-stack-row{display:flex;gap:.4rem;flex-wrap:wrap}
.lp-stag{font-family:'JetBrains Mono',monospace;font-size:.58rem;color:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.07);padding:3px 8px;border-radius:20px}

/* ══════════════════ SIDEBAR ══════════════════ */
#sidebar{
  width:var(--sidebar-w);min-height:100vh;flex-shrink:0;
  background:var(--dark);
  display:flex;flex-direction:column;
  position:fixed;top:0;left:0;bottom:0;z-index:300;
  border-right:1px solid rgba(255,255,255,.06);
  transition:transform .3s cubic-bezier(.4,0,.2,1);
  overflow:hidden;
}
.sb-top{padding:1.5rem 1.4rem 1.2rem;border-bottom:1px solid rgba(255,255,255,.07)}
.sb-logo{display:flex;align-items:center;gap:12px;margin-bottom:1.1rem}
.sb-logo-img{
  width:42px;height:42px;border-radius:10px;overflow:hidden;flex-shrink:0;
  background:linear-gradient(135deg,var(--green),var(--teal));
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 4px 14px rgba(26,107,60,.45);
}
.sb-brand h1{font-family:'Fraunces',serif;font-size:1.1rem;font-weight:600;color:#fff;letter-spacing:-.01em}
.sb-brand p{font-size:.62rem;color:var(--gold);font-weight:600;text-transform:uppercase;letter-spacing:.13em;margin-top:2px}
.sb-meta{display:flex;flex-direction:column;gap:4px}
.sb-meta-item{font-size:.7rem;color:rgba(255,255,255,.4);display:flex;align-items:center;gap:6px}
.sb-meta-item span:first-child{color:rgba(255,255,255,.2)}

.sb-nav{flex:1;padding:1.2rem .8rem;overflow-y:auto;scrollbar-width:none}
.sb-nav::-webkit-scrollbar{display:none}
.sb-section{margin-bottom:1.4rem}
.sb-section-label{font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.14em;
  color:rgba(255,255,255,.25);padding:.2rem .7rem .5rem;display:block}
.sb-item{
  display:flex;align-items:center;gap:10px;width:100%;
  padding:.65rem .85rem;border-radius:var(--radius);
  color:rgba(255,255,255,.55);font-size:.8rem;font-weight:500;
  cursor:pointer;border:none;background:transparent;
  text-align:left;transition:all .18s;position:relative;
  font-family:'Plus Jakarta Sans',sans-serif;
}
.sb-item:hover{background:rgba(255,255,255,.06);color:rgba(255,255,255,.9)}
.sb-item.active{
  background:rgba(26,107,60,.25);color:#fff;
  border-left:3px solid var(--lime);
}
.sb-item.active .sb-icon{color:var(--lime)}
.sb-icon{font-size:1rem;width:20px;text-align:center;flex-shrink:0}
.sb-item .badge{
  margin-left:auto;font-size:.58rem;background:rgba(201,168,76,.2);
  color:var(--gold);padding:2px 7px;border-radius:20px;font-weight:700;
}
.sb-bottom{padding:1rem .8rem 1.4rem;border-top:1px solid rgba(255,255,255,.07)}
#clock-sb{font-family:'JetBrains Mono',monospace;font-size:.65rem;
  color:rgba(255,255,255,.3);text-align:center;padding:.5rem}
.sb-version{font-size:.6rem;color:rgba(255,255,255,.2);text-align:center;margin-top:4px}

/* ══════════════════ MAIN CONTENT ══════════════════ */
#main-wrap{margin-left:var(--sidebar-w);flex:1;min-height:100vh;display:flex;flex-direction:column}

#topbar{
  background:#fff;border-bottom:1px solid var(--border);
  height:62px;display:flex;align-items:center;justify-content:space-between;
  padding:0 2rem;position:sticky;top:0;z-index:100;
  box-shadow:var(--shadow-xs);
}
.tb-left{display:flex;align-items:center;gap:1rem}
.tb-left h2{font-family:'Fraunces',serif;font-size:1.2rem;font-weight:600;color:var(--dark);letter-spacing:-.01em}
.tb-breadcrumb{font-size:.75rem;color:var(--muted)}
.tb-right{display:flex;align-items:center;gap:.7rem}
.badge-ai{
  background:linear-gradient(135deg,var(--gold),#e8c45a);
  color:var(--dark);font-size:.65rem;font-weight:700;
  padding:4px 12px;border-radius:20px;letter-spacing:.04em;text-transform:uppercase;
}
.btn-sm{
  background:transparent;border:1px solid var(--border);color:var(--muted);
  padding:6px 14px;border-radius:var(--radius);font-size:.76rem;cursor:pointer;
  font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;transition:all .2s;
  display:none;
}
.btn-sm:hover{background:var(--bg);color:var(--dark)}

#content{flex:1;padding:2rem 2rem 4rem}

/* ══ UPLOAD ══ */
#upload-section{max-width:700px;margin:4rem auto 0}
.upload-card{
  background:#fff;border:2px dashed var(--border);border-radius:var(--radius-xl);
  padding:3.5rem 2.5rem;text-align:center;cursor:pointer;
  transition:all .25s;box-shadow:var(--shadow-sm);
}
.upload-card:hover,.upload-card.dragover{
  border-color:var(--green);border-style:solid;background:var(--light);
  box-shadow:var(--shadow);transform:translateY(-3px);
}
.up-icon{font-size:3.5rem;margin-bottom:1.2rem}
.upload-card h2{font-family:'Fraunces',serif;font-size:1.7rem;font-weight:600;color:var(--dark);margin-bottom:.5rem}
.upload-card p{color:var(--muted);font-size:.88rem;line-height:1.7}
.col-hint{display:flex;flex-wrap:wrap;justify-content:center;gap:6px;margin-top:1.2rem}
.col-hint code{
  font-family:'JetBrains Mono',monospace;font-size:.7rem;
  background:var(--light);color:var(--green);padding:4px 10px;border-radius:6px;
  border:1px solid rgba(26,107,60,.2);
}
#file-input{display:none}
.btn-primary{
  background:linear-gradient(135deg,var(--green),var(--teal));color:#fff;
  padding:12px 32px;border-radius:var(--radius);margin-top:1.5rem;
  font-weight:700;font-size:.88rem;cursor:pointer;border:none;
  font-family:'Plus Jakarta Sans',sans-serif;letter-spacing:.02em;
  box-shadow:0 4px 18px rgba(26,107,60,.3);transition:all .2s;
  display:inline-flex;align-items:center;gap:8px;
}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 6px 24px rgba(26,107,60,.4)}
.err-banner{
  background:#fff5f5;border:1px solid #fecaca;border-radius:var(--radius);
  padding:12px 16px;margin-bottom:16px;color:var(--red);font-size:.85rem;
  display:flex;align-items:center;gap:8px;
}

/* ══ LOADING ══ */
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

/* ══ DASHBOARD ══ */
#dashboard{display:none;animation:fadeUp .45s ease}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}

.page-header{margin-bottom:1.8rem}
.page-header .ph-label{font-size:.65rem;font-weight:700;color:var(--gold);text-transform:uppercase;letter-spacing:.14em;margin-bottom:.3rem}
.page-header h2{font-family:'Fraunces',serif;font-size:1.7rem;font-weight:600;color:var(--dark);line-height:1.2}
.page-header p{color:var(--muted);font-size:.84rem;margin-top:.3rem}

.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.8rem}
@media(max-width:1200px){.kpi-grid{grid-template-columns:repeat(2,1fr)}}
.kpi{
  background:#fff;border-radius:var(--radius-lg);padding:1.4rem 1.3rem 1.2rem;
  box-shadow:var(--shadow-xs);border:1px solid var(--border);
  position:relative;overflow:hidden;transition:all .22s;
}
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

.dl-bar{
  background:var(--dark);border-radius:var(--radius-lg);padding:1.3rem 1.6rem;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.8rem;
  margin-bottom:1.8rem;box-shadow:var(--shadow);
}
.dl-bar-left{display:flex;align-items:center;gap:14px}
.dl-bar-left .icon{font-size:1.5rem}
.dl-bar-left h3{font-size:.92rem;font-weight:700;color:#fff}
.dl-bar-left p{font-size:.73rem;color:rgba(255,255,255,.45);margin-top:1px}
.dl-btns{display:flex;gap:.6rem;flex-wrap:wrap}
.dl-btn{
  display:flex;align-items:center;gap:7px;
  padding:8px 15px;border-radius:var(--radius);font-size:.75rem;
  font-weight:700;cursor:pointer;border:none;font-family:'Plus Jakarta Sans',sans-serif;
  transition:all .2s;text-decoration:none;
}
.dl-btn:hover{transform:translateY(-1px);filter:brightness(1.08)}
.dl-excel{background:linear-gradient(135deg,#1a6b3c,#0e7c6e);color:#fff}
.dl-stats{background:linear-gradient(135deg,#c9a84c,#e8c45a);color:var(--dark)}
.dl-alert{background:linear-gradient(135deg,#d64045,#e07b39);color:#fff}
.dl-forecast{background:linear-gradient(135deg,#457b9d,#7b5ea7);color:#fff}

.ana-card{
  background:#fff;border-radius:var(--radius-xl);
  border:1px solid var(--border);box-shadow:var(--shadow-xs);
  overflow:hidden;transition:box-shadow .2s;margin-bottom:1.2rem;
}
.ana-card:hover{box-shadow:var(--shadow-sm)}
.ac-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:1rem 1.4rem .8rem;border-bottom:1px solid var(--border);
}
.ac-header-left{display:flex;align-items:center;gap:10px}
.ac-icon{font-size:1.1rem}
.ac-header h3{font-size:.9rem;font-weight:700;color:var(--dark)}
.ac-header p{font-size:.72rem;color:var(--muted);margin-top:1px}
.ac-tag{
  font-size:.62rem;background:var(--light);color:var(--green);
  padding:3px 10px;border-radius:20px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;
  white-space:nowrap;
}
.ac-chart{width:100%;display:block;padding:.6rem .6rem .2rem}
.chart-ph{
  min-height:200px;display:flex;align-items:center;justify-content:center;
  color:var(--muted);font-size:.8rem;flex-direction:column;gap:.5rem;padding:2rem;
}
.chart-ph .phi{font-size:2rem;opacity:.3}

.ac-insight{
  margin:.2rem 1rem 1rem;
  background:linear-gradient(135deg,#f3fbf6,#edf7f2);
  border:1px solid rgba(26,107,60,.13);
  border-radius:var(--radius);padding:1rem 1.2rem;
}
.ac-insight-hdr{display:flex;align-items:center;gap:8px;margin-bottom:.6rem}
.ai-pill{
  font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
  color:var(--green);background:rgba(26,107,60,.1);padding:3px 10px;border-radius:20px;
  display:inline-flex;align-items:center;gap:4px;
}
.ac-insight p{font-size:.82rem;color:#253b2d;line-height:1.8;white-space:pre-wrap}

.cgrid-2{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem}
@media(max-width:1100px){.cgrid-2{grid-template-columns:1fr}}
.full-width{grid-column:1/-1}

.model-table-wrap{
  background:#fff;border-radius:var(--radius-xl);
  border:1px solid var(--border);box-shadow:var(--shadow-xs);overflow:hidden;
  margin-bottom:1.2rem;
}
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

.forecast-table-wrap{
  background:#fff;border-radius:var(--radius-xl);
  border:1px solid var(--border);box-shadow:var(--shadow-xs);overflow:hidden;
  margin-bottom:.8rem;
}
.forecast-table-wrap table{width:100%;border-collapse:collapse;font-size:.83rem}
.forecast-table-wrap thead{background:linear-gradient(135deg,#1a6b3c,#0e7c6e)}
.forecast-table-wrap thead th{padding:.8rem 1.1rem;text-align:left;font-size:.67rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,.8)}
.forecast-table-wrap tbody tr{border-bottom:1px solid var(--border);transition:background .15s}
.forecast-table-wrap tbody tr:last-child{border:none}
.forecast-table-wrap tbody tr:hover{background:#f0faf5}
.forecast-table-wrap tbody td{padding:.75rem 1.1rem;color:var(--text)}
.chg-pos{color:#16a34a;font-weight:700}
.chg-neg{color:var(--red);font-weight:700}

.meta-row{
  background:#fff;border-radius:var(--radius-lg);padding:.9rem 1.4rem;
  border:1px solid var(--border);display:flex;justify-content:space-between;flex-wrap:wrap;
  gap:.5rem;font-size:.72rem;color:var(--muted);align-items:center;margin-top:1.5rem;
}
.meta-row strong{color:var(--dark)}

@media(max-width:900px){
  #sidebar{transform:translateX(-100%)}
  #sidebar.open{transform:translateX(0)}
  #main-wrap{margin-left:0}
}

#toast{
  position:fixed;bottom:24px;right:24px;
  background:var(--dark);color:#fff;padding:12px 20px;border-radius:var(--radius);
  font-size:.8rem;font-weight:600;opacity:0;transition:all .3s;
  pointer-events:none;z-index:999;border-left:3px solid var(--lime);
  box-shadow:var(--shadow-lg);max-width:300px;
}
#toast.show{opacity:1;transform:translateY(-3px)}
#toast.err{border-left-color:var(--red)}

::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
</style>
</head>
<body>

<!-- ══════════════════ LANDING PAGE ══════════════════ -->
<div id="landing">
  <div class="lp-bg"></div>
  <div class="lp-grid-bg"></div>
  <div class="lp-orb lp-orb1"></div>
  <div class="lp-orb lp-orb2"></div>
  <div class="lp-orb lp-orb3"></div>

  <div class="lp-wrap">
    <div class="lp-topbar">
      <div class="lp-brand">
        <div class="lp-brand-icon">
          <svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="44" height="44" rx="12" fill="url(#lpg)"/>
            <text x="21" y="30" text-anchor="middle" font-family="Georgia,serif" font-size="21" font-weight="bold" fill="white">L</text>
            <path d="M27 10 Q36 8 34 19 Q31 13 24 15 Z" fill="rgba(255,255,255,0.7)"/>
            <defs><linearGradient id="lpg" x1="0" y1="0" x2="44" y2="44"><stop offset="0%" stop-color="#1a6b3c"/><stop offset="100%" stop-color="#0e7c6e"/></linearGradient></defs>
          </svg>
        </div>
        <div class="lp-brand-txt">
          <h1>PT London Sumatra Indonesia</h1>
          <p>Lonsum · Tbk · Est. 1906</p>
        </div>
      </div>
      <div class="lp-topbar-right">
        <span class="lp-pill neutral">LEAP v3.1</span>
        <span class="lp-pill gold">&#9889; AI-Powered</span>
      </div>
    </div>

    <div class="lp-main">
      <div class="lp-eyebrow">
        <span class="lp-dot"></span>
        Platform Analitik Perkebunan Enterprise
      </div>

      <h1 class="lp-title">
        LEAP<br/>
        <span class="lp-title-italic">Plantation</span>
        <span class="lp-title-accent"> Intelligence</span>
      </h1>

      <p class="lp-tagline">
        Dashboard kecerdasan buatan untuk <strong>memantau, menganalisis, dan memprediksi</strong>
        produksi kebun Lonsum secara real-time &#8212;
        dirancang untuk semua kalangan, dari manajer lapangan hingga direksi.
      </p>

      <div class="lp-cta-wrap">
        <button class="btn-mulai" onclick="enterDashboard()">
          Mulai Analisis
          <span class="bm-arrow">&#8594;</span>
        </button>
      </div>

      <div class="lp-features">
        <div class="lp-feat"><div class="lf-icon">&#128202;</div><div class="lf-title">KPI Produksi Real-Time</div><div class="lf-desc">Total produksi, produktivitas/ha, estate terbaik, dan bulan puncak otomatis</div></div>
        <div class="lp-feat"><div class="lf-icon">&#129302;</div><div class="lf-title">Insight AI per Grafik</div><div class="lf-desc">Setiap visualisasi dilengkapi analisis otomatis dari AI konsultan Lonsum</div></div>
        <div class="lp-feat"><div class="lf-icon">&#128302;</div><div class="lf-title">Prediksi Bulan Depan</div><div class="lf-desc">Model Machine Learning memprediksi produksi setiap estate dengan interval kepercayaan</div></div>
        <div class="lp-feat"><div class="lf-icon">&#128229;</div><div class="lf-title">Laporan Excel Lengkap</div><div class="lf-desc">File Excel berisi 5 sheet: produksi bulanan, statistik estate, alert, forecast, dan model ML</div></div>
      </div>

      <div class="lp-howto">
        <div class="lp-sec-lbl">Cara Penggunaan</div>
        <div class="lp-steps">
          <div class="lp-step"><div class="step-num">1</div><div class="step-title">Siapkan File CSV</div><div class="step-desc">Ekspor data produksi kebun dalam format CSV dengan kolom yang diperlukan</div></div>
          <div class="lp-step"><div class="step-num">2</div><div class="step-title">Upload Data</div><div class="step-desc">Klik Mulai, lalu drag &amp; drop atau pilih file CSV dari komputer Anda</div></div>
          <div class="lp-step"><div class="step-num">3</div><div class="step-title">Tunggu Proses AI</div><div class="step-desc">Sistem membersihkan data, melatih 3 model ML, dan menghasilkan 10 insight AI</div></div>
          <div class="lp-step"><div class="step-num">4</div><div class="step-title">Analisis &amp; Unduh</div><div class="step-desc">Baca insight di setiap grafik, lalu unduh laporan Excel untuk rapat atau arsip</div></div>
        </div>
      </div>

      <div class="lp-format">
        <div class="lp-format-inner">
          <div class="lp-sec-lbl">Format Kolom CSV yang Diperlukan</div>
          <div class="lp-cols">
            <div class="lp-col-chip"><code>date</code><span>Tanggal (YYYY-MM-DD)</span></div>
            <div class="lp-col-chip"><code>estate</code><span>Nama kebun/estate</span></div>
            <div class="lp-col-chip"><code>plantation_area_ha</code><span>Luas lahan (hektar)</span></div>
            <div class="lp-col-chip"><code>rainfall_mm</code><span>Curah hujan (mm)</span></div>
            <div class="lp-col-chip"><code>workers</code><span>Jumlah tenaga kerja</span></div>
            <div class="lp-col-chip"><code>fertilizer_kg</code><span>Penggunaan pupuk (kg)</span></div>
            <div class="lp-col-chip"><code>production_tons</code><span>Produksi (ton)</span></div>
          </div>
        </div>
      </div>

      <div class="lp-portfolio-credit">
        <span class="port-pre">Dikembangkan oleh</span>
        <span class="port-sep"></span>
        <span class="port-name">Tim Data Analytics &#183; PT London Sumatra Indonesia</span>
        <span class="port-tag">Internal Tools Portfolio</span>
      </div>
    </div>

    <div class="lp-footer">
      <p><strong>Lonsum LEAP</strong> &#8212; Lonsum Enterprise Analytics Platform &#183; Confidential</p>
      <div class="lp-stack-row">
        <span class="lp-stag">FastAPI</span><span class="lp-stag">scikit-learn</span>
        <span class="lp-stag">Matplotlib</span><span class="lp-stag">NVIDIA NIM</span>
        <span class="lp-stag">openpyxl</span>
      </div>
    </div>
  </div>
</div>

<!-- ══════════════════ SIDEBAR ══════════════════ -->
<nav id="sidebar">
  <div class="sb-top">
    <div class="sb-logo">
      <div class="sb-logo-img">
        <svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="42" height="42" rx="10" fill="url(#sbg)"/>
          <text x="21" y="28" text-anchor="middle" font-family="serif" font-size="20" font-weight="bold" fill="white">L</text>
          <path d="M26 12 Q32 10 30 18 Q28 14 22 15 Z" fill="rgba(255,255,255,0.7)"/>
          <defs>
            <linearGradient id="sbg" x1="0" y1="0" x2="42" y2="42">
              <stop offset="0%" stop-color="#1a6b3c"/>
              <stop offset="100%" stop-color="#0e7c6e"/>
            </linearGradient>
          </defs>
        </svg>
      </div>
      <div class="sb-brand">
        <h1>LONSUM LEAP</h1>
        <p>Intelligence Platform</p>
      </div>
    </div>
    <div class="sb-meta">
      <div class="sb-meta-item"><span>&#9201;</span><span id="clock-sb">—</span></div>
      <div class="sb-meta-item"><span>&#128205;</span><span>PT London Sumatra Indonesia</span></div>
    </div>
  </div>

  <div class="sb-nav">
    <div class="sb-section">
      <button class="sb-item" onclick="goHome()" style="margin-bottom:.4rem;border:1px solid rgba(255,255,255,.1);">
        <span class="sb-icon">🏠</span>Kembali ke Beranda
      </button>
    </div>
    <div class="sb-section">
      <span class="sb-section-label">Ringkasan</span>
      <button class="sb-item active" onclick="navTo('sec-overview',this)"><span class="sb-icon">📊</span>Overview &amp; KPI</button>
      <button class="sb-item" onclick="navTo('sec-downloads',this)"><span class="sb-icon">📦</span>Unduh Laporan<span class="badge">4</span></button>
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
      <button class="sb-item" onclick="navTo('sec-forecast',this)"><span class="sb-icon">🔮</span>Forecast Bulan Depan</button>
    </div>
  </div>

  <div class="sb-bottom">
    <div class="sb-version">LEAP v3.1 · scikit-learn · NVIDIA NIM</div>
  </div>
</nav>

<!-- ══════════════════ MAIN ══════════════════ -->
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

    <!-- UPLOAD -->
    <div id="upload-section">
      <div class="upload-card" id="upload-zone"
           onclick="document.getElementById('file-input').click()"
           ondragover="onDrag(event)"
           ondragleave="this.classList.remove('dragover')"
           ondrop="onDrop(event)">
        <div class="up-icon">🌿</div>
        <h2>Upload Data Produksi</h2>
        <p>Drag &amp; drop file CSV ke sini, atau klik untuk pilih file<br/>Mendukung data multi-estate &amp; multi-tahun</p>
        <div class="col-hint">
          <code>date</code><code>estate</code><code>plantation_area_ha</code>
          <code>rainfall_mm</code><code>workers</code><code>fertilizer_kg</code><code>production_tons</code>
        </div>
        <button class="btn-primary" onclick="event.stopPropagation();document.getElementById('file-input').click()">📁 Pilih File CSV</button>
        <input type="file" id="file-input" accept=".csv" onchange="onFileSelect(event)"/>
      </div>
    </div>

    <!-- LOADING -->
    <div id="loading">
      <div class="spinner-wrap"><div class="spinner"></div><div class="spinner-inner"></div></div>
      <div id="load-msg">Memulai pipeline analisis…</div>
      <div class="progress-bar"><div class="progress-fill"></div></div>
      <div class="load-steps">
        <div class="ls" id="s1"><span class="dot"></span>Membaca &amp; membersihkan data CSV</div>
        <div class="ls" id="s2"><span class="dot"></span>Membuat grafik &amp; visualisasi</div>
        <div class="ls" id="s3"><span class="dot"></span>Melatih model prediksi ML</div>
        <div class="ls" id="s4"><span class="dot"></span>Menghasilkan insight AI via LLM</div>
        <div class="ls" id="s5"><span class="dot"></span>Menyiapkan laporan download</div>
      </div>
    </div>

    <!-- DASHBOARD -->
    <div id="dashboard">

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
            <div>
              <h3>Laporan Otomatis Siap Diunduh</h3>
              <p>Semua laporan dibuat dari dataset yang Anda upload — format Excel (.xlsx)</p>
            </div>
          </div>
          <div class="dl-btns">
            <a class="dl-btn dl-excel" href="/api/download/excel" download="Lonsum_ProduksiBulanan.xlsx">📊 Laporan Produksi Bulanan</a>
            <a class="dl-btn dl-stats" href="/api/download/stats" download="Lonsum_StatistikEstate.xlsx">📋 Statistik Estate</a>
            <a class="dl-btn dl-alert" href="/api/download/alerts" download="Lonsum_AlertProduktivitas.xlsx">⚠️ Alert Produktivitas Rendah</a>
            <a class="dl-btn dl-forecast" href="/api/download/forecast" download="Lonsum_Forecast.xlsx">🔮 Forecast Bulan Depan</a>
          </div>
        </div>
      </div>

      <!-- TREND -->
      <div id="sec-trend">
        <div class="section-sep"><span class="sl">📈 Tren &amp; Pola Musiman</span><div class="line"></div></div>
        <div class="ana-card">
          <div class="ac-header">
            <div class="ac-header-left"><span class="ac-icon">📈</span>
              <div><h3>Tren Produksi Bulanan &amp; Rata-rata Bergulir</h3><p>Total produksi per bulan dari seluruh estate, termasuk tren 3 bulan</p></div>
            </div><span class="ac-tag">Time Series</span>
          </div>
          <img id="c-trend" alt="" class="ac-chart" style="display:none"/>
          <div class="chart-ph" id="c-trend-ph"><div class="phi">📈</div><span>Memuat grafik…</span></div>
          <div class="ac-insight" id="ai-trend-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI Analyst</span></div><p>Menganalisis data…</p></div>
        </div>
        <div class="cgrid-2">
          <div class="ana-card">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">📅</span>
                <div><h3>Profil Musiman</h3><p>Rata-rata produksi per bulan dalam setahun</p></div>
              </div><span class="ac-tag">Seasonality</span>
            </div>
            <img id="c-seasonal" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-seasonal-ph"><div class="phi">📅</div><span>Memuat grafik…</span></div>
            <div class="ac-insight" id="ai-seasonal-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis pola musiman…</p></div>
          </div>
          <div class="ana-card" id="sec-estate">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">🏭</span>
                <div><h3>Produksi Tahunan per Estate</h3><p>Perbandingan kontribusi setiap estate per tahun</p></div>
              </div><span class="ac-tag">Stacked Bar</span>
            </div>
            <img id="c-annual" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-annual-ph"><div class="phi">🏭</div><span>Memuat grafik…</span></div>
            <div class="ac-insight" id="ai-annual-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis distribusi estate…</p></div>
          </div>
        </div>
      </div>

      <!-- PRODUCTIVITY -->
      <div id="sec-productivity">
        <div class="section-sep"><span class="sl">🌱 Produktivitas &amp; Distribusi</span><div class="line"></div></div>
        <div class="cgrid-2">
          <div class="ana-card">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">📦</span>
                <div><h3>Distribusi Produksi per Estate</h3><p>Sebaran data produksi bulanan masing-masing estate</p></div>
              </div><span class="ac-tag">Box Plot</span>
            </div>
            <img id="c-boxplot" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-boxplot-ph"><div class="phi">📦</div><span>Memuat grafik…</span></div>
            <div class="ac-insight" id="ai-boxplot-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis distribusi…</p></div>
          </div>
          <div class="ana-card">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">🌱</span>
                <div><h3>Produktivitas per Hektar per Estate</h3><p>Efisiensi lahan — ton yang dihasilkan per hektar kebun</p></div>
              </div><span class="ac-tag">Benchmark</span>
            </div>
            <img id="c-prodha" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-prodha-ph"><div class="phi">🌱</div><span>Memuat grafik…</span></div>
            <div class="ac-insight" id="ai-prodha-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis produktivitas lahan…</p></div>
          </div>
        </div>
      </div>

      <!-- CORRELATION -->
      <div id="sec-correlation">
        <div class="section-sep"><span class="sl">🔗 Korelasi &amp; Driver Produksi</span><div class="line"></div></div>
        <div class="cgrid-2">
          <div class="ana-card">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">🔗</span>
                <div><h3>Matriks Korelasi Antar Faktor</h3><p>Seberapa kuat hubungan antara setiap variabel operasional</p></div>
              </div><span class="ac-tag">Heatmap</span>
            </div>
            <img id="c-corr" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-corr-ph"><div class="phi">🔗</div><span>Memuat grafik…</span></div>
            <div class="ac-insight" id="ai-corr-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis korelasi faktor…</p></div>
          </div>
          <div class="ana-card">
            <div class="ac-header">
              <div class="ac-header-left"><span class="ac-icon">⚙️</span>
                <div><h3>Pengaruh Driver terhadap Produksi</h3><p>Hubungan scatter antara input operasional dan output produksi</p></div>
              </div><span class="ac-tag">Scatter</span>
            </div>
            <img id="c-scatter" alt="" class="ac-chart" style="display:none"/>
            <div class="chart-ph" id="c-scatter-ph"><div class="phi">⚙️</div><span>Memuat grafik…</span></div>
            <div class="ac-insight" id="ai-scatter-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis driver produksi…</p></div>
          </div>
        </div>
      </div>

      <!-- MODEL ML -->
      <div id="sec-model">
        <div class="section-sep"><span class="sl">🤖 Perbandingan Model Machine Learning</span><div class="line"></div></div>
        <div class="model-table-wrap" style="margin-bottom:1.2rem">
          <table>
            <thead><tr><th>Model</th><th>Akurasi (R²)</th><th>Rata-rata Error (MAE)</th><th>RMSE</th><th>Cross-Val R²</th><th>Status</th></tr></thead>
            <tbody id="mtable"></tbody>
          </table>
        </div>
        <div class="ana-card">
          <div class="ac-header">
            <div class="ac-header-left"><span class="ac-icon">🎯</span>
              <div><h3>Model Terbaik — Prediksi vs Aktual</h3><p>Evaluasi akurasi model ML terpilih terhadap data nyata</p></div>
            </div><span class="ac-tag">Evaluation</span>
          </div>
          <img id="c-model" alt="" class="ac-chart" style="display:none"/>
          <div class="chart-ph" id="c-model-ph"><div class="phi">🎯</div><span>Memuat grafik…</span></div>
          <div class="ac-insight" id="ai-model-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI Analyst</span></div><p>Menganalisis performa model…</p></div>
        </div>
      </div>

      <!-- FEATURE IMPORTANCE -->
      <div id="sec-featimp">
        <div class="section-sep"><span class="sl">🏆 Faktor Paling Berpengaruh</span><div class="line"></div></div>
        <div class="ana-card">
          <div class="ac-header">
            <div class="ac-header-left"><span class="ac-icon">🏆</span>
              <div><h3>Peringkat Faktor Penting (Feature Importance)</h3><p>Faktor mana yang paling menentukan hasil produksi menurut model AI</p></div>
            </div><span class="ac-tag">Importance Score</span>
          </div>
          <img id="c-fi" alt="" class="ac-chart" style="display:none"/>
          <div class="chart-ph" id="c-fi-ph"><div class="phi">🏆</div><span>Memuat grafik…</span></div>
          <div class="ac-insight" id="ai-fi-box"><div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI</span></div><p>Menganalisis kepentingan fitur…</p></div>
        </div>
      </div>

      <!-- FORECAST -->
      <div id="sec-forecast">
        <div class="section-sep"><span class="sl">🔮 Forecast Produksi Bulan Depan</span><div class="line"></div></div>
        <div class="ana-card">
          <div class="ac-header">
            <div class="ac-header-left"><span class="ac-icon">🔮</span>
              <div><h3>Prediksi Produksi per Estate — Bulan Depan</h3><p>Hasil prediksi model ML dengan rentang kepercayaan (confidence interval)</p></div>
            </div><span class="ac-tag">Prediction</span>
          </div>
          <img id="c-forecast" alt="" class="ac-chart" style="display:none"/>
          <div class="chart-ph" id="c-forecast-ph"><div class="phi">🔮</div><span>Memuat grafik…</span></div>
        </div>
        <div class="forecast-table-wrap" id="forecast-table-wrap" style="display:none">
          <table>
            <thead><tr><th>Estate</th><th>Prediksi (ton)</th><th>Batas Bawah</th><th>Batas Atas</th><th>Aktual Bulan Lalu</th><th>Perubahan (%)</th><th>Selisih (ton)</th></tr></thead>
            <tbody id="forecast-tbody"></tbody>
          </table>
        </div>
        <div class="ac-insight" id="ai-forecast-box" style="margin-top:.5rem">
          <div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI Analyst</span></div>
          <p>Menganalisis forecast…</p>
        </div>
      </div>

      <div class="meta-row">
        <span>Dibuat: <strong id="meta-date"></strong></span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:.68rem">PT London Sumatra Indonesia · LEAP Analytics v3.1</span>
        <span id="meta-records"></span>
      </div>
    </div><!-- /dashboard -->
  </div><!-- /content -->
</div><!-- /main-wrap -->

<div id="toast"></div>

<script>
(function tick(){
  var d=new Date();
  var s=d.toLocaleDateString('id-ID',{weekday:'short',day:'2-digit',month:'short',year:'numeric'})
    +' · '+d.toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
  var e=document.getElementById('clock-sb');if(e)e.textContent=s;
  setTimeout(tick,1000);
})();

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
    img.onerror=function(){img.style.display='none';if(ph){ph.querySelector('span').textContent='Grafik tidak tersedia.';ph.style.display='flex';}};
    img.src='data:image/png;base64,'+b64;
  }else{
    img.style.display='none';
    if(ph){ph.querySelector('span').textContent='Data tidak tersedia.';ph.style.display='flex';}
  }
}
function setInsight(boxId,text){
  var box=document.getElementById(boxId);if(!box)return;
  var t=(text&&text.length>10)?text:'Insight AI tidak tersedia untuk sesi ini.';
  box.innerHTML='<div class="ac-insight-hdr"><span class="ai-pill">🤖 Insight AI Analyst</span></div><p>'+esc(t)+'</p>';
}

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

function onDrag(e){e.preventDefault();document.getElementById('upload-zone').classList.add('dragover');}
function onDrop(e){e.preventDefault();document.getElementById('upload-zone').classList.remove('dragover');var f=e.dataTransfer.files[0];if(f)doUpload(f);}
function onFileSelect(e){var f=e.target.files[0];if(f)doUpload(f);}

function showErr(msg){
  var z=document.getElementById('upload-zone');
  var old=z.querySelector('.err-banner');if(old)old.remove();
  var d=document.createElement('div');d.className='err-banner';
  d.innerHTML='⚠️ '+esc(msg);z.insertBefore(d,z.firstChild);
}

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
    .then(function(res){
      var st=res.status;
      return res.text().then(function(txt){return{st:st,txt:txt};});
    })
    .then(function(obj){
      if(obj.st!==200){
        var em='Server error '+obj.st;
        try{var p=JSON.parse(obj.txt);em=p.detail||em;}catch(e){}
        throw new Error(em);
      }
      var data;try{data=JSON.parse(obj.txt);}
      catch(e){throw new Error('Response parse gagal. Cek console browser (F12).');}
      renderDash(data);
    })
    .catch(function(err){
      clearSteps();
      document.getElementById('loading').style.display='none';
      document.getElementById('upload-section').style.display='';
      showErr(err.message);toast(err.message,'err');
    });
}

function renderDash(data){
  try{
    var k=data.kpis||{};
    document.getElementById('topbar-title').textContent='Dashboard Produksi';
    document.getElementById('topbar-sub').textContent='Periode: '+(k.date_range||'—')+' · '+(k.num_estates||0)+' Estate';
    document.getElementById('kpi-sub').textContent='Periode: '+(k.date_range||'—')+'  ·  '+(k.num_estates||0)+' Estate  ·  '+fmt(k.total_records)+' Record Data';

    var cards=[
      {icon:'🌿',lbl:'Total Produksi',val:fmt(k.total_production_tons)+' ton',sub:'Seluruh estate',acc:'g',chg:'neu',chgt:'—'},
      {icon:'📐',lbl:'Rata-rata Produktivitas',val:fmt(k.avg_productivity_t_ha)+' t/ha',sub:'Ton per hektar lahan',acc:'gold',chg:'neu',chgt:'—'},
      {icon:'🏆',lbl:'Estate Terbaik',val:esc(k.best_estate||'—'),sub:'Produksi tertinggi',acc:'teal',chg:'pos',chgt:'Top'},
      {icon:'📅',lbl:'Bulan Puncak',val:esc(k.peak_month||'—'),sub:'Produksi rata-rata tertinggi',acc:'g',chg:'neu',chgt:'—'},
      {icon:'🏭',lbl:'Jumlah Estate',val:k.num_estates||0,sub:'Kebun yang dipantau',acc:'teal',chg:'neu',chgt:'—'},
      {icon:'📋',lbl:'Total Record',val:fmt(k.total_records),sub:'Baris data diproses',acc:'red',chg:'neu',chgt:'—'},
    ];
    document.getElementById('kpi-grid').innerHTML=cards.map(function(c){
      return '<div class="kpi"><div class="kpi-accent '+c.acc+'"></div>'+
        '<div class="kpi-top"><div class="kpi-icon-wrap">'+c.icon+'</div>'+
        '<span class="kpi-change '+c.chg+'">'+c.chgt+'</span></div>'+
        '<div class="kpi-val">'+c.val+'</div>'+
        '<div class="kpi-label">'+c.lbl+'</div>'+
        '<div class="kpi-sub">'+c.sub+'</div></div>';
    }).join('');

    var ch=data.charts||{};
    setImg('c-trend',ch.trend);setImg('c-seasonal',ch.seasonal);setImg('c-annual',ch.annual);
    setImg('c-boxplot',ch.boxplot);setImg('c-prodha',ch.prodha);setImg('c-corr',ch.corr);
    setImg('c-scatter',ch.scatter);setImg('c-model',ch.model_eval);
    setImg('c-fi',ch.feature_imp);setImg('c-forecast',ch.forecast);

    var ai=data.ai_insights||{};
    setInsight('ai-trend-box',ai.trend);setInsight('ai-seasonal-box',ai.seasonal);
    setInsight('ai-annual-box',ai.annual);setInsight('ai-boxplot-box',ai.boxplot);
    setInsight('ai-prodha-box',ai.prodha);setInsight('ai-corr-box',ai.correlation);
    setInsight('ai-scatter-box',ai.scatter);setInsight('ai-model-box',ai.model);
    setInsight('ai-fi-box',ai.feature_importance);setInsight('ai-forecast-box',ai.forecast);

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

    var fcData=data.forecast_data||[];
    if(fcData.length>0){
      document.getElementById('forecast-table-wrap').style.display='';
      document.getElementById('forecast-tbody').innerHTML=fcData.map(function(r){
        var chg=parseFloat(r.change_pct||0);
        return '<tr><td><strong>'+esc(r.estate)+'</strong></td>'+
          '<td><strong>'+fmt(r.forecast_tons)+'</strong></td>'+
          '<td>'+fmt(r.lower_bound)+'</td><td>'+fmt(r.upper_bound)+'</td>'+
          '<td>'+fmt(r.last_actual)+'</td>'+
          '<td class="'+(chg>=0?'chg-pos':'chg-neg')+'">'+(chg>=0?'▲ ':'▼ ')+Math.abs(chg).toFixed(1)+'%</td>'+
          '<td class="'+(chg>=0?'chg-pos':'chg-neg')+'">'+(function(){var d=parseFloat(r.forecast_tons)-parseFloat(r.last_actual);return(d>=0?'+':'')+d.toFixed(1)+' ton';})()+'</td></tr>';
      }).join('');
    }

    document.getElementById('meta-date').textContent=data.generated_at||'—';
    document.getElementById('meta-records').textContent='Model terbaik: '+esc(best);
    clearSteps();
    document.getElementById('loading').style.display='none';
    document.getElementById('dashboard').style.display='block';
    document.getElementById('btn-reset').style.display='inline-flex';
    window.scrollTo({top:0,behavior:'smooth'});
    toast('Dashboard berhasil dimuat — '+Object.keys(ch).length+' grafik ditampilkan');
  }catch(err){
    console.error('[renderDash]',err);
    clearSteps();
    document.getElementById('loading').style.display='none';
    document.getElementById('upload-section').style.display='';
    showErr('Render error: '+err.message);toast('Render error: '+err.message,'err');
  }
}

function enterDashboard(){
  var lp=document.getElementById('landing');
  lp.classList.add('exit');
  setTimeout(function(){lp.style.display='none';},620);
}
function goHome(){
  var lp=document.getElementById('landing');
  lp.style.display='';lp.classList.remove('exit');
  lp.style.opacity='';lp.style.transform='';
  window.scrollTo({top:0,behavior:'smooth'});
}
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


# ==============================================================================
# NVIDIA LLM
# ==============================================================================
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
        "temperature": 0.45,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=60.0) as client:
            r = client.post(NVIDIA_BASE_URL, json=payload, headers=headers)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[LLM ERROR] {type(e).__name__}: {e}")
        return f"AI insight tidak tersedia ({type(e).__name__}). Pastikan API key dan koneksi aktif."


def fig_b64(fig, dpi=130) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=dpi)
    buf.seek(0)
    enc = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    buf.close()
    return enc


# ==============================================================================
# EXCEL HELPER STYLES
# ==============================================================================
def _hfont(color="FFFFFF"):
    return Font(bold=True, color=color, name="Calibri", size=10)

def _hfill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color.lstrip("#"))

def _dfill(alt=False) -> PatternFill:
    return PatternFill("solid", fgColor="F0FAF5" if alt else "FFFFFF")

_CENTER = Alignment(horizontal="center", vertical="center")
_THIN   = Border(
    left=Side(style="thin", color="D1DDE8"), right=Side(style="thin", color="D1DDE8"),
    top=Side(style="thin", color="D1DDE8"),  bottom=Side(style="thin", color="D1DDE8"),
)

def _apply_header(ws, row_num: int, cols: int, fill_hex: str):
    for c in range(1, cols + 1):
        cell = ws.cell(row=row_num, column=c)
        cell.font = _hfont(); cell.fill = _hfill(fill_hex)
        cell.alignment = _CENTER; cell.border = _THIN

def _apply_data_row(ws, row_num: int, cols: int, alt=False):
    for c in range(1, cols + 1):
        cell = ws.cell(row=row_num, column=c)
        cell.fill = _dfill(alt); cell.border = _THIN; cell.alignment = _CENTER

def _set_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

def _title_row(ws, text: str, cols: int, fill_hex="0a1628", row=1, height=30):
    ws.merge_cells(f"A{row}:{get_column_letter(cols)}{row}")
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(bold=True, name="Calibri", size=13, color="FFFFFF")
    cell.fill = _hfill(fill_hex); cell.alignment = _CENTER
    ws.row_dimensions[row].height = height

def _subtitle_row(ws, text: str, cols: int, row=2):
    ws.merge_cells(f"A{row}:{get_column_letter(cols)}{row}")
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(italic=True, name="Calibri", size=9, color="64748b")
    cell.alignment = _CENTER; ws.row_dimensions[row].height = 16


# ==============================================================================
# EXCEL BUILDER  — BUG FIX: generated_at now comes from kpis dict
# ==============================================================================
def build_excel(df: pd.DataFrame, kpis: dict, model_results: list,
                forecast_df: pd.DataFrame, alerts_df: pd.DataFrame) -> bytes:

    # ── Pull shared metadata ──
    generated_at = kpis.get("generated_at", datetime.now().strftime("%d %B %Y, %H:%M"))
    date_range   = kpis.get("date_range", "—")
    best_model   = model_results[0]["model"] if model_results else "—"

    wb = Workbook()

    # ══════════════════════════════════════════════════════════
    # SHEET 1 — Monthly Production
    # ══════════════════════════════════════════════════════════
    ws1 = wb.active
    ws1.title = "Laporan Produksi Bulanan"
    ws1.sheet_properties.tabColor = "1a6b3c"

    _title_row(ws1, "PT LONDON SUMATRA INDONESIA — LAPORAN PRODUKSI BULANAN", 8, fill_hex="1a6b3c")
    _subtitle_row(ws1, f"Periode: {date_range}  |  Dibuat: {generated_at}", 8)

    headers1 = ["Tahun", "Bulan", "Estate", "Luas Lahan (ha)",
                "Curah Hujan (mm)", "Tenaga Kerja", "Pupuk (kg)", "Produksi (ton)"]
    for i, h in enumerate(headers1, 1):
        ws1.cell(row=4, column=i, value=h)
    _apply_header(ws1, 4, 8, "1a6b3c")

    md = df[["year", "month", "month_name", "estate",
             "plantation_area_ha", "rainfall_mm", "workers",
             "fertilizer_kg", "production_tons"]].copy()
    md = md.sort_values(["year", "month", "estate"]).reset_index(drop=True)

    for ri, row in md.iterrows():
        r = ri + 5
        ws1.cell(r, 1, int(row["year"]))
        ws1.cell(r, 2, str(row["month_name"]))
        ws1.cell(r, 3, str(row["estate"]))
        ws1.cell(r, 4, round(float(row["plantation_area_ha"]), 2))
        ws1.cell(r, 5, round(float(row["rainfall_mm"]), 1))
        ws1.cell(r, 6, int(row["workers"]))
        ws1.cell(r, 7, round(float(row["fertilizer_kg"]), 1))
        ws1.cell(r, 8, round(float(row["production_tons"]), 2))
        _apply_data_row(ws1, r, 8, alt=(ri % 2 == 0))

    total_row = 5 + len(md)
    ws1.cell(total_row, 1, "TOTAL")
    ws1.cell(total_row, 8, round(float(df["production_tons"].sum()), 2))
    for c in range(1, 9):
        cell = ws1.cell(total_row, c)
        cell.font = Font(bold=True, name="Calibri", size=10, color="065f46")
        cell.fill = _hfill("D1FAE5"); cell.border = _THIN; cell.alignment = _CENTER

    _set_widths(ws1, [8, 10, 20, 18, 18, 15, 16, 18])

    # ══════════════════════════════════════════════════════════
    # SHEET 2 — Estate Statistics
    # ══════════════════════════════════════════════════════════
    ws2 = wb.create_sheet("Statistik Estate")
    ws2.sheet_properties.tabColor = "0e7c6e"

    _title_row(ws2, "STATISTIK PERFORMA ESTATE — PT LONDON SUMATRA INDONESIA", 10, fill_hex="0e7c6e")
    _subtitle_row(ws2, f"Periode: {date_range}  |  Dibuat: {generated_at}", 10)

    headers2 = ["Estate", "Total Produksi (ton)", "Rata-rata Bulanan (ton)",
                "Maks (ton)", "Min (ton)", "Std Deviasi",
                "Produktivitas (t/ha)", "Curah Hujan (mm)", "Tenaga Kerja", "Record"]
    for i, h in enumerate(headers2, 1):
        ws2.cell(row=4, column=i, value=h)
    _apply_header(ws2, 4, 10, "0e7c6e")

    stats = df.groupby("estate").agg(
        total=("production_tons", "sum"), avg=("production_tons", "mean"),
        mx=("production_tons", "max"), mn=("production_tons", "min"),
        std=("production_tons", "std"), prod_ha=("productivity_ton_per_ha", "mean"),
        rain=("rainfall_mm", "mean"), workers=("workers", "mean"),
        count=("production_tons", "count"),
    ).round(2).reset_index()

    for ri, row in stats.iterrows():
        r = ri + 5
        vals = [str(row["estate"]), row["total"], row["avg"], row["mx"],
                row["mn"], row["std"], row["prod_ha"], row["rain"],
                round(float(row["workers"]), 0), int(row["count"])]
        for ci, v in enumerate(vals, 1):
            ws2.cell(r, ci, v)
        _apply_data_row(ws2, r, 10, alt=(ri % 2 == 0))

    _set_widths(ws2, [20, 22, 22, 16, 16, 14, 20, 20, 16, 10])

    # ══════════════════════════════════════════════════════════
    # SHEET 3 — Low Productivity Alerts
    # ══════════════════════════════════════════════════════════
    ws3 = wb.create_sheet("Alert Produktivitas Rendah")
    ws3.sheet_properties.tabColor = "d64045"

    avg_prod_ha = float(df["productivity_ton_per_ha"].mean())
    threshold   = avg_prod_ha * 0.75

    _title_row(ws3, "ALERT PRODUKTIVITAS RENDAH — PT LONDON SUMATRA INDONESIA", 7, fill_hex="d64045")
    _subtitle_row(ws3, f"Threshold: < {threshold:.3f} t/ha (75% rata-rata fleet: {avg_prod_ha:.3f} t/ha) | Dibuat: {generated_at}", 7)

    headers3 = ["Tanggal", "Estate", "Produksi (ton)", "Luas (ha)",
                "Produktivitas (t/ha)", "Rata-rata Fleet (t/ha)", "Defisit (%)"]
    for i, h in enumerate(headers3, 1):
        ws3.cell(row=4, column=i, value=h)
    _apply_header(ws3, 4, 7, "d64045")

    if len(alerts_df) > 0:
        for ri, (_, row) in enumerate(alerts_df.iterrows()):
            r = ri + 5
            pv = float(row["productivity_ton_per_ha"])
            deficit = round((avg_prod_ha - pv) / avg_prod_ha * 100, 1)
            try:
                date_str = row["date"].strftime("%b %Y")
            except Exception:
                date_str = str(row["date"])
            ws3.cell(r, 1, date_str); ws3.cell(r, 2, str(row["estate"]))
            ws3.cell(r, 3, round(float(row["production_tons"]), 2))
            ws3.cell(r, 4, round(float(row["plantation_area_ha"]), 2))
            ws3.cell(r, 5, round(pv, 4)); ws3.cell(r, 6, round(avg_prod_ha, 4))
            ws3.cell(r, 7, deficit)
            _apply_data_row(ws3, r, 7, alt=(ri % 2 == 0))
            if deficit > 40:
                for c in range(1, 8):
                    ws3.cell(r, c).fill = _hfill("FEE2E2")
    else:
        ws3.merge_cells("A5:G5")
        ws3.cell(5, 1, "Tidak ada estate dengan produktivitas di bawah threshold.")
        ws3.cell(5, 1).alignment = _CENTER
        ws3.cell(5, 1).font = Font(italic=True, name="Calibri", size=10, color="64748b")

    _set_widths(ws3, [14, 20, 16, 14, 20, 22, 14])

    # ══════════════════════════════════════════════════════════
    # SHEET 4 — Forecast
    # ══════════════════════════════════════════════════════════
    ws4 = wb.create_sheet("Forecast Bulan Depan")
    ws4.sheet_properties.tabColor = "c9a84c"

    _title_row(ws4, "FORECAST PRODUKSI BULAN DEPAN — PT LONDON SUMATRA INDONESIA", 8, fill_hex="c9a84c")
    _subtitle_row(ws4, f"Model: {best_model}  |  Dibuat: {generated_at}  |  Periode: {date_range}", 8)

    headers4 = ["Estate", "Prediksi (ton)", "Batas Bawah (ton)", "Batas Atas (ton)",
                "Aktual Bulan Lalu (ton)", "Selisih (ton)", "Perubahan (%)", "Status"]
    for i, h in enumerate(headers4, 1):
        ws4.cell(row=4, column=i, value=h)
    _apply_header(ws4, 4, 8, "c9a84c")

    for ri, row in enumerate(forecast_df.itertuples()):
        r = ri + 5
        chg = float(row.change_pct)
        delta = round(float(row.forecast_tons) - float(row.last_actual), 2)
        status = "NAIK" if chg >= 0 else "TURUN"
        vals = [str(row.estate), round(float(row.forecast_tons), 2),
                round(float(row.lower_bound), 2), round(float(row.upper_bound), 2),
                round(float(row.last_actual), 2),
                f"+{delta}" if delta >= 0 else str(delta),
                f"+{chg}%" if chg >= 0 else f"{chg}%", status]
        for ci, v in enumerate(vals, 1):
            ws4.cell(r, ci, v)
        _apply_data_row(ws4, r, 8, alt=(ri % 2 == 0))
        txt_c = "065f46" if chg >= 0 else "991b1b"
        bg_c  = "D1FAE5" if chg >= 0 else "FEE2E2"
        for c in [6, 7, 8]:
            ws4.cell(r, c).fill = _hfill(bg_c)
            ws4.cell(r, c).font = Font(bold=True, name="Calibri", color=txt_c)

    _set_widths(ws4, [20, 16, 18, 18, 22, 16, 16, 12])

    # ══════════════════════════════════════════════════════════
    # SHEET 5 — ML Results
    # ══════════════════════════════════════════════════════════
    ws5 = wb.create_sheet("Hasil Model ML")
    ws5.sheet_properties.tabColor = "457b9d"

    _title_row(ws5, "PERFORMA MODEL MACHINE LEARNING — PT LONDON SUMATRA INDONESIA", 6)
    _subtitle_row(ws5, f"Dibuat: {generated_at}  |  Model terbaik: {best_model}", 6)

    headers5 = ["Model", "Akurasi (R2)", "MAE (ton)", "RMSE (ton)", "Cross-Val R2", "Peringkat"]
    for i, h in enumerate(headers5, 1):
        ws5.cell(row=4, column=i, value=h)
    _apply_header(ws5, 4, 6, "0a1628")

    for ri, m in enumerate(model_results):
        r = ri + 5
        ws5.cell(r, 1, m["model"]); ws5.cell(r, 2, m["r2"])
        ws5.cell(r, 3, m["mae"]);   ws5.cell(r, 4, m["rmse"])
        ws5.cell(r, 5, m["cv_r2"]); ws5.cell(r, 6, ri + 1)
        _apply_data_row(ws5, r, 6, alt=(ri % 2 == 0))
        if ri == 0:
            for c in range(1, 7):
                ws5.cell(r, c).fill = _hfill("D1FAE5")
                ws5.cell(r, c).font = Font(bold=True, name="Calibri", color="065f46")

    _set_widths(ws5, [26, 14, 14, 14, 14, 12])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


# ==============================================================================
# MATPLOTLIB STYLE
# ==============================================================================
def setup_mpl():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.22, "grid.color": "#94a3b8", "grid.linestyle": "--",
        "axes.labelcolor": "#1a2535", "xtick.color": "#64748b", "ytick.color": "#64748b",
        "axes.titlepad": 12, "axes.titlesize": 12, "axes.labelsize": 9,
        "figure.facecolor": "white", "axes.facecolor": "#fafbfd",
    })
    sns.set_palette(PALETTE)


# ==============================================================================
# CORE PIPELINE
# ==============================================================================
def process_dataset(raw: pd.DataFrame) -> dict:
    global _last_result
    setup_mpl()

    df = raw.copy()
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)
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

    MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    estates      = sorted(df["estate"].unique().tolist())
    total_prod   = float(df["production_tons"].sum())
    avg_prod_ha  = float(df["productivity_ton_per_ha"].mean())
    best_estate  = str(df.groupby("estate")["production_tons"].sum().idxmax())
    peak_m_num   = int(df.groupby("month")["production_tons"].mean().idxmax())
    peak_month   = MONTH_LABELS[peak_m_num - 1]
    date_range   = df["date"].min().strftime("%b %Y") + " – " + df["date"].max().strftime("%b %Y")
    generated_at = datetime.now().strftime("%d %B %Y, %H:%M")

    # ── PENTING: generated_at harus ada di dalam kpis ──
    kpis = dict(
        total_production_tons=round(total_prod, 1),
        avg_productivity_t_ha=round(avg_prod_ha, 4),
        best_estate=best_estate, peak_month=peak_month,
        total_records=int(len(df)), date_range=date_range,
        estates=estates, num_estates=int(len(estates)),
        generated_at=generated_at,   # ← FIX: wajib ada di sini agar download Excel tidak error
    )

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
        results.append(dict(
            model=nm, mae=round(float(mean_absolute_error(yte, yp)), 3),
            rmse=round(float(np.sqrt(mean_squared_error(yte, yp))), 3),
            r2=round(float(r2_score(yte, yp)), 4),
            cv_r2=round(float(cross_val_score(mdl, X, y, cv=5, scoring="r2").mean()), 4),
        ))
        trained[nm] = (mdl, yp)
    results_sorted = sorted(results, key=lambda x: x["r2"], reverse=True)
    best_name      = results_sorted[0]["model"]
    best_mdl, best_pred = trained[best_name]

    fi_series = None; fi_out = {}
    if hasattr(best_mdl, "feature_importances_"):
        fi_series = pd.Series(best_mdl.feature_importances_, index=FEATURES)
    elif hasattr(best_mdl, "coef_"):
        coef = np.abs(best_mdl.coef_); coef = coef / coef.sum()
        fi_series = pd.Series(coef, index=FEATURES)
    if fi_series is not None:
        fi_out = {k: float(v) for k, v in fi_series.sort_values(ascending=False).items()}

    # ── Forecast ──
    last_date  = df["date"].max()
    next_month = (last_date + timedelta(days=32)).replace(day=1)
    forecast_rows = []
    for est in estates:
        sub = df[df["estate"] == est]; last_row = sub.sort_values("date").iloc[-1]
        feat_vec = pd.DataFrame([{
            "plantation_area_ha": last_row["plantation_area_ha"],
            "rainfall_mm": sub["rainfall_mm"].mean(), "workers": last_row["workers"],
            "fertilizer_kg": sub["fertilizer_kg"].mean(), "month": next_month.month,
            "quarter": (next_month.month - 1) // 3 + 1,
            "estate_encoded": int(last_row["estate_encoded"]),
        }])
        pred = float(best_mdl.predict(feat_vec[FEATURES])[0])
        last_actual = float(last_row["production_tons"])
        mae_val = results_sorted[0]["mae"]
        forecast_rows.append({
            "estate": est, "forecast_tons": round(pred, 2),
            "lower_bound": round(pred - mae_val, 2), "upper_bound": round(pred + mae_val, 2),
            "last_actual": round(last_actual, 2),
            "change_pct": round((pred - last_actual) / last_actual * 100, 1),
        })
    forecast_df = pd.DataFrame(forecast_rows)

    threshold = avg_prod_ha * 0.75
    alerts_df = df[df["productivity_ton_per_ha"] < threshold].sort_values("productivity_ton_per_ha").reset_index(drop=True)

    # ─────────────────────────────────────────────────────────
    # CHARTS
    # ─────────────────────────────────────────────────────────

    # 1 — Trend
    monthly = df.groupby("date")["production_tons"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(18, 5.5))
    ax.fill_between(monthly["date"], monthly["production_tons"], alpha=0.1, color=C_GREEN)
    ax.plot(monthly["date"], monthly["production_tons"], color=C_GREEN, lw=2, marker="o", markersize=3.5, zorder=4, label="Total Bulanan")
    roll = monthly["production_tons"].rolling(3, min_periods=1).mean()
    ax.plot(monthly["date"], roll, color=C_GOLD, lw=2.5, ls="--", zorder=5, label="Rata-rata 3 Bulan")
    ax.set_title("Tren Produksi Bulanan & Rata-rata Bergulir", fontsize=13, fontweight="bold", color=C_DARK)
    ax.set_xlabel("Tanggal"); ax.set_ylabel("Produksi (ton)")
    ax.legend(fontsize=9); ax.tick_params(axis="x", rotation=25)
    fig.tight_layout(pad=1.5)
    c_trend = fig_b64(fig, dpi=140)

    # 2 — Seasonal
    mavg = df.groupby("month")["production_tons"].mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(mavg.index, mavg.values, width=0.65, edgecolor="white",
                  color=[C_RED if v == mavg.min() else (C_LIME if v == mavg.max() else C_TEAL) for v in mavg.values], zorder=3)
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(MONTH_LABELS)
    ax.axhline(mavg.mean(), color=C_GOLD, ls="--", lw=1.5, label=f"Rata-rata ({mavg.mean():.1f}t)", zorder=4)
    ax.set_title("Profil Musiman — Rata-rata Produksi per Bulan", fontsize=13, fontweight="bold", color=C_DARK)
    ax.set_ylabel("Produksi Rata-rata (ton)"); ax.legend(fontsize=9)
    for bar, val in zip(bars, mavg.values):
        ax.text(bar.get_x()+bar.get_width()/2, val+mavg.max()*0.01, f"{val:.0f}", ha="center", va="bottom", fontsize=8, fontweight="600", color=C_DARK)
    fig.tight_layout(pad=1.5)
    c_seasonal = fig_b64(fig, dpi=140)

    # 3 — Annual stacked
    piv = df.groupby(["year","estate"])["production_tons"].sum().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    piv.plot(kind="bar", stacked=True, ax=ax, color=PALETTE[:len(piv.columns)], edgecolor="white", width=0.6)
    ax.set_title("Produksi Tahunan per Estate", fontsize=13, fontweight="bold", color=C_DARK)
    ax.set_xlabel("Tahun"); ax.set_ylabel("Total Produksi (ton)")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Estate", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    fig.tight_layout(pad=1.5)
    c_annual = fig_b64(fig, dpi=140)

    # 4 — Boxplot
    eo = df.groupby("estate")["production_tons"].median().sort_values(ascending=False).index
    fig, ax = plt.subplots(figsize=(10, 5))
    bp = ax.boxplot([df[df["estate"]==e]["production_tons"].values for e in eo],
                    patch_artist=True, labels=eo, widths=0.55,
                    medianprops=dict(color=C_GOLD, lw=2.5),
                    whiskerprops=dict(color=C_GRAY), capprops=dict(color=C_GRAY),
                    flierprops=dict(marker="o", color=C_RED, markersize=4, alpha=0.5))
    for i, p in enumerate(bp["boxes"]):
        p.set_facecolor(PALETTE[i % len(PALETTE)]); p.set_alpha(0.7)
    ax.set_title("Distribusi Produksi per Estate", fontsize=13, fontweight="bold", color=C_DARK)
    ax.set_xlabel("Estate"); ax.set_ylabel("Produksi (ton)"); ax.tick_params(axis="x", rotation=20)
    fig.tight_layout(pad=1.5)
    c_boxplot = fig_b64(fig, dpi=140)

    # 5 — Prod/ha
    pha = df.groupby("estate")["productivity_ton_per_ha"].mean().sort_values()
    thr2 = float(pha.mean())
    fig, ax = plt.subplots(figsize=(10, 5))
    colors_ph = [C_RED if v < thr2 else C_GREEN for v in pha.values]
    bars_ph = ax.barh(pha.index, pha.values, color=colors_ph, edgecolor="white", height=0.55)
    ax.axvline(thr2, color=C_GOLD, ls="--", lw=2, label=f"Rata-rata ({thr2:.3f})", zorder=4)
    ax.set_title("Rata-rata Produktivitas per Hektar per Estate", fontsize=13, fontweight="bold", color=C_DARK)
    ax.set_xlabel("Ton / Hektar"); ax.legend(fontsize=9)
    for bar in bars_ph:
        v = bar.get_width()
        ax.text(v+thr2*0.01, bar.get_y()+bar.get_height()/2, f"{v:.3f}", va="center", fontsize=8.5, fontweight="600", color=C_DARK)
    fig.tight_layout(pad=1.5)
    c_prodha = fig_b64(fig, dpi=140)

    # 6 — Correlation
    ccols = ["plantation_area_ha","rainfall_mm","workers","fertilizer_kg","productivity_ton_per_ha","production_tons"]
    corr = df[ccols].corr()
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(10, 150, s=80, as_cmap=True)
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap=cmap, ax=axes[0],
                linewidths=0.5, cbar_kws={"shrink": 0.8}, vmin=-1, vmax=1, annot_kws={"size": 9, "weight": "600"})
    axes[0].set_title("Matriks Korelasi Antar Faktor", fontsize=12, fontweight="bold", color=C_DARK)
    cp = corr["production_tons"].drop("production_tons").sort_values()
    axes[1].barh(cp.index, cp.values, color=[C_RED if v < 0 else C_GREEN for v in cp.values], edgecolor="white", height=0.6)
    axes[1].axvline(0, color=C_DARK, lw=1)
    axes[1].set_title("Korelasi dengan Produksi", fontsize=12, fontweight="bold", color=C_DARK)
    axes[1].set_xlabel("Koefisien Pearson")
    for i, v in enumerate(cp.values):
        axes[1].text(v+(0.015 if v>=0 else -0.015), i, f"{v:+.3f}", va="center",
                     ha="left" if v>=0 else "right", fontsize=9, fontweight="700",
                     color=C_GREEN if v>=0 else C_RED)
    fig.tight_layout(pad=1.5)
    c_corr = fig_b64(fig, dpi=140)

    # 7 — Scatter
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Driver Produksi — Analisis Scatter", fontsize=14, fontweight="bold", color=C_DARK, y=1.01)
    pairs = [("rainfall_mm","Curah Hujan (mm)",C_TEAL),("fertilizer_kg","Pupuk (kg)",C_GOLD),
             ("workers","Jumlah Tenaga Kerja",C_NAVY),("plantation_area_ha","Luas Lahan (ha)",C_GREEN)]
    for ax, (x, xl, col) in zip(axes.flatten(), pairs):
        ax.scatter(df[x], df["production_tons"], alpha=0.45, color=col, s=18, zorder=3, edgecolors="white", linewidths=0.3)
        z = np.polyfit(df[x], df["production_tons"], 1)
        xr = np.linspace(float(df[x].min()), float(df[x].max()), 200)
        ax.plot(xr, np.poly1d(z)(xr), color=C_RED, lw=2, ls="--", label="Tren", zorder=4)
        r = float(df[[x,"production_tons"]].corr().iloc[0,1])
        ax.set_xlabel(xl); ax.set_ylabel("Produksi (ton)")
        ax.set_title(f"{xl}  (r = {r:+.3f})", fontsize=10, fontweight="bold", color=C_DARK)
        ax.legend(fontsize=8)
    fig.tight_layout(pad=1.5)
    c_scatter = fig_b64(fig, dpi=140)

    # 8 — Model eval
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f"Evaluasi Model Terbaik — {best_name}", fontsize=13, fontweight="bold", color=C_DARK)
    mn2 = float(min(float(yte.min()), float(best_pred.min())))
    mx2 = float(max(float(yte.max()), float(best_pred.max())))
    axes[0].scatter(yte, best_pred, alpha=0.55, color=C_GREEN, s=22, zorder=3, edgecolors="white", linewidths=0.3)
    axes[0].plot([mn2,mx2],[mn2,mx2], color=C_RED, lw=2, ls="--", label="Prediksi Sempurna")
    axes[0].text(0.05, 0.90, f"R² = {results_sorted[0]['r2']:.4f}", transform=axes[0].transAxes, fontsize=12, color=C_RED, fontweight="bold")
    axes[0].set_xlabel("Aktual (ton)"); axes[0].set_ylabel("Prediksi (ton)")
    axes[0].set_title("Aktual vs Prediksi", fontweight="bold"); axes[0].legend()
    resid = yte.values - best_pred
    axes[1].scatter(best_pred, resid, alpha=0.5, color=C_GOLD, s=22, zorder=3, edgecolors="white", linewidths=0.3)
    axes[1].axhline(0, color=C_RED, lw=2, ls="--")
    axes[1].set_xlabel("Prediksi (ton)"); axes[1].set_ylabel("Residual")
    axes[1].set_title("Plot Residual", fontweight="bold")
    axes[2].hist(resid, bins=28, color=C_TEAL, edgecolor="white", alpha=0.85)
    axes[2].axvline(0, color=C_RED, lw=2, ls="--")
    axes[2].set_xlabel("Nilai Residual"); axes[2].set_ylabel("Frekuensi")
    axes[2].set_title("Distribusi Residual", fontweight="bold")
    fig.tight_layout(pad=1.5)
    c_model_eval = fig_b64(fig, dpi=140)

    # 9 — Feature importance
    c_fi = ""
    if fi_series is not None:
        fi_sorted = fi_series.sort_values(ascending=True)
        fig, ax = plt.subplots(figsize=(12, 6))
        colors_fi = [C_GREEN if v >= float(fi_sorted.median()) else C_TEAL for v in fi_sorted.values]
        bars_fi = ax.barh(fi_sorted.index, fi_sorted.values, color=colors_fi, edgecolor="white", height=0.6)
        ax.set_title(f"Peringkat Faktor Penting — {best_name}", fontsize=13, fontweight="bold", color=C_DARK)
        ax.set_xlabel("Skor Kepentingan (ternormalisasi)")
        for bar in bars_fi:
            v = bar.get_width()
            ax.text(v+fi_sorted.max()*0.01, bar.get_y()+bar.get_height()/2, f"{v:.4f}", va="center", fontsize=9.5, fontweight="600", color=C_DARK)
        ax.set_xlim(0, fi_sorted.max()*1.18)
        fig.tight_layout(pad=1.5)
        c_fi = fig_b64(fig, dpi=140)

    # 10 — Forecast chart
    fig, ax = plt.subplots(figsize=(14, 6))
    x_pos = range(len(forecast_df))
    bars_fc = ax.bar(x_pos, forecast_df["forecast_tons"], color=PALETTE[:len(forecast_df)],
                     edgecolor="white", width=0.55, zorder=3, label="Prediksi")
    ax.errorbar(x_pos, forecast_df["forecast_tons"],
                yerr=[forecast_df["forecast_tons"]-forecast_df["lower_bound"],
                      forecast_df["upper_bound"]-forecast_df["forecast_tons"]],
                fmt="none", color=C_DARK, capsize=8, capthick=2, elinewidth=2, zorder=5)
    ax.plot(x_pos, forecast_df["last_actual"], "D--", color=C_GOLD, lw=2, markersize=7, zorder=6, label="Aktual Bulan Lalu")
    ax.set_xticks(list(x_pos)); ax.set_xticklabels(forecast_df["estate"], rotation=20, ha="right")
    ax.set_title(f"Forecast Produksi — {next_month.strftime('%B %Y')} (dengan interval kepercayaan MAE)",
                 fontsize=13, fontweight="bold", color=C_DARK)
    ax.set_ylabel("Produksi (ton)"); ax.legend(fontsize=9)
    for bar, row in zip(bars_fc, forecast_df.itertuples()):
        chg = row.change_pct; color = C_LIME if chg >= 0 else C_RED
        ax.text(bar.get_x()+bar.get_width()/2,
                bar.get_height()+forecast_df["forecast_tons"].max()*0.02,
                f"{chg:+.1f}%", ha="center", va="bottom", fontsize=9, fontweight="700", color=color)
    fig.tight_layout(pad=1.5)
    c_forecast = fig_b64(fig, dpi=140)

    # ── AI Insights ──
    estate_str = (df.groupby("estate")
                    .agg(total=("production_tons","sum"), avg_prod_ha=("productivity_ton_per_ha","mean"), records=("production_tons","count"))
                    .round(3).to_string())
    month_avg  = df.groupby("month_name")["production_tons"].mean().round(1).to_string()
    top3       = list(fi_out.keys())[:3] if fi_out else FEATURES[:3]

    ai_trend = ask_llm(
        f"Data tren produksi Lonsum:\n- Total: {total_prod:,.1f} ton | Periode: {date_range}\n"
        f"- Rata-rata produktivitas: {avg_prod_ha:.4f} t/ha\n- Estate: {', '.join(estates)}\n\n"
        f"Analisis tren utama dan pergerakan produksi sepanjang waktu. Berikan 1 rekomendasi konkret."
    )
    ai_seasonal = ask_llm(
        f"Pola musiman produksi Lonsum:\n{month_avg}\nBulan puncak: {peak_month}. Total estate: {len(estates)}.\n\n"
        f"Jelaskan pola musiman yang terlihat. Apa implikasinya untuk perencanaan panen? Berikan 1 rekomendasi."
    )
    ai_annual = ask_llm(
        f"Produksi tahunan per estate:\n{estate_str}\nEstate terbaik: {best_estate}. Periode: {date_range}.\n\n"
        f"Bandingkan performa antar estate. Siapa yang konsisten tumbuh? Berikan 1 rekomendasi."
    )
    ai_boxplot = ask_llm(
        f"Distribusi produksi bulanan per estate:\n{estate_str}\n\n"
        f"Analisis sebaran dan konsistensi produksi antar estate. Estate mana yang paling stabil? Berikan 1 rekomendasi."
    )
    ai_prodha = ask_llm(
        f"Produktivitas per hektar:\n{df.groupby('estate')['productivity_ton_per_ha'].mean().round(4).to_string()}\n"
        f"Rata-rata fleet: {avg_prod_ha:.4f} t/ha.\n\n"
        f"Identifikasi estate di atas dan di bawah rata-rata. Berikan 1 rekomendasi."
    )
    ai_corr = ask_llm(
        f"Korelasi faktor dengan produksi:\n{df[['plantation_area_ha','rainfall_mm','workers','fertilizer_kg','productivity_ton_per_ha','production_tons']].corr()['production_tons'].drop('production_tons').round(3).to_string()}\n\n"
        f"Jelaskan hubungan antar faktor. Mana yang paling berpengaruh? Berikan 1 rekomendasi."
    )
    ai_scatter = ask_llm(
        f"Hubungan scatter antara input dan output produksi Lonsum.\n"
        f"Faktor: curah hujan, pupuk, tenaga kerja, luas lahan.\n"
        f"Periode: {date_range}. Total produksi: {total_prod:,.1f} ton.\n\n"
        f"Driver mana yang paling actionable? Berikan 1 rekomendasi konkret."
    )
    ai_model = ask_llm(
        f"Performa model ML terbaik ({best_name}):\n"
        f"R²={results_sorted[0]['r2']:.4f} | MAE={results_sorted[0]['mae']:.3f} ton | "
        f"RMSE={results_sorted[0]['rmse']:.3f} ton | CV R²={results_sorted[0]['cv_r2']:.4f}\n\n"
        f"Jelaskan makna angka ini untuk orang awam. Seberapa bisa dipercaya? Berikan 1 rekomendasi penggunaan."
    )
    ai_fi = ask_llm(
        f"Faktor terpenting menurut model {best_name}:\n"
        + "\n".join([f"  {k}: {v:.4f}" for k, v in list(fi_out.items())[:5]]) + "\n\n"
        f"Jelaskan mengapa faktor-faktor ini penting. Berikan 1 rekomendasi prioritas."
    )
    ai_forecast = ask_llm(
        f"Forecast produksi bulan depan ({next_month.strftime('%B %Y')}):\n{forecast_df[['estate','forecast_tons','change_pct']].to_string()}\n"
        f"Model: {best_name} | MAE: {results_sorted[0]['mae']:.3f} ton\n\n"
        f"Analisis outlook produksi bulan depan. Berikan 1 rekomendasi tindakan segera."
    )

    result = {
        "kpis": kpis,
        "model_results": results_sorted,
        "best_model": best_name,
        "feature_importance": fi_out,
        "forecast_data": forecast_rows,
        "charts": {
            "trend": c_trend, "seasonal": c_seasonal, "annual": c_annual,
            "boxplot": c_boxplot, "prodha": c_prodha, "corr": c_corr,
            "scatter": c_scatter, "model_eval": c_model_eval,
            "feature_imp": c_fi, "forecast": c_forecast,
        },
        "ai_insights": {
            "trend": ai_trend, "seasonal": ai_seasonal, "annual": ai_annual,
            "boxplot": ai_boxplot, "prodha": ai_prodha, "correlation": ai_corr,
            "scatter": ai_scatter, "model": ai_model,
            "feature_importance": ai_fi, "forecast": ai_forecast,
        },
        "generated_at": generated_at,
    }

    # Simpan ke global state (termasuk DataFrame untuk download)
    _last_result = {
        **result,
        "_df": df,
        "_forecast_df": forecast_df,
        "_alerts_df": alerts_df,
    }
    return result


# ==============================================================================
# ROUTES
# ==============================================================================
@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(HTML_PAGE)


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
    if missing:
        raise HTTPException(422, f"Missing columns: {', '.join(sorted(missing))}")
    try:
        result = process_dataset(df_raw)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"Processing error: {e}")
    json_bytes = json.dumps(result, ensure_ascii=False).encode("utf-8")
    return StreamingResponse(
        iter([json_bytes]), media_type="application/json",
        headers={"Content-Length": str(len(json_bytes))},
    )


# ── Download routes — semua pakai error handling yang konsisten ──

@app.get("/api/download/excel")
async def download_excel():
    if "_df" not in _last_result:
        raise HTTPException(404, "Belum ada data — upload CSV terlebih dahulu.")
    try:
        xlsx = build_excel(
            _last_result["_df"], _last_result["kpis"],
            _last_result["model_results"],
            _last_result["_forecast_df"], _last_result["_alerts_df"]
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"Gagal membuat Excel: {e}")
    fname = f"Lonsum_ProduksiBulanan_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return Response(
        content=xlsx,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'}
    )


@app.get("/api/download/stats")
async def download_stats():
    if "_df" not in _last_result:
        raise HTTPException(404, "Belum ada data — upload CSV terlebih dahulu.")
    try:
        df   = _last_result["_df"]
        kpis = _last_result["kpis"]
        generated_at = kpis.get("generated_at", datetime.now().strftime("%d %B %Y, %H:%M"))
        date_range   = kpis.get("date_range", "—")

        stats = df.groupby("estate").agg(
            total_production_tons=("production_tons","sum"),
            avg_monthly_tons=("production_tons","mean"),
            max_monthly_tons=("production_tons","max"),
            min_monthly_tons=("production_tons","min"),
            std_dev=("production_tons","std"),
            avg_productivity_t_ha=("productivity_ton_per_ha","mean"),
            avg_rainfall_mm=("rainfall_mm","mean"),
            avg_workers=("workers","mean"),
            avg_fertilizer_kg=("fertilizer_kg","mean"),
            records=("production_tons","count"),
        ).round(3).reset_index()

        wb = Workbook(); ws = wb.active; ws.title = "Statistik Estate"
        ws.sheet_properties.tabColor = "0e7c6e"
        _title_row(ws, "STATISTIK ESTATE — PT LONDON SUMATRA INDONESIA", 10, fill_hex="0e7c6e")
        _subtitle_row(ws, f"Dibuat: {generated_at} | Periode: {date_range}", 10)

        headers = ["Estate","Total Produksi (ton)","Rata-rata Bulanan (ton)","Maks Bulanan (ton)","Min Bulanan (ton)",
                   "Std Deviasi","Produktivitas (t/ha)","Curah Hujan Rata-rata (mm)","Tenaga Kerja Rata-rata","Jumlah Record"]
        for i, h in enumerate(headers, 1):
            ws.cell(3, i, h)
        _apply_header(ws, 3, 10, "0e7c6e")

        for ri, row in stats.iterrows():
            r = ri + 4
            vals = [row["estate"],row["total_production_tons"],row["avg_monthly_tons"],row["max_monthly_tons"],
                    row["min_monthly_tons"],row["std_dev"],row["avg_productivity_t_ha"],
                    row["avg_rainfall_mm"],round(float(row["avg_workers"]),0),int(row["records"])]
            for ci, v in enumerate(vals, 1):
                ws.cell(r, ci, v)
            _apply_data_row(ws, r, 10, alt=(ri % 2 == 0))

        _set_widths(ws, [18,22,22,20,20,14,22,24,22,14])
        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"Gagal membuat Excel statistik: {e}")

    fname = f"Lonsum_StatistikEstate_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return Response(
        content=buf.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'}
    )


@app.get("/api/download/alerts")
async def download_alerts():
    if "_alerts_df" not in _last_result:
        raise HTTPException(404, "Belum ada data — upload CSV terlebih dahulu.")
    try:
        df        = _last_result["_df"]
        alerts_df = _last_result["_alerts_df"].copy()
        kpis      = _last_result["kpis"]
        generated_at = kpis.get("generated_at", datetime.now().strftime("%d %B %Y, %H:%M"))
        avg_prod  = float(df["productivity_ton_per_ha"].mean())
        thr       = avg_prod * 0.75

        alerts_df["fleet_avg_t_ha"] = round(avg_prod, 4)
        alerts_df["deficit_pct"]    = ((avg_prod - alerts_df["productivity_ton_per_ha"]) / avg_prod * 100).round(1)

        wb = Workbook(); ws = wb.active; ws.title = "Alert Produktivitas Rendah"
        ws.sheet_properties.tabColor = "d64045"
        _title_row(ws, "ALERT PRODUKTIVITAS RENDAH — PT LONDON SUMATRA INDONESIA", 7, fill_hex="d64045")
        _subtitle_row(ws, f"Threshold: < {thr:.3f} t/ha (75% rata-rata fleet) | Dibuat: {generated_at}", 7)

        headers = ["Tanggal","Estate","Produksi (ton)","Luas Lahan (ha)","Produktivitas (t/ha)","Rata-rata Fleet (t/ha)","Defisit vs Rata-rata (%)"]
        for i, h in enumerate(headers, 1):
            ws.cell(4, i, h)
        _apply_header(ws, 4, 7, "d64045")

        if len(alerts_df) > 0:
            out_cols = ["date","estate","production_tons","plantation_area_ha","productivity_ton_per_ha","fleet_avg_t_ha","deficit_pct"]
            for ri, (_, row) in enumerate(alerts_df[out_cols].iterrows()):
                r = ri + 5
                pv      = float(row["productivity_ton_per_ha"])
                deficit = float(row["deficit_pct"])
                try:
                    date_str = row["date"].strftime("%b %Y")
                except Exception:
                    date_str = str(row["date"])
                vals = [date_str, str(row["estate"]), round(float(row["production_tons"]),2),
                        round(float(row["plantation_area_ha"]),2), round(pv,4),
                        round(avg_prod,4), round(deficit,1)]
                for ci, v in enumerate(vals, 1):
                    ws.cell(r, ci, v)
                _apply_data_row(ws, r, 7, alt=(ri % 2 == 0))
                if deficit > 40:
                    for c in range(1, 8):
                        ws.cell(r, c).fill = _hfill("FEE2E2")
        else:
            ws.merge_cells("A5:G5")
            ws.cell(5, 1, "Tidak ada estate dengan produktivitas di bawah threshold.")
            ws.cell(5, 1).alignment = _CENTER
            ws.cell(5, 1).font = Font(italic=True, name="Calibri", size=10, color="64748b")

        _set_widths(ws, [14,18,16,16,18,20,22])
        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"Gagal membuat Excel alert: {e}")

    fname = f"Lonsum_AlertProduktivitas_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return Response(
        content=buf.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'}
    )


@app.get("/api/download/forecast")
async def download_forecast():
    if "_forecast_df" not in _last_result:
        raise HTTPException(404, "Belum ada data — upload CSV terlebih dahulu.")
    try:
        fc   = _last_result["_forecast_df"].copy()
        kpis = _last_result["kpis"]
        best = _last_result.get("best_model", "—")
        generated_at = kpis.get("generated_at", datetime.now().strftime("%d %B %Y, %H:%M"))
        date_range   = kpis.get("date_range", "—")

        wb = Workbook(); ws = wb.active; ws.title = "Forecast Bulan Depan"
        ws.sheet_properties.tabColor = "c9a84c"
        _title_row(ws, "FORECAST PRODUKSI BULAN DEPAN — PT LONDON SUMATRA INDONESIA", 8, fill_hex="c9a84c")
        _subtitle_row(ws, f"Model: {best} | Dibuat: {generated_at} | Periode: {date_range}", 8)

        headers = ["Estate","Prediksi (ton)","Batas Bawah (ton)","Batas Atas (ton)",
                   "Aktual Bulan Lalu (ton)","Selisih (ton)","Perubahan (%)","Status"]
        for i, h in enumerate(headers, 1):
            ws.cell(4, i, h)
        _apply_header(ws, 4, 8, "c9a84c")

        for ri, row in enumerate(fc.itertuples()):
            r    = ri + 5
            chg  = float(row.change_pct)
            delta = round(float(row.forecast_tons) - float(row.last_actual), 2)
            status = "NAIK" if chg >= 0 else "TURUN"
            vals = [str(row.estate), round(float(row.forecast_tons),2),
                    round(float(row.lower_bound),2), round(float(row.upper_bound),2),
                    round(float(row.last_actual),2),
                    f"+{delta}" if delta >= 0 else str(delta),
                    f"+{chg}%" if chg >= 0 else f"{chg}%", status]
            for ci, v in enumerate(vals, 1):
                ws.cell(r, ci, v)
            _apply_data_row(ws, r, 8, alt=(ri % 2 == 0))
            txt_c = "065f46" if chg >= 0 else "991b1b"
            bg_c  = "D1FAE5" if chg >= 0 else "FEE2E2"
            for c in [6, 7, 8]:
                ws.cell(r, c).fill = _hfill(bg_c)
                ws.cell(r, c).font = Font(bold=True, name="Calibri", color=txt_c)

        _set_widths(ws, [20,18,18,18,22,16,16,12])
        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"Gagal membuat Excel forecast: {e}")

    fname = f"Lonsum_Forecast_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return Response(
        content=buf.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'}
    )


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "has_data": "_df" in _last_result,
        "version": "3.1.0",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)