from docx import Document

def read_docx_cv(docx_path):
    doc = Document(docx_path)

    lines = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            lines.append(text)

    return lines
