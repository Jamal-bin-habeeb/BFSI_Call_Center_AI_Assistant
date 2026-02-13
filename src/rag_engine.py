"""
Lightweight RAG Engine using numpy + sentence-transformers.

Replaces ChromaDB (broken on Python 3.14) with a simple pickle-based
vector store that has zero pydantic dependency.
"""

import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer


class RAGEngine:
    def __init__(self, data_dir="data", db_path="vector_store.pkl"):
        self.data_dir = data_dir
        self.db_path = db_path
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.chunks = []
        self.embeddings = None

    # ── Document Loading ────────────────────────────────────────────────
    def _load_text_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_pdf_file(self, file_path):
        try:
            from pypdf import PdfReader

            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except ImportError:
            print("pypdf not installed — skipping PDF files.")
            return ""

    def load_documents(self):
        """Load all .txt and .pdf files from data_dir."""
        all_text = []
        if not os.path.exists(self.data_dir):
            print(f"Data directory '{self.data_dir}' not found.")
            return all_text

        for filename in os.listdir(self.data_dir):
            file_path = os.path.join(self.data_dir, filename)
            try:
                if filename.endswith(".txt"):
                    text = self._load_text_file(file_path)
                    if text.strip():
                        all_text.append(text)
                        print(f"  Loaded: {filename}")
                elif filename.endswith(".pdf"):
                    text = self._load_pdf_file(file_path)
                    if text.strip():
                        all_text.append(text)
                        print(f"  Loaded: {filename}")
            except Exception as e:
                print(f"  Error loading {filename}: {e}")

        return all_text

    # ── Chunking ────────────────────────────────────────────────────────
    @staticmethod
    def _split_text(text, chunk_size=400, overlap=80):
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    # ── Vector Store ────────────────────────────────────────────────────
    def create_vector_store(self):
        """Build embeddings from documents and save to disk."""
        print("Loading documents...")
        documents = self.load_documents()
        if not documents:
            print("No documents found. Vector store not created.")
            return

        # Split into chunks
        self.chunks = []
        for doc in documents:
            self.chunks.extend(self._split_text(doc))

        print(f"Splitting into {len(self.chunks)} chunks...")
        print("Creating embeddings (this may take a moment)...")
        self.embeddings = self.embedder.encode(self.chunks, convert_to_numpy=True)

        # Save to disk
        with open(self.db_path, "wb") as f:
            pickle.dump({"chunks": self.chunks, "embeddings": self.embeddings}, f)
        print(f"Vector store saved to {self.db_path}")

    def load_vector_store(self):
        """Load existing vector store, or create one if missing."""
        if os.path.exists(self.db_path):
            with open(self.db_path, "rb") as f:
                data = pickle.load(f)
            self.chunks = data["chunks"]
            self.embeddings = data["embeddings"]
            print(f"Loaded vector store ({len(self.chunks)} chunks).")
        else:
            print("No vector store found — creating one...")
            self.create_vector_store()

    # ── Retrieval ───────────────────────────────────────────────────────
    def retrieve(self, query, k=2):
        """Find the k most relevant chunks for a query."""
        if self.embeddings is None or len(self.chunks) == 0:
            self.load_vector_store()

        if self.embeddings is None or len(self.chunks) == 0:
            return []

        query_emb = self.embedder.encode([query], convert_to_numpy=True)

        # Cosine similarity
        scores = np.dot(self.embeddings, query_emb.T).flatten()
        norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_emb)
        scores = scores / (norms + 1e-10)

        top_indices = scores.argsort()[-k:][::-1]
        return [self.chunks[i] for i in top_indices if scores[i] > 0.2]


if __name__ == "__main__":
    rag = RAGEngine()
    rag.create_vector_store()

    print("\nTesting Retrieval:")
    results = rag.retrieve("What is the interest rate for a home loan?")
    for i, r in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(r)
