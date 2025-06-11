# chat_model_wrapper.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)

class ChatRefiner:
    def __init__(self, model_name="gemini-1.5-flash"):
        """
        Initializes the Gemini Pro chat model.
        """
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment or .env file.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def refine(self, context: str, answer: str) -> str:
        """
        Uses Gemini to improve and clarify the answer text.

        Args:
            context: The user’s question or prompt.
            answer: The original system-generated answer.

        Returns:
            A refined answer as a string.
        """
        prompt = f"""
        You are a helpful assistant. Given the user's question and the system answer,
        rewrite the answer to be more natural, friendly, and informative without changing the meaning.

        Question: {context}
        Answer: {answer}

        Improved Answer:
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[GeminiRefiner] Error: {e}")
            return answer  # fallback to raw answer
