import fitz  # PyMuPDF
import os

def convert_pdf_to_images(pdf_path, output_dir="images", dpi=300):
    """
    Chuyển toàn bộ trang PDF sang ảnh
    """

    print("  PDF → IMAGE (PyMuPDF)")

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    image_paths = []

    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        pix = page.get_pixmap(dpi=dpi)

        image_path = os.path.join(output_dir, f"page_{page_index}.jpg")
        pix.save(image_path)

        image_paths.append(image_path)
        print(f"✅ Trang {page_index + 1} → {image_path}")

    print(" Đã chuyển PDF sang ảnh \n")

    return image_paths
