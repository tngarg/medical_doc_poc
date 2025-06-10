import os
import shutil
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings # Corrected import
import pickle

class VectorStoreManager:
    def __init__(self, persist_folder: str = "data", index_name: str = "vector_index", embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.persist_folder = persist_folder
        self.index_name = index_name
        self.embedding_model_name = embedding_model_name
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
        self.vector_store = None
        # Ensure the persist_folder exists when the manager is initialized,
        # as FAISS.load_local expects the folder_path to exist.
        if not os.path.exists(self.persist_folder):
            os.makedirs(self.persist_folder, exist_ok=True)
        print(f"VectorStoreManager initialized. Index will be saved in folder '{self.persist_folder}' with base name '{self.index_name}'. Embedding model: '{self.embedding_model_name}'")

    def create_or_load_store(self, documents: list = None, force_recreate: bool = False):
        faiss_file_path = os.path.join(self.persist_folder, f"{self.index_name}.faiss")
        pkl_file_path = os.path.join(self.persist_folder, f"{self.index_name}.pkl")

        if force_recreate:
            if os.path.exists(faiss_file_path):
                print(f"Force recreating store. Deleting existing FAISS file: {faiss_file_path}")
                os.remove(faiss_file_path)
            if os.path.exists(pkl_file_path):
                print(f"Force recreating store. Deleting existing PKL file: {pkl_file_path}")
                os.remove(pkl_file_path)

        if os.path.exists(faiss_file_path) and not force_recreate: # Check for .faiss file primarily
            print(f"Loading existing vector store. Base name: '{self.index_name}', Folder: '{self.persist_folder}'")
            try:
                self.vector_store = FAISS.load_local(
                    folder_path=self.persist_folder,
                    embeddings=self.embeddings,
                    index_name=self.index_name,
                    allow_dangerous_deserialization=True
                )
                print("Vector store loaded successfully.")
            except Exception as e:
                print(f"Error loading vector store: {e}. Will attempt to recreate if documents are provided.")
                if documents is None:
                    print("Error: Cannot recreate store without documents. Please provide documents.")
                    return None
                self.vector_store = self._create_new_store(documents)
        elif documents is not None:
            self.vector_store = self._create_new_store(documents)
        else:
            print(f"Error: No documents provided and no existing vector store (e.g. {faiss_file_path}) found to load.")
            return None

        return self.vector_store

    def _create_new_store(self, documents: list):
        if not documents:
            print("Error: Cannot create vector store without documents.")
            return None
        print(f"Creating new vector store with {len(documents)} documents/chunks...")
        try:
            if not all(hasattr(doc, 'page_content') and hasattr(doc, 'metadata') for doc in documents):
                print("Error: Documents list contains items not of type Langchain Document.")
                return None

            self.vector_store = FAISS.from_documents(documents, self.embeddings)

            # Ensure persist_folder exists before saving (should be by __init__ or if user changed it)
            if not os.path.exists(self.persist_folder):
                os.makedirs(self.persist_folder, exist_ok=True)

            self.vector_store.save_local(folder_path=self.persist_folder, index_name=self.index_name)
            print(f"New vector store created and saved. Base name: '{self.index_name}', Folder: '{self.persist_folder}'")
        except Exception as e:
            print(f"Failed to create and save vector store: {e}")
            self.vector_store = None
        return self.vector_store

    def add_documents(self, documents: list):
        if not self.vector_store:
            print("Error: Vector store not initialized. Call create_or_load_store() first or provide documents to create a new one.")
            if documents:
                print("Attempting to create a new store with the provided documents...")
                self.create_or_load_store(documents)
                if self.vector_store:
                     print("New store created. Documents added implicitly.")
                else:
                    print("Failed to create a new store. Documents not added.")
            return

        if documents:
            print(f"Adding {len(documents)} new documents to the existing vector store...")
            self.vector_store.add_documents(documents)
            self.vector_store.save_local(folder_path=self.persist_folder, index_name=self.index_name)
            print("Documents added and store updated.")
        else:
            print("No documents provided to add.")

    def similarity_search(self, query: str, k: int = 5):
        if not self.vector_store:
            print("Error: Vector store not initialized. Cannot perform search.")
            return []

        print(f"Performing similarity search for query: '{query}' with k={k}")
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            print(f"Found {len(results)} results.")
            return results
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return []

if __name__ == "__main__":
    class MockDocument: # Renamed to avoid conflict if Document class is imported
        def __init__(self, page_content, metadata=None):
            self.page_content = page_content
            self.metadata = metadata if metadata is not None else {}

    # Removed MockDocumentLoader as it's not strictly needed for this test script's new focus
    # The main test is that the class can be initialized and methods called.

    print("Running VectorStoreManager example...")
    # Test with default persist_folder='data' and index_name='vector_index'
    # These will be created in the root of the medical-qa-poc project if running script from there.
    # For isolated testing, a dedicated test output folder is better.
    test_output_folder = "test_vs_manager_output"
    default_persist_folder = os.path.join(test_output_folder, "data")
    default_index_name = "vector_index"

    if os.path.exists(test_output_folder): # Clean up entire test output folder
        shutil.rmtree(test_output_folder)
    os.makedirs(default_persist_folder, exist_ok=True) # Ensure data subdir is made

    print(f"Test FAISS index will be in: {default_persist_folder}, with name: {default_index_name}")

    # Create some mock documents for testing
    mock_docs = [
        MockDocument(page_content="Apples are a type of fruit, rich in vitamins.", metadata={"source": "doc1.txt"}),
        MockDocument(page_content="Oranges are citrus fruits, known for Vitamin C.", metadata={"source": "doc1.txt"}),
        MockDocument(page_content="Python is a versatile programming language.", metadata={"source": "doc2.txt"}),
        MockDocument(page_content="Langchain provides tools for building LLM applications.", metadata={"source": "doc2.txt"})
    ]

    vs_manager = VectorStoreManager(persist_folder=default_persist_folder, index_name=default_index_name)

    print("\nAttempting to create a new vector store (force_recreate=True)...")
    vs_manager.create_or_load_store(documents=mock_docs, force_recreate=True)

    if vs_manager.vector_store:
        print("Vector store created/loaded successfully.")
        print("\nPerforming similarity search for 'fruits'...")
        search_results = vs_manager.similarity_search(query="fruits", k=2)
        if search_results:
            for doc, score in search_results:
                print(f"Found: {doc.page_content[:60]}... (Score: {score:.4f}) (Source: {doc.metadata.get('source')})")

        print("\nTesting loading from persisted store...")
        vs_manager_load_test = VectorStoreManager(persist_folder=default_persist_folder, index_name=default_index_name)
        vs_manager_load_test.create_or_load_store() # No documents, should load from disk
        if vs_manager_load_test.vector_store:
            print("Successfully loaded store from disk.")
            search_results_load = vs_manager_load_test.similarity_search(query="Python programming", k=1)
            if search_results_load:
                for doc, score in search_results_load:
                    print(f"Search on loaded store: {doc.page_content[:60]}... (Score: {score:.4f})")
        else:
            print("Failed to load store from disk in test.")
    else:
        print("Failed to create or load vector store in the test.")

    print("\nCleaning up test data and directories...")
    if os.path.exists(test_output_folder):
        shutil.rmtree(test_output_folder)

    print("VectorStoreManager example finished.")
