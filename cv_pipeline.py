import os
import json
import cv2
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

from pdf_to_image import convert_pdf_to_images
from text_cleaner import clean_text
from text_corrector import fix_ocr_text, correct_vi_block
from docx_reader import read_docx_cv

from text_corrector import fix_ocr_text, correct_vi_block

# ==================================================
# OCR ENGINE
# ==================================================
ocr = RapidOCR(det_lang="vi", rec_lang="vi")


# ==================================================
# IMAGE PREPROCESS
# ==================================================
def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    return gray


# ==================================================
# MERGE LINE → PARAGRAPH
# ==================================================
def merge_lines(lines):
    merged = []
    buffer = ""

    for line in lines:
        if not buffer:
            buffer = line
        elif line[0].islower():
            buffer += " " + line
        else:
            merged.append(buffer)
            buffer = line

    if buffer:
        merged.append(buffer)

    return merged


# ==================================================
# BASIC CV PARSER
# ==================================================
def parse_cv(lines):
    cv = {
        "name": "",
        "email": "",
        "phone": "",
        "education": [],
        "skills": [],
        "projects": [],
        "full_text": lines
    }

    for line in lines:
        l = line.lower()

        if "@" in l and not cv["email"]:
            cv["email"] = line

        elif any(c.isdigit() for c in l) and len(line) >= 9 and not cv["phone"]:
            cv["phone"] = line

        elif "đại học" in l or "university" in l:
            cv["education"].append(line)

        elif any(k in l for k in [
            "machine learning",
            "computer vision",
            "yolo",
            "python",
            "opencv",
            "deep learning"
        ]):
            cv["skills"].append(line)

        elif "dự án" in l or "project" in l:
            cv["projects"].append(line)

        elif not cv["name"] and line.isupper() and len(line) > 5:
            cv["name"] = line

    return cv


# ==================================================
# MAIN PIPELINE
# ==================================================
def run_pipeline(file_path, output_root="output"):

    file_name = os.path.splitext(os.path.basename(file_path))[0]
    safe_name = file_name.replace(" ", "_")
    out_dir = os.path.join(output_root, safe_name)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n📘 XỬ LÝ FILE: {file_path}")

    # ==================================================
    # CASE 1: DOCX (KHÔNG OCR)
    # ==================================================
    if file_path.lower().endswith(".docx"):
        print("📄 DOCX → đọc trực tiếp")

        raw_lines = read_docx_cv(file_path)
        merged = merge_lines(raw_lines)
        corrected = correct_vi_block(merged)

        _save_texts(out_dir, raw_lines, merged, corrected)

        cv_info = parse_cv(corrected)
        _save_cv(out_dir, cv_info)

        print("✅ DONE DOCX:", out_dir)
        return out_dir

    # ==================================================
    # CASE 2: PDF → OCR
    # ==================================================
    print("📘 PDF → OCR")

    image_paths = convert_pdf_to_images(file_path)
    raw_lines = []
    bbox_json = []

    bbox_dir = os.path.join(out_dir, "bbox_images")
    os.makedirs(bbox_dir, exist_ok=True)

    for page_id, img_path in enumerate(image_paths):

        img = cv2.imread(img_path)
        if img is None:
            continue

        img_pre = preprocess(img)
        result = ocr(img_pre)

        if isinstance(result, tuple):
            result = result[0]

        if not result:
            continue

        draw = img.copy()
        page_lines = []

        for box, text, score in result:
            if score < 0.5:
                continue

            text = clean_text(text)
            text = fix_ocr_text(text)

            if len(text) < 2:
                continue

            bbox_json.append({
                "page": page_id,
                "text": text,
                "bbox": box,
                "score": float(score)
            })

            pts = np.array(box).astype(int)
            cv2.polylines(draw, [pts], True, (0, 255, 0), 2)

            y = min(p[1] for p in box)
            page_lines.append((y, text))

        page_lines.sort(key=lambda x: x[0])
        raw_lines.extend([t for _, t in page_lines])

        Image.fromarray(
            cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)
        ).save(os.path.join(bbox_dir, f"page_{page_id}_bbox.jpg"))

    # ==================================================
    # POST PROCESS
    # ==================================================
    merged = merge_lines(raw_lines)
    corrected = correct_vi_block(merged)

    _save_texts(out_dir, raw_lines, merged, corrected)

    with open(os.path.join(out_dir, "ocr_bbox.json"),
              "w", encoding="utf-8") as f:
        json.dump(bbox_json, f, ensure_ascii=False, indent=2)

    cv_info = parse_cv(corrected)
    _save_cv(out_dir, cv_info)

    print("✅ DONE OCR:", out_dir)
    return out_dir


# ==================================================
# UTILS
# ==================================================
def _save_texts(out_dir, raw, merged, corrected):
    with open(os.path.join(out_dir, "full_text_raw.txt"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(raw))

    with open(os.path.join(out_dir, "full_text_merged.txt"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(merged))

    with open(os.path.join(out_dir, "full_text_corrected.txt"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(corrected))


def _save_cv(out_dir, cv_info):
    with open(os.path.join(out_dir, "cv_info.json"),
              "w", encoding="utf-8") as f:
        json.dump(cv_info, f, ensure_ascii=False, indent=2)
