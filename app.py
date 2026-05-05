from fastapi import FastAPI, UploadFile, File
import pdfplumber, re, shutil, os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 👉 IMPORTANT: replace with your full answer key
ANSWER_KEY = {
    "1505611633": 2,
    "1505611666": 2
}

def extract_responses(pdf_path):
    responses = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            matches = re.findall(
                r"Question ID : (\d+).*?Chosen Option : (\d+)",
                text,
                re.DOTALL
            )
            for qid, ans in matches:
                responses[qid] = int(ans)
    return responses

def calculate_score(responses):
    correct = wrong = 0
    for qid, correct_ans in ANSWER_KEY.items():
        if qid in responses:
            if responses[qid] == correct_ans:
                correct += 1
            else:
                wrong += 1
    score = correct * 2 - wrong * 0.5
    return {
        "score": score,
        "correct": correct,
        "wrong": wrong,
        "accuracy": round(correct / (correct + wrong), 3) if (correct + wrong) else 0
    }

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    path = f"{UPLOAD_DIR}/{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    responses = extract_responses(path)
    return calculate_score(responses)
