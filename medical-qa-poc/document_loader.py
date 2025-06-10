import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader # Corrected imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
import shutil # For cleaning up test directory

LOADER_MAPPING = {
    ".txt": (TextLoader, {"encoding": "utf8"}),
    ".pdf": (PyPDFLoader, {}), # PyPDFLoader uses pypdf by default
}

class DocumentLoader:
    def __init__(self, data_path: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        # Allow data_path to be non-existent if it's the specific test_data_loader path for __main__
        # This logic is mainly for the __main__ example block.
        if not (__name__ == "__main__" and data_path.endswith("test_data_loader")) and not os.path.isdir(data_path):
            raise ValueError(f"Data path '{data_path}' is not a valid directory or does not exist.")

        self.data_path = data_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            add_start_index=True, # Adds start index to metadata, useful for tracking
        )
        print(f"DocumentLoader initialized for path: {self.data_path}")

    def load_single_document(self, file_path: str):
        ext = "." + file_path.rsplit(".", 1)[-1].lower()
        if ext in LOADER_MAPPING:
            loader_class, loader_args = LOADER_MAPPING[ext]
            try:
                # For PyPDFLoader, file_path is passed directly.
                # For TextLoader, file_path is also passed directly.
                loader = loader_class(file_path, **loader_args)
                print(f"Loading document: {file_path} using {loader_class.__name__}")
                return loader.load() # Returns a list of Document objects (pages for PDF)
            except Exception as e:
                print(f"Error loading document {file_path} with {loader_class.__name__}: {e}")
                return None
        else:
            print(f"Warning: No loader found for extension '{ext}' in file {file_path}. Skipping.")
            return None

    def load_documents(self):
        all_pages_or_docs = []
        # Create data_path if it is for __main__ and does not exist
        if __name__ == "__main__" and self.data_path.endswith("test_data_loader") and not os.path.exists(self.data_path):
            os.makedirs(self.data_path, exist_ok=True)
            print(f"Created test directory: {self.data_path}")
            # Create dummy files for testing if in __main__
            self._create_dummy_files_for_testing()


        if not os.path.exists(self.data_path):
            print(f"Error: Data directory '{self.data_path}' not found.")
            return all_pages_or_docs

        for filename in os.listdir(self.data_path):
            file_path = os.path.join(self.data_path, filename)
            if os.path.isfile(file_path):
                ext = "." + filename.rsplit(".", 1)[-1].lower()
                if ext not in LOADER_MAPPING:
                    print(f"Skipping file {filename} with unsupported extension '{ext}'.")
                    continue

                loaded_content = self.load_single_document(file_path) # list of Document objects
                if loaded_content:
                    all_pages_or_docs.extend(loaded_content)
            else:
                print(f"Skipping non-file item: {file_path}")

        if not all_pages_or_docs:
            print(f"No documents were loaded from {self.data_path}. Check path and supported file types.")
            return []

        print(f"Loaded {len(all_pages_or_docs)} pages/documents from {self.data_path}")
        return all_pages_or_docs

    def split_documents(self, documents: list):
        if not documents:
            print("No documents/pages to split.")
            return []

        print(f"Splitting {len(documents)} document pages/items into chunks of size {self.chunk_size} with overlap {self.chunk_overlap}...")
        split_docs = self.text_splitter.split_documents(documents)
        print(f"Finished splitting. Original items: {len(documents)}, Total chunks: {len(split_docs)}")
        return split_docs

    def load_and_split_documents(self):
        raw_pages_or_docs = self.load_documents()
        if not raw_pages_or_docs:
            return []

        chunked_documents = self.split_documents(raw_pages_or_docs)
        return chunked_documents

    def _create_dummy_files_for_testing(self):
        # This method is intended to be called only from __main__ when using test_data_loader
        if not (self.data_path.endswith("test_data_loader")):
            return

        print(f"Creating dummy files in {self.data_path} for testing...")
        try:
            # Dummy Text File
            with open(os.path.join(self.data_path, "sample.txt"), "w") as f:
                f.write("This is a sample text document for testing the document loader. " * 50)

            # Dummy PDF File
            from pypdf import PdfWriter # pypdf is a dependency of PyPDFLoader
            pdf = PdfWriter()
            pdf.add_blank_page(width=8.5 * 72, height=11 * 72) # Standard letter size page
            pdf.add_blank_page(width=8.5 * 72, height=11 * 72) # Add a second page
            with open(os.path.join(self.data_path, "sample.pdf"), "wb") as f_pdf:
               pdf.write(f_pdf)
            print(f"Created dummy files: sample.txt, sample.pdf in {self.data_path}")
        except ImportError:
            print("pypdf not installed, skipping dummy PDF creation for test. Install with: pip install pypdf")
        except Exception as e:
            print(f"Error creating dummy files for test: {e}")


if __name__ == "__main__":
    test_data_dir = "test_data_loader" # A dedicated directory for this script's test

    # DocumentLoader will create this directory and dummy files if it doesn't exist
    # when called from __main__ with this specific path.

    print("\nRunning DocumentLoader example...")
    # data_path will be created by DocumentLoader's load_documents if it's test_data_dir
    doc_loader = DocumentLoader(data_path=test_data_dir)

    processed_documents = doc_loader.load_and_split_documents()

    if processed_documents:
        print(f"\nSuccessfully loaded and processed {len(processed_documents)} document chunks from '{test_data_dir}'.")
        if len(processed_documents) > 0:
             print(f"First document chunk metadata: {processed_documents[0].metadata}")
             print(f"First document chunk content sample: {processed_documents[0].page_content[:100]}...")
    else:
        print(f"\nNo documents were processed from '{test_data_dir}'.")

    print("\nCleaning up test data directory...")
    if os.path.exists(test_data_dir):
        try:
            shutil.rmtree(test_data_dir)
            print(f"Removed test directory: {test_data_dir}")
        except OSError as e:
            print(f"Error removing test directory {test_data_dir}: {e}")

    print("DocumentLoader example finished.")
