import re
import unicodedata


def clean_ocr_text(text: str) -> str:

    # Unicode normalisation — fixes ligatures, curly quotes, dashes
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u00a0", " ").replace("\u200b", "")

    # Fix broken hyphenated line splits (e.g. "respira-\ntion" → "respiration")
    text = re.sub(r"-\s*\n\s*", "", text)

    # Common handwriting OCR substitutions
    text = re.sub(r"(?<=\d)O(?=\d)", "0", text)          # O → 0 between digits
    text = re.sub(r"(?<=\d)l(?=\d)", "1", text)          # l → 1 between digits
    text = re.sub(r"(?<=[a-z])rn(?=[a-z])", "m", text)   # rn → m inside words

    # Remove noise lines (no alphanumeric content)
    lines = text.split("\n")
    lines = [ln for ln in lines if re.search(r"[a-zA-Z0-9]", ln)]

    # Strip each line and collapse multiple spaces
    lines = [re.sub(r" {2,}", " ", ln.strip()) for ln in lines]

    text = "\n".join(lines)

    # Fix punctuation spacing
    text = re.sub(r"\s+([.!?,;:])", r"\1", text)
    text = re.sub(r"([.!?,;:])(?=[a-zA-Z])", r"\1 ", text)

    return text.strip()


def clean_extracted_file(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        raw = f.read()

    cleaned = clean_ocr_text(raw)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned)


if __name__ == "__main__":
    clean_extracted_file(
        "data\\extracted_text\\question_paper.txt",
        "data\\extracted_text\\question_paper_cleaned.txt"
    )