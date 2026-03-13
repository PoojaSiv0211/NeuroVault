import streamlit as st
from utils.text_loader import load_text_from_file
from utils.concept_extractor import extract_concepts
from utils.relation_builder import extract_relations
from utils.graph_builder import build_graph
from utils.graph_qa import answer_graph_query

st.set_page_config(page_title="NeuroVault", layout="wide")

st.title(" NeuroVault")
st.caption("AI-Powered Knowledge Graph Builder for Notes and Documents")

uploaded_file = st.file_uploader("Upload a TXT or PDF file", type=["txt", "pdf"])
manual_text = st.text_area("Or paste your notes here", height=220)

text = ""

if uploaded_file is not None:
    text = load_text_from_file(uploaded_file)

if manual_text.strip():
    text = manual_text.strip()

if "concepts" not in st.session_state:
    st.session_state.concepts = []

if "relations" not in st.session_state:
    st.session_state.relations = []

if "graph_path" not in st.session_state:
    st.session_state.graph_path = ""

if st.button("Generate Knowledge Graph"):
    if not text.strip():
        st.warning("Please upload a file or paste some text.")
    else:
        with st.spinner("Extracting concepts and building graph..."):
            concepts = extract_concepts(text)
            relations = extract_relations(text)
            graph_path = build_graph(concepts, relations)

            st.session_state.concepts = concepts
            st.session_state.relations = relations
            st.session_state.graph_path = graph_path

        st.success("Knowledge graph generated successfully.")

if st.session_state.graph_path:
    concepts = st.session_state.concepts
    relations = st.session_state.relations
    graph_path = st.session_state.graph_path

    st.subheader("Graph Statistics")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Concepts Extracted", len(concepts))

    with col2:
        st.metric("Relations Detected", len(relations))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Extracted Concepts")
        st.json(concepts)

    with col2:
        st.markdown("### Extracted Relations")
        st.json(relations)

    st.markdown("## Knowledge Graph")
    with open(graph_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=800, scrolling=True)

    with open(graph_path, "rb") as f:
        st.download_button(
            "Download Knowledge Graph",
            f,
            file_name="knowledge_graph.html",
            mime="text/html"
        )

    st.markdown("---")
    st.markdown("## Ask Questions About the Graph")

    user_question = st.text_input(
        "Ask something about the generated graph",
        placeholder="Example: What is related to learning?"
    )

    if st.button("Ask Graph"):
        answer = answer_graph_query(user_question, relations)
        st.markdown("### Answer")
        st.write(answer)
        st.markdown("---")
st.markdown("## Explore a Concept")

concept_query = st.text_input(
    "Enter a concept to explore",
    placeholder="Example: learning"
)

if st.button("Explore Concept"):
    concept = concept_query.strip().lower()

    if not concept:
        st.warning("Please enter a concept.")
    else:
        related = []
        incoming = []
        outgoing = []

        for subject, relation, obj in st.session_state.relations:

            if subject.lower() == concept:
                outgoing.append((relation, obj))
                related.append(obj)

            if obj.lower() == concept:
                incoming.append((subject, relation))
                related.append(subject)

        if not incoming and not outgoing:
            st.info(f"No graph connections found for '{concept_query}'.")
        else:

            st.subheader(f"Concept: {concept_query}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Outgoing Relations")
                if outgoing:
                    for rel, obj in outgoing:
                        st.write(f"{concept_query} → {rel} → {obj}")
                else:
                    st.write("None")

            with col2:
                st.markdown("### Incoming Relations")
                if incoming:
                    for subj, rel in incoming:
                        st.write(f"{subj} → {rel} → {concept_query}")
                else:
                    st.write("None")

            st.markdown("### Related Concepts")

            unique_related = list(set(related))

            if unique_related:
                for item in unique_related:
                    st.write(f"• {item}")
            else:
                st.write("None")