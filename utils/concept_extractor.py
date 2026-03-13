import re
import spacy

nlp = spacy.load("en_core_web_sm")

STOP_CONCEPTS = {
    "result", "name", "label", "config", "model", "data", "test", "train",
    "use", "used", "using", "type", "value"
}


def is_valid_concept(text: str) -> bool:
    text = text.strip()

    if not text:
        return False
    if len(text) < 3:
        return False
    if len(text.split()) > 4:
        return False
    if re.search(r'[{}[\]();=<>/_#]', text):
        return False
    if re.search(r'^\d+$', text):
        return False
    if re.search(r'[_]{1,}', text):
        return False
    if "import " in text.lower():
        return False
    if text.lower() in STOP_CONCEPTS:
        return False

    alpha_count = sum(ch.isalpha() for ch in text)
    if alpha_count < 2:
        return False

    return True


def clean_text(text: str) -> str:
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue
        if line.startswith("import ") or line.startswith("from "):
            continue
        if "print(" in line:
            continue
        if "=" in line and len(line) < 40:
            continue
        if re.search(r'[{}[\]<>]', line):
            continue

        cleaned_lines.append(line)

    return " ".join(cleaned_lines)


def extract_concepts(text):
    text = clean_text(text)
    doc = nlp(text)

    concepts = set()

    for ent in doc.ents:
        ent_text = ent.text.strip()
        if is_valid_concept(ent_text):
            concepts.add(ent_text)

    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.strip()
        if is_valid_concept(chunk_text):
            concepts.add(chunk_text)

    cleaned = sorted(concepts)
    return cleaned[:30]