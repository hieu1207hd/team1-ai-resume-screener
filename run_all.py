import os
from cv_pipeline import run_pipeline

DATA_DIR = "data"

print("🚀 BẮT ĐẦU OCR NHIỀU CV PDF + DOCX\n")

for file in os.listdir(DATA_DIR):

    file_path = os.path.join(DATA_DIR, file)

    if file.lower().endswith((".pdf", ".docx")):

        print(f"\n📘 ĐANG XỬ LÝ: {file}")
        run_pipeline(file_path)
