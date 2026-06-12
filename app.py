import streamlit as st
import pandas as pd
import re
import requests
import time
from urllib.parse import urlparse
from io import BytesIO

st.set_page_config(page_title="Multi-Platform Post Checker", layout="wide")
st.title("🔥 Multi-Platform Post Checker [FREE]")
st.markdown("**Hỗ trợ X, YouTube, Facebook...** • Tự detect Platform + Engagement = Likes + RT/Shares + Quotes + Bookmarks")

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
    else:
        return "Other"

def extract_id(url, platform):
    if platform == "X/Twitter":
        patterns = [r'/status/(\d+)', r'twitter\.com/[^/]+/status/(\d+)', r'x\.com/[^/]+/status/(\d+)']
        for p in patterns:
            m = re.search(p, url)
            if m: return m.group(1)
    elif platform == "YouTube":
        if 'youtu.be' in url:
            m = re.search(r'youtu\.be/([^?&#]+)', url)
            return m.group(1) if m else None
        else:
            m = re.search(r'v=([^&]+)', url)
            return m.group(1) if m else None
    return None

def fetch_x_metrics(tid):
    try:
        resp = requests.get(f"https://api.fxtwitter.com/status/{tid}", timeout=15)
        if resp.status_code == 200:
            data = resp.json().get("tweet", {})
            likes = data.get("likes", 0)
            retweets = data.get("retweets", 0)
            quotes = data.get("quotes", 0)
            bookmarks = data.get("bookmarks", 0)
            engagement = likes + retweets + quotes + bookmarks
            
            return {
                "impressions": data.get("views", 0),
                "likes": likes,
                "retweets": retweets,
                "quotes": quotes,
                "bookmarks": bookmarks,
                "replies": data.get("replies", 0),
                "engagement": engagement,
                "content": data.get("text", "")[:600]
            }
    except:
        pass
    return {"impressions":0, "likes":0, "retweets":0, "quotes":0, "bookmarks":0, "replies":0, "engagement":0, "content":""}

def fetch_youtube_metrics(video_id):
    try:
        import yt_dlp
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            likes = info.get("like_count", 0)
            comments = info.get("comment_count", 0)
            # YT không có retweet/quotes/bookmarks rõ ràng
            engagement = likes + comments  # tạm coi comments như engagement chính
            return {
                "impressions": info.get("view_count", 0),
                "likes": likes,
                "retweets": 0,
                "quotes": 0,
                "bookmarks": 0,
                "replies": comments,
                "engagement": engagement,
                "content": info.get("title", "")[:600]
            }
    except:
        pass
    return {"impressions":0, "likes":0, "retweets":0, "quotes":0, "bookmarks":0, "replies":0, "engagement":0, "content":""}

# ====================== UPLOAD ======================
uploaded_file = st.file_uploader("Upload file chứa link (CSV / Excel / TXT)", 
                                type=["csv", "xlsx", "xls", "txt"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        lines = [line.strip() for line in uploaded_file.getvalue().decode("utf-8").splitlines() if line.strip()]
        df = pd.DataFrame({"Link": lines})

    st.success(f"✅ Đã load {len(df)} links")

    link_col = st.selectbox("Chọn cột chứa link", df.columns, index=0)

    if st.button("🚀 Fetch Data & Tính Engagement", type="primary"):
        with st.spinner("Đang scrape metrics..."):
            results = []
            progress_bar = st.progress(0)

            for idx, link in enumerate(df[link_col].astype(str)):
                platform = get_platform(link)
                row = {
                    "Original_Link": link,
                    "Platform": platform,
                    "Impressions": 0,
                    "Likes": 0,
                    "Retweets_Shares": 0,
                    "Quotes": 0,
                    "Bookmarks_Saves": 0,
                    "Replies_Comments": 0,
                    "Engagement": 0,
                    "Content": ""
                }

                if platform == "X/Twitter":
                    tid = extract_id(link, platform)
                    if tid:
                        data = fetch_x_metrics(tid)
                        row.update(data)
                elif platform == "YouTube":
                    vid = extract_id(link, platform)
                    if vid:
                        data = fetch_youtube_metrics(vid)
                        row.update(data)
                else:
                    # Fallback cho các platform khác
                    try:
                        resp = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
                        title = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE | re.DOTALL)
                        row["Content"] = title.group(1).strip()[:500] if title else "Không lấy được nội dung"
                    except:
                        row["Content"] = "Không scrape được"

                results.append(row)
                progress_bar.progress(min(100, int((idx + 1) / len(df) * 100)))
                time.sleep(1.1 if platform in ["X/Twitter", "YouTube"] else 2.0)

            result_df = pd.DataFrame(results)
            
            # Sắp xếp cột cho đẹp
            cols_order = ["Original_Link", "Platform", "Impressions", "Engagement", 
                         "Likes", "Retweets_Shares", "Quotes", "Bookmarks_Saves", 
                         "Replies_Comments", "Content"]
            result_df = result_df[[c for c in cols_order if c in result_df.columns]]

            st.subheader("📊 Kết quả")
            st.dataframe(result_df, use_container_width=True)

            # Download
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Tải CSV", csv, f"post_metrics_{time.strftime('%Y%m%d_%H%M')}.csv", "text/csv")

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                result_df.to_excel(writer, index=False)
            st.download_button("📥 Tải Excel (.xlsx)", output.getvalue(), 
                             f"post_metrics_{time.strftime('%Y%m%d_%H%M')}.xlsx")

st.caption("Made for Minh Anh • Mantle Squad • Free version")
