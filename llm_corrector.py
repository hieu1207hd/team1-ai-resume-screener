import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"


def llm_fix_text(lines, batch_size=20):
    fixed_lines = []

    for i in range(0, len(lines), batch_size):

        batch = lines[i:i + batch_size]

        prompt = f"""
Bạn là AI sửa lỗi OCR tiếng Việt.

Yêu cầu:
- Sửa chính tả tiếng Việt
- Ghép dòng bị gãy
- Không bịa nội dung
- Giữ nguyên ý
- Trả về MỖI DÒNG MỘT CÂU

Danh sách câu OCR:
{chr(10).join(batch)}

Kết quả:
"""

        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }

        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=180)
            data = r.json()

            if "response" not in data or not data["response"].strip():
                print("⚠️ LLM không trả content")
                fixed_lines.extend(batch)
                continue

            result_lines = [
                line.strip()
                for line in data["response"].split("\n")
                if line.strip()
            ]

            fixed_lines.extend(result_lines)

            time.sleep(0.3)

        except Exception as e:
            print("⚠️ LLM lỗi:", e)
            fixed_lines.extend(batch)

    return fixed_lines
