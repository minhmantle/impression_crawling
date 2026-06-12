import streamlit as st
import pandas as pd
import re
import requests
import time
from urllib.parse import urlparse
from io import BytesIO

st.set_page_config(page_title="Multi-Platform Post Checker", layout="wide")
st.title("🔥 Multi-Platform Post Checker [FREE]")
st.markdown("**Debug mode bật** • Xem lỗi chi tiết nếu có")

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
        headers = {"User-Agent": "Mantle-Squad-Tool/1.0"}
        resp = requests.get(url, headers=headers, timeout=12)
        
        st.caption(f"Debug: {tid} → Status {resp.status_code}")  # debug tạm thời
        
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
            return {"impressions":0, "likes":0, "retweets":0, "quotes":0, "bookmarks":0, 
                    "replies":0, "engagement":0, "content":"", "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"impressions":0, ..., "error": str(e)[:100]}

# ====================== MAIN ======================
uploaded_file = st.file_uploader("Upload file link...", type=["csv", "xlsx", "xls", "txt"])

if uploaded_file:
    # Đọc file (giữ nguyên logic cũ)
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        lines = [line.strip() for line in uploaded_file.getvalue().decode("utf-8").splitlines() if line.strip()]
        df = pd.DataFrame({"Link": lines})

    st.success(f"✅ Load {len(df)} links")

    link_col = st.selectbox("Chọn cột link", df.columns)

    if st.button("🚀 Fetch + Tính Engagement", type="primary"):
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
                    data = fetch_x_metrics(tid)
                    row.update({
                        "Impressions": data["impressions"],
                        "Likes": data["likes"],
                        "Retweets_Shares": data["retweets"],
                        "Quotes": data["quotes"],
                        "Bookmarks_Saves": data["bookmarks"],
                        "Replies_Comments": data["replies"],
                        "Engagement": data["engagement"],
                        "Content": data["content"],
                        "Error": data.get("error", "")
                    })
            # ... (các platform khác giữ nguyên hoặc bỏ tạm)

            results.append(row)
            progress_bar.progress(min(100, int((idx+1)/len(df)*100)))
            time.sleep(1.2)

        result_df = pd.DataFrame(results)
        st.subheader("📊 Kết quả")
        st.dataframe(result_df, use_container_width=True)

        # Download...
        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Tải CSV", csv, f"metrics_{time.strftime('%Y%m%d_%H%M')}.csv")

st.info("Nếu vẫn 0 hết → paste 1-2 link X mày
