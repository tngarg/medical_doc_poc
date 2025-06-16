# generate_vector_store.py

# ✅ Environment Setup
import os
from dotenv import load_dotenv
load_dotenv(override=True)

# Environment variables
DATA_PATH = os.getenv("DATA_PATH", "OneDrive_2025-06-12/LLM Collatoral")
PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY", "data/vector_store")
KG_FILE_PATH = os.getenv("KG_FILE_PATH", "data/medical_kg.gml")

# ✅ Load and Split Documents
from document_loader import DocumentLoader

print(f"\n📂 Loading documents from: {DATA_PATH}")
doc_loader = DocumentLoader(data_path=DATA_PATH)
documents = doc_loader.load_and_split_documents()

if not documents:
    raise RuntimeError("❌ No documents found. Please check DATA_PATH or file formats.")

print(f"✅ Loaded and split {len(documents)} chunks.\n")

# ✅ Create Vector Store
from vector_store import VectorStoreManager

print(f"💾 Saving vector store to: {PERSIST_DIRECTORY}")
vector_store_manager = VectorStoreManager(persist_directory=PERSIST_DIRECTORY)
vector_store_manager.build_and_save_vector_store(documents)

# ✅ Reload Vector Store for Validation
print(f"\n📥 Reloading vector store from: {PERSIST_DIRECTORY}")
vector_store_manager.load_vector_store()

# ✅ Run a Sample Query for Validation
sample_query = "What are the side effects of aspirin?"
print(f"\n🔎 Running test query: \"{sample_query}\"")
results = vector_store_manager.similarity_search(sample_query, k=2)

if results:
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n🔹 Match {i}")
        print(f"→ Score: {score:.2f}")
        print(f"📄 Source: {doc.metadata.get('source', 'unknown')}")
        print(f"📝 Snippet: {doc.page_content[:300]}...")
else:
    print("⚠️ No matches found in vector store.")
