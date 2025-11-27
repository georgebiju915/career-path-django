import re
from collections import Counter
# Optionally use spaCy for better NER
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

SKILL_KEYWORDS = {"python","django","react","aws","docker","sql","excel","pandas","tensorflow"}

def extract_text_from_pdf(pdf_path):
    # For production, use tika or pdfminer.six to extract text.
    from io import BytesIO
    import textract
    return textract.process(pdf_path).decode("utf-8", errors="ignore")

def parse_resume_text(text):
    skills_found = set()
    text_low = text.lower()
    for skill in SKILL_KEYWORDS:
        if skill in text_low:
            skills_found.add(skill)
    # Named entity / job titles via spaCy (optional)
    titles = []
    if nlp:
        doc = nlp(text[:20000])
        for ent in doc.ents:
            if ent.label_ in ("ORG","PERSON","NORP","PRODUCT"):  # tune as needed
                titles.append(ent.text)
    return {
        "skills": list(skills_found),
        "title_candidates": titles,
        "skill_counts": dict(Counter(re.findall(r'\b[a-zA-Z+-#]+\b', text_low)))
    }