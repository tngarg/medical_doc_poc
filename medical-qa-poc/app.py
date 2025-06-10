import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import other modules from the project
# import document_loader
# import vector_store
# import knowledge_graph
# import agents
# import fallback
# import mcp

app = Flask(__name__)

# --- Configuration ---
# Example: Accessing an environment variable
# api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
# if not api_key:
#     print("Warning: HUGGINGFACEHUB_API_TOKEN not set.")

# --- Initialization of components ---
# Example:
# doc_loader = document_loader.DocumentLoader(data_path=os.getenv("DATA_PATH"))
# vec_store = vector_store.VectorStore(persist_directory=os.getenv("PERSIST_DIRECTORY"))
# knowledge_g = knowledge_graph.KnowledgeGraph(kg_file_path=os.getenv("KG_FILE_PATH"))
# qa_orchestrator = mcp.MasterControlProgram() # This will internally initialize agents and fallback

@app.route('/')
def home():
    return "Medical QA PoC is running!"

@app.route('/ask', methods=['POST'])
def ask_question():
    """
    Endpoint to receive a question and return an answer.
    Expected JSON payload: {"question": "your question here"}
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "Missing 'question' in request payload"}), 400

    # --- Core QA Logic (to be implemented) ---
    # answer = qa_orchestrator.handle_question(question)
    # For now, returning a dummy answer
    answer = f"The answer to '{question}' is being processed."
    confidence = 0.0
    source = "N/A"
    # --- End Core QA Logic ---

    return jsonify({
        "question": question,
        "answer": answer,
        "confidence": confidence,
        "source": source
    })

# --- More Endpoints (e.g., for document upload, status check) ---
# @app.route('/upload_document', methods=['POST'])
# def upload_document():
#     # ... document upload logic ...
#     pass

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, port=port, host='0.0.0.0')
