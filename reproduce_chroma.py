from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
import os
import shutil

# Clean up
if os.path.exists("chroma_db_test"):
    shutil.rmtree("chroma_db_test")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

docs = [Document(page_content="This is a test document.", metadata={"source": "test"})]

print("Attempting to create vector store...")
try:
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory="chroma_db_test"
    )
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
