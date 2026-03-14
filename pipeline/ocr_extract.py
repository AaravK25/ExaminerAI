from paddleocr import PaddleOCR
import os

PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = True

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    device='gpu:0'
)

def ocrExtraction():

    proc_dir = os.listdir("data\\processed_images")

    proc_path_list = []

    for proc_img in proc_dir:
        path = os.path.join("data\\processed_images", proc_img)
        proc_path_list.append(path)                                     #Basically this updates the list with relative paths so that paddleocr can receive them correctly
        print(proc_path_list)

    for i in proc_path_list:
        print(i)
        result = ocr.predict(input=i)                                  #Iterating through the list and passing images to paddleocr
        for res in result:
            texts = res['rec_texts']
            scores = res['rec_scores']
            boxes = res['rec_boxes']

        mode = "a" if os.path.exists("data\\extracted_text\\question_paper.txt") and os.path.getsize("data\\extracted_text\\question_paper.txt") > 0 else "w"

        with open("data\\extracted_text\\question_paper.txt", mode, encoding="utf-8") as f:
            for text, score, box in zip(texts, scores, boxes):
                f.write(text + "\n")

# for text, score, box in zip(texts, scores, boxes):
        # print(f"[{score:.3f}] {text} [{boxes}]")
