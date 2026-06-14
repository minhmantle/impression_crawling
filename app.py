import streamlit as st
import pandas as pd
import re
import requests
import time
import random
from urllib.parse import urlparse
from io import BytesIO

# ====================== PAGE CONFIG ======================
MANTLE_LOGO_B64 = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+CiAgPHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIHJ4PSIyMiIgZmlsbD0iIzBBMjgxOCIvPgogIDxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDUwLDUwKSI+CiAgICA8cG9seWdvbiBwb2ludHM9IjAuMDAsLTEyLjAwIDMuNDEsLTExLjUxIDguMDksLTI3LjMzIDAuMDAsLTI4LjUwIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjY4Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9IjMuNzEsLTExLjQxIDYuODAsLTkuODkgMTcuMTEsLTI0Ljg5IDkuMzMsLTI4LjcyIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjc4Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9IjcuMDUsLTkuNzEgOS41MiwtNy4zMSAyNC45MSwtMTkuMTEgMTguNDUsLTI1LjQwIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjg3Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9IjkuNzEsLTcuMDUgMTEuMzEsLTQuMDEgMzAuMTMsLTEwLjY3IDI1Ljg2LC0xOC43OSIgZmlsbD0iIzNERDY4QyIgb3BhY2l0eT0iMC45NCIvPgogICAgPHBvbHlnb24gcG9pbnRzPSIxMS40MSwtMy43MSAxMi4wMCwtMC4zMSAzMS44NCwtMC44MyAzMC4yOSwtOS44NCIgZmlsbD0iIzNERDY4QyIgb3BhY2l0eT0iMC45OCIvPgogICAgPHBvbHlnb24gcG9pbnRzPSIxMi4wMCwwLjAwIDExLjUxLDMuNDEgMjkuNzgsOC44MiAzMS4wNiwwLjAwIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIxLjAwIi8+CiAgICA8cG9seWdvbiBwb2ludHM9IjExLjQxLDMuNzEgOS44OSw2LjgwIDI0LjQ2LDE2LjgxIDI4LjIzLDkuMTciIGZpbGw9IiMzREQ2OEMiIG9wYWNpdHk9IjAuOTgiLz4KICAgIDxwb2x5Z29uIHBvaW50cz0iOS43MSw3LjA1IDcuMzEsOS41MiAxNi45NSwyMi4wOSAyMi41MywxNi4zNyIgZmlsbD0iIzNERDY4QyIgb3BhY2l0eT0iMC45NCIvPgogICAgPHBvbHlnb24gcG9pbnRzPSI3LjA1LDkuNzEgNC4wMSwxMS4zMSA4LjU5LDI0LjI2IDE1LjEyLDIwLjgyIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjg3Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9IjMuNzEsMTEuNDEgMC4zMSwxMi4wMCAwLjYyLDIzLjU0IDcuMjgsMjIuMzkiIGZpbGw9IiMzREQ2OEMiIG9wYWNpdHk9IjAuNzgiLz4KICAgIDxwb2x5Z29uIHBvaW50cz0iMC4wMCwxMi4wMCAtMy40MSwxMS41MSAtNi4xMSwyMC42MSAwLjAwLDIxLjUwIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjY4Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii0zLjcxLDExLjQxIC02LjgwLDkuODkgLTExLjIxLDE2LjMyIC02LjEyLDE4LjgzIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjU3Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii03LjA1LDkuNzEgLTkuNTIsNy4zMSAtMTQuNzYsMTEuMzMgLTEwLjk0LDE1LjA1IiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjQ4Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii05LjcxLDcuMDUgLTExLjMxLDQuMDEgLTE3LjAwLDYuMDIgLTE0LjU5LDEwLjYwIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjQxIi8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii0xMS40MSwzLjcxIC0xMi4wMCwwLjMxIC0xOC4xNSwwLjQ4IC0xNy4yNiw1LjYxIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjM3Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii0xMi4wMCwwLjAwIC0xMS41MSwtMy40MSAtMTguMTYsLTUuMzggLTE4Ljk0LDAuMDAiIGZpbGw9IiMzREQ2OEMiIG9wYWNpdHk9IjAuMzUiLz4KICAgIDxwb2x5Z29uIHBvaW50cz0iLTExLjQxLC0zLjcxIC05Ljg5LC02LjgwIC0xNi43NCwtMTEuNTEgLTE5LjMyLC02LjI4IiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjM3Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii05LjcxLC03LjA1IC03LjMxLC05LjUyIC0xMy40OSwtMTcuNTggLTE3LjkyLC0xMy4wMiIgZmlsbD0iIzNERDY4QyIgb3BhY2l0eT0iMC40MSIvPgogICAgPHBvbHlnb24gcG9pbnRzPSItNy4wNSwtOS43MSAtNC4wMSwtMTEuMzEgLTguMTAsLTIyLjg4IC0xNC4yNiwtMTkuNjMiIGZpbGw9IiMzREQ2OEMiIG9wYWNpdHk9IjAuNDgiLz4KICAgIDxwb2x5Z29uIHBvaW50cz0iLTMuNzEsLTExLjQxIC0wLjMxLC0xMi4wMCAtMC42OSwtMjYuNDUgLTguMTgsLTI1LjE2IiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjU3Ii8+CiAgPC9nPgo8L3N2Zz4="

st.set_page_config(
    page_title="Post Checker — Mantle",
    page_icon=MANTLE_LOGO_B64,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ====================== MANTLE BRAND CSS ======================
st.markdown("""
<style>
  /* ── Google Fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

  /* ── Root palette (Mantle) ── */
  :root {
    --mantle-dark:    #0A2818;
    --mantle-mid:     #1A4D30;
    --mantle-mint:    #3DD68C;
    --mantle-mint-lt: #A8F0CB;
    --mantle-bg:      #F4FBF7;
    --mantle-surface: #FFFFFF;
    --mantle-border:  #D1EEE0;
    --mantle-text:    #0A2818;
    --mantle-muted:   #4A7A5E;
    --mantle-error:   #C0392B;
    --mantle-warn:    #E67E22;
  }

  /* ── Global reset ── */
  html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--mantle-bg) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--mantle-text) !important;
  }

  [data-testid="stHeader"] {
    background-color: var(--mantle-bg) !important;
    border-bottom: 1px solid var(--mantle-border);
  }

  /* ── Hero header ── */
  .mantle-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 32px 0 24px;
    border-bottom: 2px solid var(--mantle-border);
    margin-bottom: 32px;
  }
  .mantle-logo-ring {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--mantle-dark) 0%, var(--mantle-mid) 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .mantle-logo-ring svg { width: 32px; height: 32px; }
  .mantle-header-text h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: var(--mantle-dark) !important;
    margin: 0 0 2px !important;
    letter-spacing: -0.02em;
  }
  .mantle-header-text p {
    font-size: 0.82rem !important;
    color: var(--mantle-muted) !important;
    margin: 0 !important;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .mantle-badge {
    display: inline-block;
    background: var(--mantle-mint-lt);
    color: var(--mantle-dark);
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 20px;
    margin-left: 8px;
    vertical-align: middle;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* ── Cards / surfaces ── */
  .mantle-card {
    background: var(--mantle-surface);
    border: 1px solid var(--mantle-border);
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(10,40,24,0.06);
  }
  .mantle-card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--mantle-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 12px;
  }

  /* ── File uploader ── */
  [data-testid="stFileUploader"] {
    background: var(--mantle-surface) !important;
    border: 1.5px dashed var(--mantle-mint) !important;
    border-radius: 10px !important;
  }
  [data-testid="stFileUploader"]:hover {
    border-color: var(--mantle-dark) !important;
    background: #EDFAF4 !important;
  }

  /* ── Selectbox ── */
  [data-testid="stSelectbox"] > div > div {
    background: var(--mantle-surface) !important;
    border: 1px solid var(--mantle-border) !important;
    border-radius: 8px !important;
    color: var(--mantle-text) !important;
  }

  /* ── Primary button ── */
  .stButton > button[kind="primary"],
  .stButton > button {
    background: var(--mantle-dark) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 10px 24px !important;
    letter-spacing: 0.01em;
    transition: background 0.18s ease, transform 0.1s ease;
  }
  .stButton > button:hover {
    background: var(--mantle-mid) !important;
    transform: translateY(-1px);
  }
  .stButton > button:active { transform: translateY(0); }

  /* ── Download buttons ── */
  .stDownloadButton > button {
    background: var(--mantle-surface) !important;
    color: var(--mantle-dark) !important;
    border: 1.5px solid var(--mantle-mint) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
  }
  .stDownloadButton > button:hover {
    background: var(--mantle-mint-lt) !important;
    border-color: var(--mantle-dark) !important;
  }

  /* ── Progress bar ── */
  [data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, var(--mantle-mint) 0%, var(--mantle-dark) 100%) !important;
    border-radius: 4px;
  }

  /* ── Success / info / warning banners ── */
  [data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left: 4px solid var(--mantle-mint) !important;
    background: #EDFAF4 !important;
    color: var(--mantle-text) !important;
  }

  /* ── Dataframe / table ── */
  [data-testid="stDataFrame"] {
    border-radius: 10px !important;
    border: 1px solid var(--mantle-border) !important;
  }

  /* ── Spinner text ── */
  [data-testid="stSpinner"] p {
    color: var(--mantle-muted) !important;
    font-weight: 500;
  }

  /* ── Section labels ── */
  .section-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--mantle-dark);
    margin: 24px 0 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--mantle-border);
    margin-left: 8px;
  }

  /* ── Loading toast ── */
  .loading-joke {
    background: var(--mantle-dark);
    color: var(--mantle-mint);
    border-radius: 10px;
    padding: 14px 20px;
    font-size: 0.88rem;
    font-weight: 500;
    margin: 12px 0;
    font-style: italic;
    letter-spacing: 0.01em;
  }

  /* ── Stat pills ── */
  .stat-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
  .stat-pill {
    background: var(--mantle-bg);
    border: 1px solid var(--mantle-border);
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 0.82rem;
    color: var(--mantle-muted);
    font-weight: 500;
  }
  .stat-pill strong {
    display: block;
    font-size: 1.15rem;
    color: var(--mantle-dark);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: var(--mantle-dark) !important;
    color: white !important;
  }

  /* Hide Streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ====================== FUNNY LOADING MESSAGES ======================
FUNNY_MESSAGES = [
    "💸 This tool is free, so please be patient — good things take time (and budget cuts).",
    "☕ Fetching data... Minh Anh is probably sipping coffee right now and can't speed this up.",
    "🐌 Fun fact: this API is powered by hopes, dreams, and zero dollars.",
    "🔍 Still working... If this takes forever, it's not a bug, it's a free-tier feature.",
    "🛠️ For any technical issues, please reach out to Minh Anh. She will fix it. Eventually.",
    "🌱 Growing your data organically. No paid boosts here.",
    "🤖 The robots are working hard. The unpaid kind.",
    "📡 Pinging the internet... it pinged back 'lol good luck'.",
    "⏳ Loading metrics. If you see this for more than 30s, the API is having a moment.",
    "🎯 Accuracy not guaranteed, vibes are. Reach out to Minh Anh for serious bugs.",
    "🚀 This would be instant if we had a budget. We don't. Enjoy the wait!",
    "🧘 Take a deep breath. The data will arrive when it's ready (or in ~30 seconds, whichever comes first).",
]

# ====================== HELPERS ======================
def get_platform(url):
    domain = urlparse(url.lower()).netloc
    if any(x in domain for x in ['x.com', 'twitter.com']):
        return "X/Twitter"
    elif 'youtube.com' in domain or 'youtu.be' in domain:
        return "YouTube"
    elif 'facebook.com' in domain:
        return "Facebook"
    elif 'tiktok.com' in domain:
        return "TikTok"
    elif 'instagram.com' in domain:
        return "Instagram"
    return "Other"

def extract_tweet_id(url):
    patterns = [r'/status/(\d+)', r'twitter\.com/[^/]+/status/(\d+)', r'x\.com/[^/]+/status/(\d+)']
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def fetch_x_metrics(tid):
    try:
        url = f"https://api.fxtwitter.com/status/{tid}"
        headers = {"User-Agent": "Mantle-Squad-Tool/1.0"}
        resp = requests.get(url, headers=headers, timeout=12)

        if resp.status_code == 200:
            data = resp.json()
            tweet = data.get("tweet") or {}
            likes     = tweet.get("likes", 0)
            retweets  = tweet.get("retweets", 0)
            quotes    = tweet.get("quotes", 0)
            bookmarks = tweet.get("bookmarks", 0)
            views     = tweet.get("views", 0)
            engagement = likes + retweets + quotes + bookmarks
            return {
                "impressions": views,
                "likes": likes,
                "retweets": retweets,
                "quotes": quotes,
                "bookmarks": bookmarks,
                "replies": tweet.get("replies", 0),
                "engagement": engagement,
                "content": tweet.get("text", "")[:600],
                "error": ""
            }
        else:
            return {"impressions":0,"likes":0,"retweets":0,"quotes":0,
                    "bookmarks":0,"replies":0,"engagement":0,"content":"",
                    "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"impressions":0,"likes":0,"retweets":0,"quotes":0,
                "bookmarks":0,"replies":0,"engagement":0,"content":"",
                "error": str(e)[:100]}

# ====================== HEADER ======================
st.markdown("""
<div class="mantle-header">
  <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+CiAgPHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIHJ4PSIyMiIgZmlsbD0iIzBBMjgxOCIvPgogIDxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDUwLDUwKSI+CiAgICA8cG9seWdvbiBwb2ludHM9IjAuMDAsLTEyLjAwIDMuNDEsLTExLjUxIDguMDksLTI3LjMzIDAuMDAsLTI4LjUwIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjY4Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9IjMuNzEsLTExLjQxIDYuODAsLTkuODkgMTcuMTEsLTI0Ljg5IDkuMzMsLTI4LjcyIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjc4Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9IjcuMDUsLTkuNzEgOS41MiwtNy4zMSAyNC45MSwtMTkuMTEgMTguNDUsLTI1LjQwIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjg3Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9IjkuNzEsLTcuMDUgMTEuMzEsLTQuMDEgMzAuMTMsLTEwLjY3IDI1Ljg2LC0xOC43OSIgZmlsbD0iIzNERDY4QyIgb3BhY2l0eT0iMC45NCIvPgogICAgPHBvbHlnb24gcG9pbnRzPSIxMS40MSwtMy43MSAxMi4wMCwtMC4zMSAzMS44NCwtMC44MyAzMC4yOSwtOS44NCIgZmlsbD0iIzNERDY4QyIgb3BhY2l0eT0iMC45OCIvPgogICAgPHBvbHlnb24gcG9pbnRzPSIxMi4wMCwwLjAwIDExLjUxLDMuNDEgMjkuNzgsOC44MiAzMS4wNiwwLjAwIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIxLjAwIi8+CiAgICA8cG9seWdvbiBwb2ludHM9IjExLjQxLDMuNzEgOS44OSw2LjgwIDI0LjQ2LDE2LjgxIDI4LjIzLDkuMTciIGZpbGw9IiMzREQ2OEMiIG9wYWNpdHk9IjAuOTgiLz4KICAgIDxwb2x5Z29uIHBvaW50cz0iOS43MSw3LjA1IDcuMzEsOS41MiAxNi45NSwyMi4wOSAyMi41MywxNi4zNyIgZmlsbD0iIzNERDY4QyIgb3BhY2l0eT0iMC45NCIvPgogICAgPHBvbHlnb24gcG9pbnRzPSI3LjA1LDkuNzEgNC4wMSwxMS4zMSA4LjU5LDI0LjI2IDE1LjEyLDIwLjgyIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjg3Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9IjMuNzEsMTEuNDEgMC4zMSwxMi4wMCAwLjYyLDIzLjU0IDcuMjgsMjIuMzkiIGZpbGw9IiMzREQ2OEMiIG9wYWNpdHk9IjAuNzgiLz4KICAgIDxwb2x5Z29uIHBvaW50cz0iMC4wMCwxMi4wMCAtMy40MSwxMS41MSAtNi4xMSwyMC42MSAwLjAwLDIxLjUwIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjY4Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii0zLjcxLDExLjQxIC02LjgwLDkuODkgLTExLjIxLDE2LjMyIC02LjEyLDE4LjgzIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjU3Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii03LjA1LDkuNzEgLTkuNTIsNy4zMSAtMTQuNzYsMTEuMzMgLTEwLjk0LDE1LjA1IiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjQ4Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii05LjcxLDcuMDUgLTExLjMxLDQuMDEgLTE3LjAwLDYuMDIgLTE0LjU5LDEwLjYwIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjQxIi8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii0xMS40MSwzLjcxIC0xMi4wMCwwLjMxIC0xOC4xNSwwLjQ4IC0xNy4yNiw1LjYxIiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjM3Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii0xMi4wMCwwLjAwIC0xMS41MSwtMy40MSAtMTguMTYsLTUuMzggLTE4Ljk0LDAuMDAiIGZpbGw9IiMzREQ2OEMiIG9wYWNpdHk9IjAuMzUiLz4KICAgIDxwb2x5Z29uIHBvaW50cz0iLTExLjQxLC0zLjcxIC05Ljg5LC02LjgwIC0xNi43NCwtMTEuNTEgLTE5LjMyLC02LjI4IiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjM3Ii8+CiAgICA8cG9seWdvbiBwb2ludHM9Ii05LjcxLC03LjA1IC03LjMxLC05LjUyIC0xMy40OSwtMTcuNTggLTE3LjkyLC0xMy4wMiIgZmlsbD0iIzNERDY4QyIgb3BhY2l0eT0iMC40MSIvPgogICAgPHBvbHlnb24gcG9pbnRzPSItNy4wNSwtOS43MSAtNC4wMSwtMTEuMzEgLTguMTAsLTIyLjg4IC0xNC4yNiwtMTkuNjMiIGZpbGw9IiMzREQ2OEMiIG9wYWNpdHk9IjAuNDgiLz4KICAgIDxwb2x5Z29uIHBvaW50cz0iLTMuNzEsLTExLjQxIC0wLjMxLC0xMi4wMCAtMC42OSwtMjYuNDUgLTguMTgsLTI1LjE2IiBmaWxsPSIjM0RENjhDIiBvcGFjaXR5PSIwLjU3Ii8+CiAgPC9nPgo8L3N2Zz4=" style="width:52px;height:52px;border-radius:12px;flex-shrink:0;"/>
  <div class="mantle-header-text">
    <h1>Post Checker <span class="mantle-badge">Mantle Internal</span></h1>
    <p>X / Twitter engagement metrics — developed by Mantle</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ====================== UPLOAD SECTION ======================
st.markdown('<div class="section-label">📂 Upload Your File</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drag & drop or browse — CSV, Excel, or plain TXT (one link per line)",
    type=["csv", "xlsx", "xls", "txt"],
    label_visibility="visible"
)

if uploaded_file:
    # Parse file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        lines = [l.strip() for l in uploaded_file.getvalue().decode("utf-8").splitlines() if l.strip()]
        df = pd.DataFrame({"Link": lines})

    col1, col2 = st.columns([2, 1])
    with col1:
        st.success(f"✅ Loaded **{len(df)} rows** from `{uploaded_file.name}`")
    with col2:
        link_col = st.selectbox("Column containing links", df.columns, index=0)

    st.markdown('<div class="section-label">⚙️ Run Analysis</div>', unsafe_allow_html=True)

    if st.button("🚀 Fetch Metrics & Calculate Engagement", type="primary"):

        # Show a random funny message
        joke = random.choice(FUNNY_MESSAGES)
        joke_placeholder = st.empty()
        joke_placeholder.markdown(f'<div class="loading-joke">{joke}</div>', unsafe_allow_html=True)

        with st.spinner("Fetching metrics — hang tight..."):
            results = []
            progress_bar = st.progress(0)
            status_text  = st.empty()

            for idx, link in enumerate(df[link_col].astype(str)):
                platform = get_platform(link)
                status_text.markdown(
                    f'<p style="color:#4A7A5E;font-size:0.82rem;font-weight:500;">'
                    f'Processing {idx+1} / {len(df)} &nbsp;·&nbsp; {link[:60]}{"…" if len(link)>60 else ""}</p>',
                    unsafe_allow_html=True
                )

                row = {
                    "Original_Link":     link,
                    "Platform":          platform,
                    "Impressions":       0,
                    "Engagement":        0,
                    "Likes":             0,
                    "Retweets_Shares":   0,
                    "Quotes":            0,
                    "Bookmarks_Saves":   0,
                    "Replies_Comments":  0,
                    "Content":           "",
                    "Error":             ""
                }

                if platform == "X/Twitter":
                    tid = extract_tweet_id(link)
                    if tid:
                        data = fetch_x_metrics(tid)
                        row.update({
                            "Impressions":      data["impressions"],
                            "Likes":            data["likes"],
                            "Retweets_Shares":  data["retweets"],
                            "Quotes":           data["quotes"],
                            "Bookmarks_Saves":  data["bookmarks"],
                            "Replies_Comments": data["replies"],
                            "Engagement":       data["engagement"],
                            "Content":          data["content"],
                            "Error":            data.get("error", "")
                        })

                results.append(row)
                progress_bar.progress(min(100, int((idx + 1) / len(df) * 100)))

                # Rotate funny message every 5 posts
                if (idx + 1) % 5 == 0:
                    joke_placeholder.markdown(
                        f'<div class="loading-joke">{random.choice(FUNNY_MESSAGES)}</div>',
                        unsafe_allow_html=True
                    )

                time.sleep(1.2)

            joke_placeholder.empty()
            status_text.empty()

        result_df = pd.DataFrame(results)
        cols = ["Original_Link","Platform","Impressions","Engagement",
                "Likes","Retweets_Shares","Quotes","Bookmarks_Saves",
                "Replies_Comments","Content","Error"]
        result_df = result_df[[c for c in cols if c in result_df.columns]]

        # ── Summary stats ──
        st.markdown('<div class="section-label">📊 Results</div>', unsafe_allow_html=True)

        x_rows = result_df[result_df["Platform"] == "X/Twitter"]
        total_impressions = x_rows["Impressions"].sum()
        total_engagement  = x_rows["Engagement"].sum()
        total_likes       = x_rows["Likes"].sum()
        success_count     = len(x_rows[x_rows["Error"] == ""])

        st.markdown(f"""
        <div class="stat-row">
          <div class="stat-pill"><strong>{len(result_df)}</strong>Total Posts</div>
          <div class="stat-pill"><strong>{success_count}</strong>Fetched OK</div>
          <div class="stat-pill"><strong>{total_impressions:,}</strong>Total Impressions</div>
          <div class="stat-pill"><strong>{total_engagement:,}</strong>Total Engagement</div>
          <div class="stat-pill"><strong>{total_likes:,}</strong>Total Likes</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Excel download (above table) ──
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            result_df.to_excel(writer, index=False)
        st.download_button(
            "⬇️ Download Excel",
            output.getvalue(),
            f"mantle_metrics_{time.strftime('%Y%m%d_%H%M')}.xlsx"
        )

        st.dataframe(result_df, use_container_width=True)


# ====================== FOOTER ======================
st.markdown("""
<div style="margin-top:48px; padding-top:20px; border-top:1px solid #D1EEE0;
            display:flex; justify-content:space-between; align-items:center;
            color:#4A7A5E; font-size:0.78rem; font-weight:500;">
  <span>Post Checker · Mantle Internal Tool</span>
  <span>Supports X / Twitter · More platforms coming soon</span>
  <span>Issues? Reach out to <strong style="color:#0A2818">Minh Anh</strong></span>
</div>
""", unsafe_allow_html=True)
