# ExaminerAI — AI-Powered Answer Sheet Evaluation System

An end-to-end pipeline that ingests handwritten answer sheet images, extracts text via OCR, retrieves subject-specific rubrics from a vector database, and evaluates student answers using a local LLM — producing marks, missing-point feedback, and confidence scores.

---

## ✨ Features

- **Automated OCR** — Extracts handwritten text from scanned answer sheets using PaddleOCR
- **Multi-Subject Support** — Separate vector collections for Maths, Science, and English
- **Intelligent Query Routing** — Automatically identifies the subject and selects the correct rubric collection
- **Hybrid Retrieval** — Combines dense vector search with BM25 keyword search (top-K rubric chunks)
- **CRAG Verification** — Corrective Retrieval-Augmented Generation checks retrieved chunks for relevance before grading
- **LLM-Based Evaluation** — Gemma (GPU-accelerated) evaluates answers against rubric points
- **Structured Output** — Returns marks, confidence score, missing points, and a review flag for edge cases

---

## System Architecture

```mermaid
flowchart TD
    A([📄 Upload answer sheet image]) --> B[Preprocess<br>crop & enhance]
    B --> C[PaddleOCR<br>extract handwritten text]
    C --> D[Clean extracted text]

    D --> E[(Vector DB<br>Maths · Science · English)]

    E --> F{Query Router<br>identify subject}
    F --> G[Retrieve top-K rubric chunks<br>Hybrid Search: vector + BM25]
    G --> H{CRAG Verifier<br>relevance check}

    H -->|YES| I[Verified Rubric + Student Answer<br>→ Gemma on GPU]
    H -->|PARTIAL| J[Re-retrieve / expand / flag]
    H -->|NO| J
    J --> H

    I --> K[Gemma evaluates answer<br>vs rubric points]
    K --> L[Assign marks +<br>confidence score]
    L --> M([Output<br>Marks · Missing Points · Review Flag])

    style A fill:#4B5563,color:#fff,stroke:none
    style M fill:#4B5563,color:#fff,stroke:none
    style F fill:#1D4ED8,color:#fff,stroke:none
    style H fill:#1D4ED8,color:#fff,stroke:none
    style E fill:#065F46,color:#fff,stroke:none
    style J fill:#7C3AED,color:#fff,stroke:none
```

---

## 🗂️ Project Structure

```
autograder/
├── ingestion/
│   ├── upload.py              # Image upload handler
│   ├── preprocess.py          # Crop, deskew, contrast enhancement
│   └── ocr.py                 # PaddleOCR wrapper + text extraction
│
├── retrieval/
│   ├── vector_db/
│   │   ├── collections.py     # Maths / Science / English collections
│   │   └── ingest_rubrics.py  # Rubric chunking & embedding ingestion
│   ├── router.py              # Subject classifier / query router
│   ├── hybrid_search.py       # Vector + BM25 hybrid retrieval
│   └── crag_verifier.py       # Relevance check & re-retrieval logic
│
├── evaluation/
│   ├── gemma_evaluator.py     # Gemma inference (GPU)
│   └── scoring.py             # Mark assignment + confidence scoring
│
├── output/
│   └── formatter.py           # Structured output: marks, gaps, flags
│
├── config.py                  # Model paths, DB URIs, hyperparameters
├── pipeline.py                # End-to-end orchestration
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### Prerequisites

| Requirement | Version |
|---|---|
| Python | ≥ 3.10 |
| CUDA | ≥ 11.8 (for Gemma GPU inference) |
| PaddlePaddle | ≥ 2.5 |
| Vector DB | Qdrant / Weaviate / ChromaDB |

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/autograder.git
cd autograder

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install PaddleOCR
pip install paddlepaddle-gpu paddleocr
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Vector Database
VECTOR_DB_URI=http://localhost:6333
VECTOR_DB_API_KEY=your_api_key_here

# Gemma Model
GEMMA_MODEL_PATH=/models/gemma-2b-it
GEMMA_DEVICE=cuda          # or cpu

# Retrieval
TOP_K=5
HYBRID_ALPHA=0.5           # 0 = pure BM25, 1 = pure vector
CRAG_THRESHOLD=0.75        # Relevance score cutoff

# Collections
MATHS_COLLECTION=maths_rubrics
SCIENCE_COLLECTION=science_rubrics
ENGLISH_COLLECTION=english_rubrics
```

---

## Usage

### Run the full pipeline on a single answer sheet

```python
from pipeline import AutoGrader

grader = AutoGrader()
result = grader.grade(image_path="answer_sheet.jpg")

print(result)
# {
#   "marks": 14,
#   "max_marks": 20,
#   "confidence": 0.87,
#   "missing_points": ["Did not mention Newton's third law", "No units on final answer"],
#   "review_flag": False
# }
```

### Ingest rubrics into the vector database

```bash
python retrieval/vector_db/ingest_rubrics.py \
  --subject science \
  --rubric_dir ./rubrics/science/ \
  --chunk_size 256
```

### Run from the command line

```bash
python pipeline.py --image answer_sheet.jpg --output results.json
```

---

## Output Schema

| Field | Type | Description |
|---|---|---|
| `marks` | `int` | Marks awarded to the student |
| `max_marks` | `int` | Total marks possible for the question |
| `confidence` | `float` | Grading confidence score (0.0 – 1.0) |
| `missing_points` | `list[str]` | Key rubric points absent from the answer |
| `review_flag` | `bool` | `True` if human review is recommended |
| `subject` | `str` | Detected subject (Maths / Science / English) |
| `ocr_text` | `str` | Raw extracted text from the answer sheet |

---

## Pipeline Deep Dive

### Step 2 — Preprocessing
Images are deskewed, contrast-enhanced, and cropped to isolate the answer region before OCR. This significantly improves extraction accuracy on low-quality scans.

### Step 3 — PaddleOCR
PaddleOCR runs a detection + recognition pipeline optimised for handwritten text. The output is a list of text blocks with bounding boxes.

### Step 5 — Vector DB Collections
Rubrics are pre-chunked and embedded (using a sentence-transformer model) into three separate collections — one per subject. Each chunk maps to a specific mark-scheme point.

### Step 6a — Query Router
A lightweight classifier (or prompt-based LLM call) determines the subject from the extracted answer text, then routes the query to the correct collection.

### Step 6b — Hybrid Search
Retrieval combines cosine-similarity vector search with BM25 keyword matching. The `HYBRID_ALPHA` parameter controls the blend. Results are re-ranked before passing to the verifier.

### Step 6c — CRAG Verifier
Each retrieved chunk is scored for relevance against the student answer. Chunks below `CRAG_THRESHOLD` trigger a re-retrieval with an expanded query. Partially relevant results are flagged for downstream handling.

### Step 7–9 — Gemma Evaluation
The verified rubric chunks and cleaned student answer are passed to Gemma with a structured grading prompt. Gemma returns marks per rubric point, a list of missing points, and an overall confidence estimate.

---

---

## Roadmap

- [ ] Web UI for teacher review and mark override
- [ ] Support equation recognition
- [ ] Fine-tuned subject-specific embedding models
- [ ] Batch processing for entire exam sets
- [ ] Export to CSV / PDF report cards

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) — Handwritten text recognition
- [Gemma](https://ai.google.dev/gemma) — Open LLM for answer evaluation
- [Qdrant](https://qdrant.tech/) — Vector database for rubric retrieval
