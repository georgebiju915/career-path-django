import re
from collections import Counter, defaultdict

# fuzzy matching
try:
    from rapidfuzz import process, fuzz
    rapidfuzz_available = True
except Exception:
    rapidfuzz_available = False

# optional spaCy for noun chunks / context
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# Replace this with a larger curated skills list (CSV/DB). For demo, a small subset:
DEFAULT_SKILL_LIST = [
    "python", "django", "flask", "javascript", "react", "nodejs", "aws",
    "azure", "docker", "kubernetes", "sql", "mysql", "postgres", "mongodb",
    "pandas", "numpy", "tensorflow", "pytorch", "excel", "powerbi", "tableau",
    "html", "css", "git", "linux", "bash", "spark", "hadoop",
]


def normalize_text(text):
    # very simple normalization; keep punctuation slightly because some skills like C++ or C# exist
    return text.strip()


def exact_skill_find(text_low, skill):
    # match whole word boundary; allow punctuation around skill tokens
    # handle skills with special chars like c++, c#
    if re.search(rf'(?<!\w){re.escape(skill)}(?!\w)', text_low):
        return True
    # also match variations like node.js vs nodejs
    alt = skill.replace(".", "").replace("-", "")
    if alt != skill and re.search(rf'(?<!\w){re.escape(alt)}(?!\w)', text_low):
        return True
    return False


def extract_skills_from_text(text, skills_list=None, fuzzy_threshold=85):
    """
    Returns dict:
      {
        'skills': { skill_name: count, ... },
        'matches': { skill_name: [positions], ... }  # positions are (start,end) or snippets
      }
    """
    skills_list = skills_list or DEFAULT_SKILL_LIST
    text_norm = normalize_text(text)
    text_low = text_norm.lower()

    found = Counter()
    matches = defaultdict(list)

    # exact matching (fast)
    for skill in skills_list:
        # lower compare
        if exact_skill_find(text_low, skill.lower()):
            count = len(re.findall(rf'(?<!\w){re.escape(skill.lower())}(?!\w)', text_low))
            if count == 0:
                # maybe find alt forms
                alt = skill.replace(".", "").replace("-", "")
                count = len(re.findall(rf'(?<!\w){re.escape(alt)}(?!\w)', text_low))
            if count > 0:
                found[skill] += count
                # collect short snippets as context
                for m in re.finditer(rf'(?<!\w)({re.escape(skill.lower())}|{re.escape(skill.replace(".", "").replace("-", ""))})(?!\w)', text_low):
                    start, end = m.start(), m.end()
                    snippet = text_norm[max(0, start-30):min(len(text_norm), end+30)]
                    matches[skill].append({"start": start, "end": end, "snippet": snippet})

    # fuzzy matching for remaining skills (optional)
    if rapidfuzz_available:
        # build a set of tokens to match against
        # We run fuzzy match skill list vs the whole text, but that's expensive — instead check unique tokens/phrases
        tokens = list(set(re.findall(r'\b[a-zA-Z0-9\-\+\.#]{2,}\b', text_low)))
        for skill in skills_list:
            if skill in found:
                continue
            # try best token match
            best = process.extractOne(skill.lower(), tokens, scorer=fuzz.partial_ratio)
            if best and best[1] >= fuzzy_threshold:
                token_value, score = best[0], best[1]
                # count occurrences of token_value
                for m in re.finditer(rf'(?<!\w){re.escape(token_value)}(?!\w)', text_low):
                    found[skill] += 1
                    start, end = m.start(), m.end()
                    snippet = text_norm[max(0, start-30):min(len(text_norm), end+30)]
                    matches[skill].append({"start": start, "end": end, "snippet": snippet})

    # spaCy fallback: noun chunks or TECH named entities heuristic
    if nlp and not found:
        try:
            doc = nlp(text_norm[:20000])
            for chunk in doc.noun_chunks:
                c = chunk.text.lower().strip()
                for skill in skills_list:
                    if skill.lower() in c and skill not in found:
                        found[skill] += 1
                        matches[skill].append({"start": chunk.start_char, "end": chunk.end_char, "snippet": chunk.text})
        except Exception:
            pass

    return {"skills": dict(found), "matches": dict(matches), "total_tokens": len(text_low.split())}