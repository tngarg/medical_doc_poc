import gradio as gr
from agents import SimpleVectorStoreAgent, KnowledgeGraphAgent
from vector_store import VectorStoreManager
from knowledge_graph import KnowledgeGraphManager
from fallback import FallbackHandler
from mcp import MasterControlProgram
from chat_model_wrapper import ChatRefiner
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# --- Configuration ---
DATA_PATH = os.getenv("DATA_PATH", "./OneDrive_1_10-06-2025")
PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY", "./vector_store_db")
KG_FILE_PATH = os.getenv("KG_FILE_PATH", "./data/medical_kg.gml")

# --- Initialize Components ---
vector_store_manager = VectorStoreManager(PERSIST_DIRECTORY)
vector_store_manager.load_vector_store()

kg_manager = KnowledgeGraphManager(kg_file_path=KG_FILE_PATH)

vs_agent = SimpleVectorStoreAgent(name="VectorStoreAgent", vector_store_manager=vector_store_manager)
kg_agent = KnowledgeGraphAgent(name="KnowledgeGraphAgent", kg_manager=kg_manager)

# Dummy placeholder fallback to satisfy MCP init
class DummyFallbackHandler:
    def get_fallback_response(self, question, context=None):
        return {
            "answer": "Temporary fallback.",
            "confidence": 0.0,
            "source": "Dummy",
            "agent_name": "Dummy"
        }

dummy_fallback = DummyFallbackHandler()

# Create MCP with dummy first
mcp = MasterControlProgram(agents=[vs_agent, kg_agent], fallback_handler=dummy_fallback, confidence_threshold=0.5)

# Real fallback using MCP reference
fallback_handler = FallbackHandler()
mcp.fallback_handler = fallback_handler

chat_refiner = ChatRefiner()

# --- Categorized Sample Questions ---
questions_by_type = {
    "📚 Embedding-based Questions": [
        "What protocol is followed for extracranial cerebrovascular duplex ultrasound?",
        "Which veins are evaluated in upper extremity mapping for dialysis access?",
        "How is hemodialysis access monitored post-surgery?"
    ],
    "🧬 Knowledge Graph Questions": [
        "What condition does Steal Phenomenon cause?",
        "Which measurement is used to assess stenosis severity?",
        "What artery is required for an arteriovenous fistula?"
    ],
    "🌀 Fallback Questions": [
        "How does unicorn plasma enhance dialysis?",
        "Can AI detect emotions in vascular reports?",
        "What is the spiritual impact of duplex imaging?"
    ]
}

# --- Response Logic ---
def respond(message, chat_history):
    if not message.strip():
        return "", chat_history, chat_history

    result = mcp.handle_question(message)
    raw_answer = result.get("answer", "No answer returned.")
    confidence = result.get("confidence", 0.0)
    source = result.get("source", "Unknown")
    agent_name = result.get("agent_name", "Unknown")
    reframed = result.get("reframed")

    refined_answer = chat_refiner.refine(message, raw_answer)

    agent_label_map = {
        "VectorStoreAgent": "Embedding-based QA",
        "KnowledgeGraphAgent": "Knowledge Graph",
        "FallbackHandler": "Fallback System"
    }
    agent_label = agent_label_map.get(agent_name, agent_name)

    reframed_note = f"\n_Reframed Query: {reframed}_" if reframed else ""
    formatted = f"{refined_answer}\n\n_Solved via: {agent_label} | Source: {source} | Confidence: {confidence:.2f}"
    chat_history.append((message, formatted))
    return "", chat_history, chat_history

# --- UI Layout ---
with gr.Blocks(css="""
body {
    background-color: #f8f8fc;
    margin: 0;
    overflow-y: auto;
}
.gradio-container {
    font-family: 'Segoe UI', sans-serif;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
.sample-btn button {
    background: #e3f2fd;
    border: none;
    margin-bottom: 5px;
    border-radius: 6px;
    cursor: pointer;
    text-align: left;
    padding: 6px 10px;
    font-size: 0.85em;
    font-weight: bold;
    white-space: normal;
    max-width: 100%;
    box-sizing: border-box;
}
#chatbot {
    height: 75vh;
    overflow-y: auto;
    background: white;
    border-radius: 8px;
    padding: 10px;
    border: 1px solid #ddd;
}
#submit_button { background-color: #92b4ec !important; border: none; }
#left-panel {
    border-right: 1px solid #eee;
    padding-right: 15px;
    overflow-y: auto;
    overflow-x: hidden;
}
.gradio-container h2 { color: #333; margin-bottom: 20px; }
.gradio-container h3 { color: #555; margin-top: 15px; margin-bottom: 10px; }
hr { border: 0; height: 1px; background: #eee; margin: 20px 0; }
""") as demo:

    gr.Markdown("## 🩺 Medical QA Chat", elem_id="header")

    with gr.Row():
        with gr.Column(scale=1, min_width=250, elem_id="left-panel"):
            question_input = gr.Textbox(visible=False)
            chat_state = gr.State([])

            for category, questions in questions_by_type.items():
                gr.Markdown(f"### {category}")
                with gr.Column():
                    for q in questions:
                        gr.Button(q, elem_classes=["sample-btn"]).click(
                            fn=lambda x=q: x,
                            inputs=[],
                            outputs=question_input
                        )
            gr.Markdown("---")

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

    submit.click(fn=respond, inputs=[user_input, chat_state], outputs=[user_input, chat_state, chatbot])
    user_input.submit(fn=respond, inputs=[user_input, chat_state], outputs=[user_input, chat_state, chatbot])
    question_input.change(fn=lambda x: x, inputs=[question_input], outputs=[user_input])

if __name__ == "__main__":
    demo.launch(debug=True)
