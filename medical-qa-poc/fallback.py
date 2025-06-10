import random

class FallbackHandler:
    """
    Handles situations where no agent can confidently answer a question.
    """
    def __init__(self, default_message: str = "I'm sorry, I couldn't find a definitive answer to your question at this time."):
        """
        Initializes the FallbackHandler.

        Args:
            default_message (str): The default message to return when no specific fallback logic applies.
        """
        self.default_message = default_message
        self.canned_responses = [
            "I'm unable to answer that question with the current information available.",
            "That's a bit outside my current knowledge. Could you try rephrasing or asking something else?",
            "I don't have enough information to provide a confident answer for that.",
            "Unfortunately, I can't assist with that specific query right now.",
        ]
        print("FallbackHandler initialized.")

    def get_fallback_response(self, question: str, context: dict = None) -> dict:
        """
        Generates a fallback response.

        Args:
            question (str): The original question that could not be answered.
            context (dict, optional): Additional context, which might include:
                                      - "agent_responses" (list): List of responses from all tried agents.
                                      - "error_messages" (list): Specific errors encountered.
                                      - "user_history" (list): Previous interactions.

        Returns:
            dict: A dictionary containing the fallback answer, a very low confidence score,
                  and the source as "System/Fallback".
        """
        print(f"FallbackHandler processing for question: '{question}'")

        # Log the unanswered question (implementation of logging is external to this class)
        self._log_unanswered_question(question, context)

        # Basic strategy: return a random canned response or the default one.
        # More advanced strategies could analyze the context.
        if context and context.get("agent_responses"):
            # Check if any agent gave a partial answer or a specific reason for failure
            # For now, we just use a generic message.
            pass # Future: analyze agent_responses for more tailored fallback

        chosen_message = random.choice(self.canned_responses + [self.default_message])

        return {
            "answer": chosen_message,
            "confidence": 0.01,  # Very low confidence for fallback
            "source": "System/Fallback",
            "original_question": question,
            "agent_name": "FallbackHandler"
        }

    def _log_unanswered_question(self, question: str, context: dict = None):
        """
        Placeholder for logging unanswered questions.
        In a real application, this would write to a file, database, or logging service.
        """
        log_message = f"UNANSWERED_QUESTION: \"{question}\""
        if context:
            if context.get("agent_responses"):
                log_message += f" | AgentResponses: {len(context['agent_responses'])}"
            if context.get("error_messages"):
                 log_message += f" | Errors: {context['error_messages']}"
        # In a real system, use a logger:
        # import logging
        # logging.info(log_message)
        print(f"LOG (Fallback): {log_message}")


# --- Example Usage (for testing) ---
if __name__ == "__main__":
    print("Running FallbackHandler example...")

    fallback_handler = FallbackHandler()

    test_question = "What is the meaning of life in the context of advanced medical AI?"

    # Simulate context from an orchestrator
    example_context = {
        "agent_responses": [
            {"answer": "Agent1 uncertain.", "confidence": 0.3, "source": "Agent1"},
            {"answer": "Agent2 found nothing.", "confidence": 0.1, "source": "Agent2"},
        ],
        "error_messages": [],
        "user_history": ["User asked: How are you?", "Bot said: I am an AI."]
    }

    response1 = fallback_handler.get_fallback_response(test_question)
    print(f"\nFallback response (no context):\n{response1}")

    response2 = fallback_handler.get_fallback_response(test_question, context=example_context)
    print(f"\nFallback response (with context):\n{response2}")

    # Test with a different default message
    custom_fallback = FallbackHandler(default_message="Apologies, your query could not be processed by our medical information system.")
    response3 = custom_fallback.get_fallback_response("Tell me about drug X for condition Y.")
    print(f"\nFallback response (custom default):\n{response3}")

    print("\nFallbackHandler example finished.")
