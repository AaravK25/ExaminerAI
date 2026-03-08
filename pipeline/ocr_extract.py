from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    device='gpu:0'
)

result = ocr.predict(input="data/processed_images/IMG_20260205_175116.jpg")

for res in result:
    texts = res['rec_texts']
    scores = res['rec_scores']
    boxes = res['rec_boxes']

    for text, score, box in zip(texts, scores, boxes):
        print(f"[{score:.3f}] {text}")