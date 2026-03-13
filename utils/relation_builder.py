import re
import spacy

nlp = spacy.load("en_core_web_sm")


def valid_piece(text: str) -> bool:
    text = text.strip()

    if not text or len(text) < 3:
        return False
    if len(text.split()) > 5:
        return False
    if re.search(r'[{}[\]();=<>/_#]', text):
        return False
    if re.search(r'^\d+$', text):
        return False

    return True


def extract_relations(text):
    doc = nlp(text)
    relations = []

    for sent in doc.sents:
        subjects = [tok for tok in sent if tok.dep_ in ("nsubj", "nsubjpass")]
        objects = [tok for tok in sent if tok.dep_ in ("dobj", "pobj", "attr")]
        verbs = [tok for tok in sent if tok.pos_ == "VERB"]

        if not (subjects and objects and verbs):
            continue

        subject = subjects[0].text.strip()
        verb = verbs[0].lemma_.strip()
        obj = objects[0].text.strip()

        if valid_piece(subject) and valid_piece(obj) and valid_piece(verb):
            relations.append((subject, verb, obj))

    unique_relations = []
    seen = set()

    for rel in relations:
        if rel not in seen:
            seen.add(rel)
            unique_relations.append(rel)

    return unique_relations[:20]