from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Fungsi normalisasi pertanyaan ---
def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)  # hapus tanda baca
    return text

# --- Load Data QA dari CSV ---
try:
    df_qa = pd.read_csv("qa_data.csv")
    df_qa = df_qa.dropna(subset=["question", "answer"])
    df_qa["clean_question"] = df_qa["question"].apply(normalize_text)
except Exception as e:
    print(f"[ERROR] Gagal memuat qa_data.csv: {e}")
    df_qa = pd.DataFrame(columns=["question", "answer", "clean_question"])

# TF-IDF Setup
if not df_qa.empty:
    vectorizer = TfidfVectorizer()
    question_vectors = vectorizer.fit_transform(df_qa["clean_question"])

# FastAPI app setup
app = FastAPI()

# CORS Middleware (agar bisa diakses frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # untuk production ganti dengan domain frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model dari frontend
class QuestionInput(BaseModel):
    message: str

# --- Fungsi utama chatbot ---
def chatbot_response(user_question, threshold=0.05):
    if df_qa.empty:
        return "Maaf, basis data jawaban tidak tersedia."

    normalized_question = normalize_text(user_question)
    user_vector = vectorizer.transform([normalized_question])
    similarity_scores = cosine_similarity(user_vector, question_vectors)

    best_match_index = similarity_scores.argmax()
    best_match_score = similarity_scores[0, best_match_index]

    print(f"[DEBUG] Pertanyaan pengguna: {user_question}")
    print(f"[DEBUG] Normalized: {normalized_question}")
    print(f"[DEBUG] Pertanyaan terdekat: {df_qa.iloc[best_match_index]['question']}")
    print(f"[DEBUG] Skor kemiripan: {best_match_score}")

    if best_match_score < threshold:
        return "Maaf, saya belum mengerti pertanyaan Anda. Bisa dijelaskan lagi?"

    return df_qa.iloc[best_match_index]["answer"]

# --- Endpoint utama ---
@app.post("/chat")
def chat_endpoint(input: QuestionInput):
    response = chatbot_response(input.message)
    return {"reply": response}
