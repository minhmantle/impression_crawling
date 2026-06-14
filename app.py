import streamlit as st
import pandas as pd
import re
import requests
import time
import random
from urllib.parse import urlparse
from io import BytesIO

# Mantle Brand Colors
MANTLE_GREEN = "#00D4A5"
MANTLE_DARK = "#0A1F1C"
MANTLE_LIGHT = "#F8FFFD"

st.set_page_config(page_title="Post Checker", layout="wide", page_icon="🔥")

# Custom CSS for Mantle branding + light theme
st.markdown(f"""
<style>
    .stApp {{ background-color: {MANTLE_LIGHT}; }}
    .stButton>button {{ background-color: {MANTLE_GREEN}; color: white; border-radius: 8px; }}
    h1, h2, h3 {{ color: {MANTLE_DARK}; }}
    .stDataFrame {{ background-color: white; }}
</style>
""", unsafe_allow_html=True)

st.title("🔥 Post Checker")
st.markdown("**Mantle internal developed** • Multi-platform metrics tool")

funny_messages = [
    "Since this is a free tool, it might take a little longer... like waiting for altseason 😅",
    "Brewing the metrics... Free version so we use magic instead of paid API ✨",
    "Scraping the internet like a true degen... Hang tight!",
    "Free tool = occasional slow loading. Blame X, not us 😂",
    "Fetching impressions... If it fails, blame Elon, not Minh Anh",
    "Running on pure Mantle community spirit (and coffee)",
    "Please wait while the free hamster runs on the wheel...",
    "This tool is sponsored by: Minh Anh's patience ❤️",
    "Loading... Rate limited by being free. Worth it though!",
    "Almost there! Free tools need love too 💚"
]

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
        if m: return m.group(1)
    return None

def fetch_x_metrics(tid):
    try:
        url = f"https://api.fxtwitter.com/status/{tid}"
        headers = {"User-Agent": "Mantle-Post-Checker/1.0"}
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            tweet = data.get("tweet") or {}
            likes = tweet.get("likes", 0)
            retweets = tweet.get("retweets", 0)
            quotes = tweet.get("quotes", 0)
            bookmarks = tweet.get("bookmarks", 0)
            views = tweet.get("views", 0)
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
            return {"impressions":0, "likes":0, "retweets":0, "quotes":0, "bookmarks":0, "replies":0, "engagement":0, "content":"", "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"impressions":0, "likes":0, "retweets":0, "quotes":0, "bookmarks":0, "replies":0, "engagement":0, "content":"", "error": str(e)[:80]}

# Upload section
uploaded_file = st.file_uploader("Upload file containing post links (CSV / Excel / TXT)", 
                                type=["csv", "xlsx", "xls", "txt"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        lines = [line.strip() for line in uploaded_file.getvalue().decode("utf-8").splitlines() if line.strip()]
        df = pd.DataFrame({"Link": lines})

    st.success(f"✅ Loaded {len(df)} links successfully")

    link_col = st.selectbox("Select column containing links", df.columns, index=0)

    if st.button("🚀 Fetch Metrics & Calculate Engagement", type="primary"):
        random_msg = random.choice(funny_messages)
        with st.spinner(random_msg):
            results = []
            progress_bar = st.progress(0)

            for idx, link in enumerate(df[link_col].astype(str)):
                platform = get_platform(link)
                row = {
                    "Original_Link": link,
                    "Platform": platform,
                    "Impressions": 0,
                    "Engagement": 0,
                    "Likes": 0,
                    "Retweets_Shares": 0,
                    "Quotes": 0,
                    "Bookmarks_Saves": 0,
                    "Replies_Comments": 0,
                    "Content": "",
                    "Error": ""
                }

                if platform == "X/Twitter":
                    tid = extract_tweet_id(link)
                    if tid:
                        data = fetch
