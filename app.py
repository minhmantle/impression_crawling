import streamlit as st
import pandas as pd
import re
import requests
import time
from io import BytesIO

st.set_page_config(page_title="X Impression Checker - Free", layout="wide")
st.title("🔥 X (Twitter) Post Impression Checker [FREE]")
st.markdown("**Không cần API Key** • Dùng FXTwitter public proxy • Upload file link → Lấy impressions")

def extract_tweet_id(url):
    patterns = [
        r'/status/(\d+)',
        r'twitter\.com/[^/]+/status/(\d+)',
        r'x\.com/[^/]+/status/(\d+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    # Fallback lấy số dài
    numbers = re.findall(r'\d{15,20}', url)
    return numbers[-1] if numbers else None

def fetch_tweet_metrics(tweet_ids):
    metrics = {}
    for tid in tweet_ids:
        try:
            url = f"https://api.fxtwitter.com/status/{tid}"
            headers = {
                "User-Agent": "Mantle-Squad-Impression-Tool/1.0 (by @leminhanh0709)"
            }
            resp = requests.get(url, headers=headers, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                tweet = data.get("tweet", {})
                metrics[tid] = {
                    "impression_count": tweet.get("views", 0),
                    "like_count": tweet.get("likes", 0),
                    "retweet_count": tweet.get("retweets", 0),
                    "reply_count": tweet.get("replies", 0),
                    "quote_count": tweet.get("quotes", 0),
                    "bookmark_count": tweet.get("bookmarks", 0),
                    "created_at": tweet.get("created_at", ""),
                    "text": tweet.get("text", "")[:100] + "..." if tweet.get("text") else ""
                }
            else:
                metrics[tid] = {"impression_count": 0, "error": f"HTTP {resp.status_code}"}
            
            time.sleep(1.2)  # Tránh rate limit
            
        except Exception as e:
            metrics[tid] = {"impression_count": 0, "error": str(e)}
    
    return metrics

# Upload
uploaded_file = st.file_uploader("Upload file chứa link X (CSV, Excel, TXT)", 
                                type=["csv", "xlsx", "xls", "txt"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            lines = uploaded_file.getvalue().decode("utf-8").splitlines()
            df = pd.DataFrame({"Link": [line.strip() for line in lines if line.strip()]})
        
        st.success(f"Đã load {len(df)} dòng")

        # Tự detect cột link
        link_col = None
        for col in df.columns:
            sample = df[col].astype(str).head(10).str.cat(sep=' ')
            if re.search(r'status|twitter|x\.com', sample, re.IGNORECASE):
                link_col = col
                break
        
        if not link_col and len(df.columns) == 1:
            link_col = df.columns[0]
        elif not link_col:
            link_col = st.selectbox("Chọn cột chứa link", df.columns)

        links = df[link_col].astype(str).tolist()

        if st.button("🚀 Bắt đầu Fetch Impressions (Free)", type="primary"):
            with st.spinner("Đang scrape qua FXTwitter... (chậm một chút vì free)"):
                tweet_data = []
                batch_size = 30  # An toàn
                
                progress_bar = st.progress(0)
                
                for i in range(0, len(links), batch_size):
                    batch = links[i:i+batch_size]
                    tweet_ids = []
                    link_map = {}
                    
                    for link in batch:
                        tid = extract_tweet_id(link)
                        if tid:
                            tweet_ids.append(tid)
                            link_map[tid] = link
                    
                    if tweet_ids:
                        metrics = fetch_tweet_metrics(tweet_ids)
                        for tid, m in metrics.items():
                            tweet_data.append({
                                "Original_Link": link_map.get(tid, ""),
                                "Tweet_ID": tid,
                                "Impressions": m.get("impression_count", 0),
                                "Likes": m.get("like_count", 0),
                                "Retweets": m.get("retweet_count", 0),
                                "Replies": m.get("reply_count", 0),
                                "Quotes": m.get("quote_count", 0),
                                "Bookmarks": m.get("bookmark_count", 0),
                                "Created_At": m.get("created_at", ""),
                                "Text_Sample": m.get("text", "")
                            })
                    
                    progress = min(100, int((i + batch_size) / len(links) * 100))
                    progress_bar.progress(progress)
                
                result_df = pd.DataFrame(tweet_data)
                
                st.subheader("📊 Kết quả")
                st.dataframe(result_df, use_container_width=True)
                
                # Download buttons
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Tải CSV", csv, f"x_impressions_{time.strftime('%Y%m%d_%H%M')}.csv", "text/csv")
                
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    result_df.to_excel(writer, index=False)
                st.download_button("📥 Tải Excel (.xlsx)", output.getvalue(), 
                                 f"x_impressions_{time.strftime('%Y%m%d_%H%M')}.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                
    except Exception as e:
        st.error(f"Lỗi: {str(e)}")

st.caption("Made for Minh Anh • Mantle Squad • Free version dùng FXTwitter (có thể chậm nếu fetch >100 links)")
