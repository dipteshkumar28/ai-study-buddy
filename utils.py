"""Shared defaults and prompts for AI Study Buddy (no sign-in needed)."""
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULTS = {
    "api_key": os.getenv("GROQ_API_KEY", ""), "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    "logged_in": True, "username": "Student", "user_email": "Guest mode · no sign-up needed",
    "achievements": [], "active_doc": None, "adaptive_pool": [], "concept_to_explain": "",
    "documents": {}, "explain_mode": "standard", "explain_result": "", "extracted_text": "",
    "fc_flipped": False, "fc_index": 0, "flashcards": [], "history": [], "last_study_date": None,
    "level": 1, "num_flashcards": 8, "num_quiz": 5, "pomodoro_break_min": 5, "pomodoro_work_min": 25,
    "pomodoros_done": 0, "quiz": [], "quiz_answers": {}, "quiz_history": [], "quiz_submitted": False,
    "revision_notes": [], "streak": 0, "stream_enabled": True, "strong_areas": [], "weak_areas": [],
    "study_start_time": None, "study_timer_active": False, "study_timer_mode": "work", "summary": "",
    "total_correct": 0, "total_flashcards_viewed": 0, "total_quizzes": 0, "voice_history": [], "xp": 0,
}

_JSON = "Return ONLY a valid JSON array, no markdown fences, no commentary."
_QFMT = ('[{{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A", '
         '"explanation": "...", "topic": "short concept name", "difficulty": 1}}]')

SUMMARY_PROMPT = ("You are an expert study assistant. Summarize the material below with: a 2-line TL;DR, "
                  "key points (bullets), key terms with definitions, and 3 self-test questions.\n\nMATERIAL:\n{text}")
FLASHCARD_PROMPT = ("Create {num} flashcards from the material. " + _JSON +
                    ' Format: [{{"front": "question", "back": "answer", "topic": "concept", "difficulty": 1}}] '
                    "(difficulty 1=easy, 2=medium, 3=hard).\n\nMATERIAL:\n{text}")
QUIZ_PROMPT = ("Write {num} multiple-choice questions from the material. Options MUST start with A), B), C), D). "
               "'answer' is the single correct letter. " + _JSON + " Format: " + _QFMT + "\n\nMATERIAL:\n{text}")
ADAPTIVE_QUIZ_PROMPT = ("Write {num} multiple-choice questions at difficulty {difficulty} (1-3) from the material, "
                        "focusing heavily on the student's weak areas: {weak_areas}. Options MUST start with A), B), "
                        "C), D). " + _JSON + " Format: " + _QFMT + "\n\nMATERIAL:\n{text}")
CHAT_PROMPT = ("You are a friendly tutor. Answer using the material when relevant.\n\nMATERIAL:\n{context}\n\n"
               "CONVERSATION:\n{history}\n\nSTUDENT: {question}\n\nTUTOR:")
REVISION_NOTES_PROMPT = ("Write concise revision notes from the material. Put extra emphasis on these weak "
                         "areas: {weak_areas}. Use headings, bullets, mnemonics and a quick-recall list.\n\nMATERIAL:\n{text}")
VOICE_TUTOR_PROMPT = ("You are a warm spoken-word tutor. Reply in 3-6 natural sentences, no markdown, no bullet "
                      "points, as if talking aloud.\n\nMATERIAL:\n{context}\n\nCONVERSATION:\n{history}\n\n"
                      "STUDENT: {question}\n\nTUTOR:")
MULTI_DOC_PROMPT = ("Analyze the documents below and respond to: {question}\nCite the document names. "
                    "Be structured and concise.\n\n{docs}")
_EX = "Concept: {concept}\n\nUse this material if relevant:\n{text}\n\n"
EXPLAIN_PROMPT = {
    "standard": "Explain the concept clearly: intuition, key idea, worked example, common mistake.\n" + _EX,
    "eli5": "Explain like I'm 5: tiny words, one fun everyday example, no jargon.\n" + _EX,
    "expert": "Give a deep, technical, rigorous explanation with edge cases and nuances.\n" + _EX,
    "analogy": "Explain ONLY through vivid analogies, metaphors and a short story.\n" + _EX,
    "visual": "Explain using ASCII diagrams, flow charts and tables, with brief captions.\n" + _EX,
}
