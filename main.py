from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
from fuzzywuzzy import fuzz
import re

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000/chat"], # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot_pipeline = pipeline("text-generation", model="microsoft/DialoGPT-medium")
FAQ_DATA = {
   "Apa itu sistem deteksi jalan berlubang?":
        "Sistem deteksi jalan berlubang adalah aplikasi yang menggunakan teknologi kecerdasan buatan dan pengolahan citra untuk mendeteksi keberadaan lubang pada permukaan jalan.",

    "Bagaimana cara kerja sistem ini?":
        "Sistem bekerja dengan menganalisis gambar atau video jalan menggunakan model deep learning untuk mengidentifikasi dan menandai lokasi jalan berlubang.",

    "Apa manfaat sistem deteksi jalan berlubang?":
        "Sistem membantu pemerintah dan masyarakat dalam mengidentifikasi kerusakan jalan lebih cepat sehingga dapat dilakukan perbaikan sebelum menyebabkan kecelakaan.",

    "Apakah sistem dapat mendeteksi secara real-time?":
        "Ya, jika diintegrasikan dengan kamera atau CCTV, sistem dapat melakukan deteksi jalan berlubang secara real-time.",

    "Bagaimana cara melaporkan jalan berlubang?":
        "Pengguna dapat mengunggah foto jalan yang rusak melalui aplikasi, kemudian sistem akan menganalisis dan menyimpan hasil deteksi.",

    "Apa tingkat akurasi sistem?":
        "Tingkat akurasi bergantung pada model yang digunakan, kualitas data pelatihan, dan kondisi gambar yang dianalisis."
}

# Keyword mappings for common terms
KEYWORD_SYNONYMS = {
    "jalan": [
        "jalan",
        "ruas jalan",
        "aspal",
        "jalan raya"
    ],

    "lubang": [
        "lubang",
        "jalan berlubang",
        "kerusakan jalan",
        "retak",
        "pothole"
    ],

    "deteksi": [
        "deteksi",
        "mendeteksi",
        "identifikasi",
        "analisis",
        "pengenalan"
    ],

    "lapor": [
        "lapor",
        "melaporkan",
        "pengaduan",
        "laporan"
    ],

    "akurasi": [
        "akurasi",
        "ketepatan",
        "precision",
        "hasil"
    ],

    "kamera": [
        "kamera",
        "cctv",
        "video",
        "gambar",
        "foto"
    ]
}

class UserInput(BaseModel):
    message: str
    
def preprocess_input(message: str) -> str:
    """Normalize user input: lowercase, remove extra spaces, and handle basic synonyms."""
    message = re.sub(r'\s+', ' ', message.strip().lower())
    # Replace synonyms with canonical terms
    for canonical, synonyms in KEYWORD_SYNONYMS.items():
        for synonym in synonyms:
            message = message.replace(synonym, canonical)
    return message

def find_best_faq_match(user_message: str) -> tuple[str, int]:
    """Find the best FAQ match using multiple fuzzy matching strategies."""
    best_match = None
    highest_score = 0
    for question in FAQ_DATA:
        # Preprocess FAQ question
        processed_question = preprocess_input(question)
        processed_message = preprocess_input(user_message)
        # Use multiple fuzzy matching strategies
        partial_score = fuzz.partial_ratio(processed_message, processed_question)
        token_sort_score = fuzz.token_sort_ratio(processed_message,
        processed_question)
        ratio_score = fuzz.ratio(processed_message, processed_question)
        # Combine scores (weighted average for better accuracy)
        combined_score = (partial_score * 0.5 + token_sort_score * 0.3 +
        ratio_score * 0.2)
        # Lowered threshold to allow looser matches
        if combined_score > 70 and combined_score > highest_score: # Lowered from 80 to 70
            best_match = question
            highest_score = combined_score
            
        # Keyword-based matching as a fallback
        if not best_match:
            user_words = set(processed_message.split())
            question_words = set(processed_question.split())
            common_keywords = user_words.intersection(question_words)
            if len(common_keywords) >= 2: # At least 2 common keywords
          
                best_match = question
                highest_score = 75 # Arbitrary score for keyword match
    return best_match, highest_score

@app.post("/chat")
async def chat(user_input: UserInput):
    user_message = user_input.message.strip()
    
    # Find the best FAQ match
    best_match, score = find_best_faq_match(user_message)
    if best_match and score > 70:
        return {"response": FAQ_DATA[best_match]}
    
    # Fallback to NLP
    try:
        response = chatbot_pipeline(
            user_message,
            max_length=150,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.9,
            temperature=0.7,
            pad_token_id=chatbot_pipeline.tokenizer.eos_token_id
        )[0]["generated_text"]
        
        # Remove input from output if present
        if response.startswith(user_message):
            response = response[len(user_message):].strip()
            
        return {"response": response or "Maaf, saya tidak bisa menghasilkan respons yang sesuai."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
            
@app.get("/faq")
async def faq():
    return FAQ_DATA