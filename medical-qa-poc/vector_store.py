# vector_store.py

import os
# OLD (Deprecated)
# from langchain.vectorstores import FAISS
# from langchain.embeddings import HuggingFaceEmbeddings

# NEW (Recommended)

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings


class VectorStoreManager:
    def __init__(self, persist_directory: str = "data/vector_store"):
        self.persist_directory = persist_directory
        self.vector_store = None
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print(f"✅ VectorStoreManager initialized. Directory: {self.persist_directory}")

    def build_and_save_vector_store(self, documents: list):
        if not documents:
            raise ValueError("No documents provided for vector store creation.")
        
        print(f"🔄 Building FAISS index from {len(documents)} chunks...")
        self.vector_store = FAISS.from_documents(documents, self.embedding_model)
        self.vector_store.save_local(self.persist_directory)
        print(f"✅ FAISS index saved to {self.persist_directory}")

    def load_vector_store(self):
        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError(f"Vector store not found at {self.persist_directory}")
        
        print(f"📥 Loading FAISS index from {self.persist_directory}")
        self.vector_store = FAISS.load_local(
            folder_path=self.persist_directory,
            embeddings=self.embedding_model,
            allow_dangerous_deserialization=True  # ← Add this line
        )
        print("✅ Vector store loaded successfully.")
        return self.vector_store



    def similarity_search(self, query: str, k: int = 3):
        if not self.vector_store:
            raise RuntimeError("Vector store not loaded. Call load_vector_store() first.")
        
        print(f"🔍 Performing similarity search for: '{query}'")
        return self.vector_store.similarity_search_with_score(query, k=k)
