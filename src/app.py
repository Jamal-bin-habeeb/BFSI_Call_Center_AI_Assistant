import streamlit as st
import json
import os
from sentence_transformers import SentenceTransformer, util
from model_engine import SLMEngine
from rag_engine import RAGEngine

# ── Resolve paths relative to project root ──────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(PROJECT_ROOT, "bfsi_alpaca_1_to_160_final_clean.json")

# Page Config
st.set_page_config(page_title="BFSI AI Assistant", layout="wide")


# ── Initialize Systems ──────────────────────────────────────────────────────
@st.cache_resource
def load_resources():
    st.text("Loading resources...")

    # 1. Load Dataset (PRD §3.1: 150+ Alpaca samples)
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # 2. Load Embedding Model for Similarity
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    match_texts = []
    for item in dataset:
        text = item["instruction"]
        if item.get("input"):
            text += " " + item["input"]
        match_texts.append(text)
    dataset_embeddings = embedder.encode(match_texts, convert_to_tensor=True)

    # 3. Load RAG (PRD §3.3: Knowledge retrieval)
    rag = RAGEngine(
        data_dir=os.path.join(PROJECT_ROOT, "data"),
        db_path=os.path.join(PROJECT_ROOT, "vector_store.pkl"),
    )
    rag.load_vector_store()

    # 4. Load SLM (PRD §3.2: Lightweight, local)
    slm = SLMEngine()
    slm.load_model()

    return dataset, dataset_embeddings, embedder, rag, slm


try:
    dataset, dataset_embeddings, embedder, rag, slm = load_resources()
    st.success("System Ready!")
except Exception as e:
    st.error(f"Error loading system: {e}")
    st.stop()


# ── Helpers ──────────────────────────────────────────────────────────────────
def get_best_match(query, threshold=0.70):
    """PRD §4 Tier 1: Dataset Match — return stored response if similarity high."""
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, dataset_embeddings)[0]
    top_idx = cos_scores.argmax().item()
    top_score = cos_scores[top_idx].item()

    if top_score >= threshold:
        return dataset[top_idx]["output"], top_score
    return None, top_score


def is_complex_query(query):
    """PRD §4 Tier 3: Detect queries needing RAG (policy/knowledge docs)."""
    complex_keywords = [
        "policy", "breakdown", "schedule", "penalty", "detailed",
        "clause", "terms", "grievance", "ombudsman", "redressal",
        "billing cycle", "late payment", "cash withdrawal", "digital",
        "limit", "cooling period",
    ]
    return any(kw in query.lower() for kw in complex_keywords)


# ── UI ───────────────────────────────────────────────────────────────────────
st.title("🏦 BFSI Call Center Assistant")
st.caption("Secure • Compliant • Local — All processing happens on your machine.")
st.markdown("---")

# Sidebar with system info (PRD §6: maintainability)
with st.sidebar:
    st.header("📋 System Info")
    st.markdown(f"**Dataset entries:** {len(dataset)}")
    st.markdown(f"**Response pipeline:**")
    st.markdown("1. 🎯 Dataset Match (Tier 1)")
    st.markdown("2. 📚 RAG Retrieval (Tier 3)")
    st.markdown("3. 🤖 AI Fallback (Tier 2)")
    st.markdown("---")
    st.markdown("**Supported Topics:**")
    st.markdown("• Loans, EMI, Interest Rates")
    st.markdown("• Cards, Transactions")
    st.markdown("• Insurance, FD/RD")
    st.markdown("• Account, KYC, Complaints")
    st.markdown("---")
    st.caption("⚠️ All responses are for guidance only.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()

        # ── PRD §4: Response Logic ──────────────────────────────────────
        # Tier 1: Dataset Match
        match_response, score = get_best_match(prompt)

        if match_response:
            response = f"{match_response}\n\n*(Source: Dataset, Confidence: {score:.2f})*"

        # Tier 3: Complex query → RAG + SLM
        elif is_complex_query(prompt):
            response_placeholder.markdown("🔍 Searching knowledge base...")
            contexts = rag.retrieve(prompt)
            if contexts:
                context_str = "\n".join(contexts)
                augmented_prompt = (
                    f"Context: {context_str}\n\n"
                    f"User Question: {prompt}\nAnswer based on context:"
                )
                response = slm.generate_response(augmented_prompt)
                response += "\n\n*(Source: RAG + Knowledge Base)*"
            else:
                response = slm.generate_response(prompt)
                response += "\n\n*(Source: AI Assistant)*"

        # Tier 2: Fallback to SLM
        else:
            response_placeholder.markdown("💬 Generating response...")
            response = slm.generate_response(prompt)
            response += "\n\n*(Source: AI Assistant)*"

        response_placeholder.markdown(response)
        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )
