import random
from chat_model_wrapper import ChatRefiner

class FallbackHandler:
    """
    Handles fallback by reframing the query and using Gemini (LLM) to generate an answer.
    """
    def __init__(self, status_callback=None, default_message="I'm sorry, I couldn't find a definitive answer to your question at this time."):
        self.default_message = default_message
        self.canned_responses = [
            "I'm unable to answer that question with the current information available.",
            "That's a bit outside my current knowledge. Could you try rephrasing or asking something else?",
            "I don't have enough information to provide a confident answer for that.",
            "Unfortunately, I can't assist with that specific query right now.",
        ]
        self.chat_refiner = ChatRefiner()
        self.status_callback = status_callback or (lambda msg: None)
        print("FallbackHandler initialized (Gemini only).")

    def get_fallback_response(self, question: str, context: dict = None) -> dict:
        # Step 1: Reframe the question for clarity
        self.status_callback("Rephrasing your query for better understanding...")
        try:
            reframed_question = self.chat_refiner.reframe(question)
        except Exception as e:
            print(f"Error during reframing: {e}")
            reframed_question = question

        print(f"Reframed question: {reframed_question}")

        # Step 2: Use Gemini (ChatRefiner) to answer directly
        self.status_callback("Using Gemini to generate an answer...")
        try:
            gemini_response = self.chat_refiner.answer(reframed_question)
            if gemini_response:
                return {
                    "answer": gemini_response,
                    "confidence": 0.2,
                    "source": "Fallback - Gemini",
                    "original_question": question,
                    "agent_name": "FallbackHandler",
                    "reframed": reframed_question
                }
        except Exception as e:
            print(f"Error using Gemini: {e}")

        # Step 3: Provide a polite fallback message
        self.status_callback("No results found. Showing fallback message.")
        chosen_message = random.choice(self.canned_responses + [self.default_message])
        return {
            "answer": (
                f"{chosen_message}\n\n"
                f"_Note: We attempted to reframe your question and used fallback mechanism, "
                f"but could not find a reliable answer._"
            ),
            "confidence": 0.01,
            "source": "System/Fallback",
            "original_question": question,
            "agent_name": "FallbackHandler",
            "reframed": reframed_question
        }
