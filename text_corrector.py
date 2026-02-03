from dotenv import load_dotenv
load_dotenv()

import re

# ===== BẬT / TẮT PROTONX =====
USE_PROTONX = False   # 👈 đổi True nếu muốn refine nhẹ

try:
    import protonx
    _client = protonx.ProtonX(mode="online")
except Exception:
    _client = None


# ===============================
# RULE OCR TIẾNG VIỆT (MẪU – MỞ RỘNG ĐƯỢC 300+)
# ===============================
OCR_RULES = {
    r"\bH6\b": "Hỗ",
    r"\bC6\b": "Có",
    r"\btrg\b": "trợ",
    r"\bdur\b": "dự",
    r"\blieu\b": "liệu",
    r"\bcuru\b": "cứu",
    r"\bnghien\b": "nghiên",
    r"\bky nang\b": "kỹ năng",
    r"\bdu an\b": "dự án",
    r"\btrinh do\b": "trình độ",
    r"\bthong tin lien he\b": "thông tin liên hệ",
}

def apply_ocr_rules(text: str) -> str:
    for p, r in OCR_RULES.items():
        text = re.sub(p, r, text, flags=re.IGNORECASE)
    return text


def correct_vi_block(lines):
    """
    - KHÔNG bịa chữ
    - Rule-based OCR là chính
    - ProtonX chỉ refine nhẹ (nếu bật)
    """
    if not lines:
        return lines

    # 1️⃣ Rule OCR
    fixed = [apply_ocr_rules(l) for l in lines]
    block = "\n".join(fixed)

    # 2️⃣ Mask email
    emails = re.findall(r"\S+@\S+", block)
    for e in emails:
        block = block.replace(e, "<EMAIL>")

    # 3️⃣ ProtonX (OPTIONAL)
    if USE_PROTONX and _client:
        try:
            block = _client.normalizer_http.correct(block)
        except Exception:
            pass

    # 4️⃣ Unmask
    for e in emails:
        block = block.replace("<EMAIL>", e, 1)

    return block.split("\n")
