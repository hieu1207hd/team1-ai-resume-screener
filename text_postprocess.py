import re

# =====================================================
# 1. DANH SÁCH LỖI OCR PHỔ BIẾN TIẾNG VIỆT
# =====================================================

OCR_REPLACE_MAP = {

    # ===== cơ bản =====
    "cong nghe": "công nghệ",
    "gia thong": "giao thông",
    "thong tin": "thông tin",
    "ky nang": "kỹ năng",
    "hoc van": "học vấn",
    "kinh nghiem": "kinh nghiệm",
    "du an": "dự án",
    "muc tieu": "mục tiêu",
    "trinh do": "trình độ",
    "chuyen mon": "chuyên môn",
    "thuc tap": "thực tập",
    "sinh vien": "sinh viên",

    # ===== sai dấu =====
    "xur ly": "xử lý",
    "du lieu": "dữ liệu",
    "phan tich": "phân tích",
    "nghien cuu": "nghiên cứu",
    "thiet ke": "thiết kế",
    "lap trinh": "lập trình",
    "toi uu": "tối ưu",

    # ===== OCR nhầm chữ =====
    "dai hoc": "đại học",
    "truong dai hoc": "trường đại học",
    "ky thuat": "kỹ thuật",
    "phan mem": "phần mềm",
    "he thong": "hệ thống",

    # ===== CV domain =====
    "tri tue nhan tao": "trí tuệ nhân tạo",
    "thi giac may tinh": "thị giác máy tính",
    "hoc may": "học máy",
    "deep leaming": "deep learning",
    "machlne learnlng": "machine learning",

    # ===== phổ biến OCR =====
    "dugc": "được",
    "duoc": "được",
    "dugc": "được",
    "trlnh": "trình",
    "kl nang": "kỹ năng",
    "kl nãng": "kỹ năng",

    # ===== lỗi chữ hoa =====
    "Cong nghe": "Công nghệ",
    "Giao thong": "Giao thông",
    "Dai hoc": "Đại học",
}


# =====================================================
# 2. REGEX BẢO VỆ CÁC THỨ KHÔNG ĐƯỢC SỬA
# =====================================================

EMAIL_REGEX = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
URL_REGEX = re.compile(r"https?://\S+")
PHONE_REGEX = re.compile(r"\b0\d{8,10}\b")


# =====================================================
# 3. HÀM CHÍNH SỬA OCR
# =====================================================

def fix_ocr_text(text: str) -> str:
    """
    Sửa lỗi OCR tiếng Việt bằng rule-based
    KHÔNG dùng AI
    KHÔNG phá email / link / số điện thoại
    """

    if not text or len(text) < 2:
        return text

    original = text

    # -----------------------------
    # bảo vệ dữ liệu đặc biệt
    # -----------------------------
    protected = {}

    def protect(pattern, prefix):
        nonlocal text
        for i, m in enumerate(pattern.findall(text)):
            key = f"{prefix}_{i}"
            protected[key] = m
            text = text.replace(m, key)

    protect(EMAIL_REGEX, "EMAIL")
    protect(URL_REGEX, "URL")
    protect(PHONE_REGEX, "PHONE")

    # -----------------------------
    # normalize
    # -----------------------------
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()

    # -----------------------------
    # replace OCR errors
    # -----------------------------
    for wrong, correct in OCR_REPLACE_MAP.items():
        text = re.sub(rf"\b{re.escape(wrong)}\b", correct, text)

    # -----------------------------
    # khôi phục dữ liệu bảo vệ
    # -----------------------------
    for k, v in protected.items():
        text = text.replace(k, v)

    # -----------------------------
    # viết hoa chữ đầu
    # -----------------------------
    if text:
        text = text[0].upper() + text[1:]

    return text
