import streamlit as st
import hashlib
from collections import deque, Counter

def calculate_md5(input_str: str) -> str:
    return hashlib.md5(input_str.encode()).hexdigest()

def complex_calculation(input_str: str) -> float:
    md5_hash = int(hashlib.md5(input_str.encode()).hexdigest(), 16)
    sha256_hash = int(hashlib.sha256(input_str.encode()).hexdigest(), 16)
    blake2b_hash = int(hashlib.blake2b(input_str.encode()).hexdigest(), 16)
    combined_hash = (
        (md5_hash % 100) * 0.3 +
        (sha256_hash % 100) * 0.4 +
        (blake2b_hash % 100) * 0.3
    )
    return combined_hash % 100

def bayesian_adjustment(recent_results: deque) -> float:
    count = Counter(recent_results)
    total = len(recent_results)
    if total == 0:
        return 50.0
    prob_xiu = (count["Xỉu"] + 1) / (total + 2)
    return prob_xiu * 100

def detect_trend(recent_results: deque) -> str:
    if len(recent_results) < 4:
        return "Không đủ dữ liệu phân tích cầu."
    trend_str = ''.join(['T' if res == "Tài" else 'X' for res in recent_results])
    if trend_str.endswith('TTTT'):
        return "Cầu bệt Tài"
    elif trend_str.endswith('XXXX'):
        return "Cầu bệt Xỉu"
    elif trend_str.endswith('TXTX'):
        return "Cầu 1-1"
    elif trend_str.endswith('TXT'):
        return "Cầu 1-2-1"
    elif trend_str.endswith('TTTX'):
        return "Cầu bệt ngắt (Tài ngắt)"
    elif trend_str.endswith('XXXT'):
        return "Cầu bệt ngắt (Xỉu ngắt)"
    elif trend_str.endswith('TXXT'):
        return "Cầu 2-1-2"
    elif trend_str.endswith('XXTXX'):
        return "Cầu 3-2"
    if "TTT" in trend_str[-5:] and trend_str[-1] == "X":
        return "Cầu bẻ từ Tài sang Xỉu"
    elif "XXX" in trend_str[-5:] and trend_str[-1] == "T":
        return "Cầu bẻ từ Xỉu sang Tài"
    return "Cầu không xác định"

def adjust_prediction(percentage: float, trend: str) -> float:
    if trend == "Cầu bệt Tài":
        percentage -= 7
    elif trend == "Cầu bệt Xỉu":
        percentage += 7
    elif trend == "Cầu 1-1":
        percentage += 5 if percentage > 50 else -5
    elif trend == "Cầu 1-2-1":
        percentage += 3
    elif trend in ["Cầu bệt ngắt (Tài ngắt)", "Cầu bệt ngắt (Xỉu ngắt)"]:
        percentage += 2
    elif trend == "Cầu 2-1-2":
        percentage -= 4
    elif trend == "Cầu 3-2":
        percentage += 6
    elif trend == "Cầu bẻ từ Tài sang Xỉu":
        percentage += 10
    elif trend == "Cầu bẻ từ Xỉu sang Tài":
        percentage -= 10
    return max(0, min(100, percentage))

# === Giao diện Streamlit ===
st.title("🎯 Tool Phân Tích Cầu 68 Game Bài")
username = st.text_input("🔑 Nhập tên hiển thị của bạn:", "Ẩn danh")

input_str = st.text_input("🎰 Nhập chuỗi bất kỳ 68 game bài:")

if 'recent_results' not in st.session_state:
    st.session_state.recent_results = deque(maxlen=10)

if input_str:
    md5_hash = calculate_md5(input_str)
    base_percent = complex_calculation(input_str)
    bayes_percent = bayesian_adjustment(st.session_state.recent_results)
    trend = detect_trend(st.session_state.recent_results)
    adjusted_percent = adjust_prediction(bayes_percent, trend)

    st.subheader("📊 Kết Quả Phân Tích:")
    st.markdown(f"**👤 Người dùng:** `{username}`")
    st.markdown(f"**🔗 MD5 Chuỗi:** `{md5_hash}`")
    st.markdown(f"**🟢 Tài:** `{100 - adjusted_percent:.2f}%`")
    st.markdown(f"**🔵 Xỉu:** `{adjusted_percent:.2f}%`")
    st.markdown(f"**📈 Xu hướng cầu:** `{trend}`")

    result = st.selectbox("📝 Nhập kết quả thực tế:", ["", "Tài", "Xỉu"])
    if result:
        st.session_state.recent_results.append(result)
        st.success(f"✅ Đã lưu kết quả: {result}")

