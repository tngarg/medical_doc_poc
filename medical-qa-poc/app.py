import gradio as gr
from agents import SimpleVectorStoreAgent, KnowledgeGraphAgent
from vector_store import VectorStoreManager
from knowledge_graph import KnowledgeGraphManager
from fallback import FallbackHandler
from mcp import MasterControlProgram
import os
from dotenv import load_dotenv


load_dotenv(override=True)

DATA_PATH = os.getenv("DATA_PATH", "./OneDrive_1_10-06-2025")
PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY", "./vector_store_db")
KG_FILE_PATH = os.getenv("KG_FILE_PATH", "./data/medical_kg.gml")

# Initialize backend
vector_store_manager = VectorStoreManager(PERSIST_DIRECTORY)
vector_store_manager.load_vector_store()
kg_manager = KnowledgeGraphManager(kg_file_path=KG_FILE_PATH)
vs_agent = SimpleVectorStoreAgent(name="VectorStoreAgent", vector_store_manager=vector_store_manager)
kg_agent = KnowledgeGraphAgent(name="KnowledgeGraphAgent", kg_manager=kg_manager)
fallback_handler = FallbackHandler()
mcp = MasterControlProgram(agents=[vs_agent, kg_agent], fallback_handler=fallback_handler, confidence_threshold=0.5)

# Sample questions
sample_questions = [
    "What are the side effects of aspirin?",
    "How is duplex ultrasound used in vascular diagnosis?",
    "Describe the use of Doppler in graft stenosis.",
    "Aspirin",
    "What does Aspirin treats?",
    "What vein is used for fistula?",
    "What is the meaning of life?",
    "Can AI dream?",
    "Tell me about unicorn medicine."
]

# Core logic
def respond(message, chat_history):
    if not message.strip():
        return "", chat_history, chat_history

    result = mcp.handle_question(message)
    answer = result.get("answer", "No answer returned.")
    confidence = result.get("confidence", 0.0)
    source = result.get("source", "Unknown")

    formatted = f"{answer}\n\n_Source: {source} | Confidence: {confidence:.2f}_"
    chat_history.append((message, formatted))
    return "", chat_history, chat_history

# UI layout
with gr.Blocks(css="""
body { background-color: #f8f8fc; margin: 0; }
.gradio-container { font-family: 'Segoe UI', sans-serif; height: 100vh; display: flex; flex-direction: column; }
.sample-btn button { background: #e3f2fd; border: none; margin-bottom: 5px; border-radius: 6px; cursor: pointer; }
#chatbot { height: 75vh; overflow-y: auto; background: white; border-radius: 8px; padding: 10px; border: 1px solid #ddd; }
#submit_button { background-color: #92b4ec !important; }
""") as demo:
    gr.Markdown("## 🩺 Medical QA Chat", elem_id="header")

    with gr.Row():
        with gr.Column(scale=1, min_width=250):
            gr.Markdown("### 💬 Sample Questions")
            question_input = gr.Textbox(visible=False)
            chat_state = gr.State([])  # Persist chat history

            for q in sample_questions:
                sample_btn = gr.Button(q, elem_classes=["sample-btn"])
                sample_btn.click(fn=lambda x=q: x, inputs=[], outputs=question_input)

        with gr.Column(scale=4):
            chatbot = gr.Chatbot(label="Chat", elem_id="chatbot")
            with gr.Row():
                user_input = gr.Textbox(
                    show_label=False,
                    placeholder="Ask a medical question...",
                    lines=2,
                    scale=4
                )
                submit = gr.Button("Submit", elem_id="submit_button", scale=1)

    # Connect input to response handler
    submit.click(fn=respond, inputs=[user_input, chat_state], outputs=[user_input, chat_state, chatbot])
    user_input.submit(fn=respond, inputs=[user_input, chat_state], outputs=[user_input, chat_state, chatbot])
    question_input.change(fn=respond, inputs=[question_input, chat_state], outputs=[question_input, chat_state, chatbot])

if __name__ == "__main__":
    demo.launch(debug=True)
