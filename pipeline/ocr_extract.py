from paddleocr import PaddleOCR
import os
from paddleocr import PPStructureV3
import google.generativeai as genai

api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    device='gpu:0'
)

structure = PPStructureV3(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    device='gpu:0'
)

def clean_with_gemini(raw_text: str) -> str:
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    You are cleaning up OCR-extracted text from a school question paper.

    The raw OCR output below may have:
    - Missing spaces between words (e.g. "Whatisthe" should be "What is the")
    - Broken or malformed markdown tables
    - Incorrect reading order
    - Merged or split question numbers
    - Garbled math/chemical formulas

    Please fix all of these issues and return clean, properly formatted markdown.

    Rules:
    - Preserve all question numbers and marks
    - Reconstruct tables correctly using proper markdown table syntax
    - Do NOT generate excessively long lines of dashes
    - Keep markdown table separators concise (max 10-15 dashes)
    - Avoid repetitive characters (e.g., ----- repeated many times)
    - If unsure about table structure, return plain text instead
    - Fix spacing between words
    - Keep mathematical expressions readable (use plain text if LaTeX is broken)
    - Do NOT add, remove, or change any actual content — only fix formatting

    Raw OCR text:
    {raw_text}

    Return ONLY the cleaned markdown. No explanation.
    """

    response = model.generate_content(prompt)

    return response.text  

def ocrExtraction():

    proc_dir = os.listdir("data\\processed_images")

    proc_path_list = []

    for proc_img in proc_dir:
        path = os.path.join("data\\processed_images", proc_img)
        proc_path_list.append(path)

    for i in proc_path_list:

        result = structure.predict(input=i)
        extracted_texts = []

        for res in result:
            md = res.markdown
            page_text = md.get("markdown_texts", "")
            if isinstance(page_text, list):
                extracted_texts.extend([str(t).strip("\n") for t in page_text if str(t).strip()])
            else:
                page_text = str(page_text).strip("\n")
                if page_text.strip():
                    extracted_texts.append(page_text)

        mode = "a" if os.path.exists("data\\extracted_text\\question_paper.md") and os.path.getsize("data\\extracted_text\\question_paper.md") > 0 else "w"

        with open("data\\extracted_text\\question_paper.md", mode, encoding="utf-8") as f:
            full_text = "\n".join(text for text in extracted_texts)
            full_text = clean_with_gemini(full_text)  #clean before writing
            f.write(full_text + "\n\n")

    return "Successfully Extracted for:", proc_path_list

a = ocrExtraction()
print(a)