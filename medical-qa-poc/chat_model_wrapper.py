# chat_model_wrapper.py

from transformers.pipelines import pipeline

class ChatRefiner:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.2"):
        # Load a lightweight summarization or response refinement model
        # You may switch to any Hugging Face model available for deployment
        self.generator = pipeline("text2text-generation", model=model_name)

    def refine(self, context: str, answer: str) -> str:
        """
        Refines the agent-generated answer before it's shown to the user.

        Args:
            context: The user question or conversation context
            answer: The raw answer returned by the MCP system

        Returns:
            A refined, more conversational and concise response
        """
        prompt = f"""
        You are a helpful assistant. Given the user's question and the system answer,
        rewrite the answer to be more natural, friendly, and informative without changing the meaning.

        Question: {context}
        Answer: {answer}

        Improved Answer:
        """

        response = self.generator(prompt, max_new_tokens=150, do_sample=False)
        print(response)
        return response