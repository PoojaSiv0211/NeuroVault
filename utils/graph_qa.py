import re


def normalize(text: str) -> str:
    return text.strip().lower()


def answer_graph_query(question: str, relations: list[tuple[str, str, str]]) -> str:
    if not question.strip():
        return "Please enter a question."

    q = normalize(question)

    if not relations:
        return "No relations are available yet. Generate a graph first."

    # Build graph lookups
    outgoing = {}
    incoming = {}

    for subject, relation, obj in relations:
        s = normalize(subject)
        r = normalize(relation)
        o = normalize(obj)

        outgoing.setdefault(s, []).append((r, obj))
        incoming.setdefault(o, []).append((subject, r))

    # Pattern 1: What is X / Explain X
    m = re.search(r"(what is|explain|tell me about)\s+(.+)", q)
    if m:
        concept = normalize(m.group(2).replace("?", ""))

        neighbors = []

        for subject, relation, obj in relations:
            if normalize(subject) == concept:
                neighbors.append(f"{subject} --{relation}--> {obj}")
            elif normalize(obj) == concept:
                neighbors.append(f"{subject} --{relation}--> {obj}")

        if neighbors:
            return f"Graph knowledge about '{concept}':\n\n" + "\n".join(f"- {n}" for n in neighbors)

        return f"'{concept}' exists but no relations were found."

    # Pattern 2: What is related to X
    m = re.search(r"related to (.+)", q)
    if m:
        concept = normalize(m.group(1).replace("?", ""))

        answers = []
        for subject, relation, obj in relations:
            if normalize(subject) == concept or normalize(obj) == concept:
                answers.append(f"{subject} --{relation}--> {obj}")

        if answers:
            return "Related knowledge:\n\n" + "\n".join(f"- {a}" for a in answers)

        return f"No relations found for '{concept}'."

    # Pattern 3: What does X use/include/apply
    m = re.search(r"what does (.+?) ([a-z]+)", q)
    if m:
        subject_query = normalize(m.group(1))
        relation_query = normalize(m.group(2))

        matches = []
        for relation, obj in outgoing.get(subject_query, []):
            if relation == relation_query:
                matches.append(obj)

        if matches:
            return f"{subject_query} {relation_query}s: " + ", ".join(matches)

        return "No matches found."

    # Fallback search
    keyword = q.replace("?", "")
    matches = []

    for subject, relation, obj in relations:
        if keyword in normalize(subject) or keyword in normalize(obj):
            matches.append(f"{subject} --{relation}--> {obj}")

    if matches:
        return "Closest matches:\n\n" + "\n".join(f"- {m}" for m in matches)

    return "I couldn't find anything related to that question."