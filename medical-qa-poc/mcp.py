# from agents import BaseAgent, SimpleVectorStoreAgent, KnowledgeGraphAgent # Import actual agent classes
# from fallback import FallbackHandler
# from vector_store import VectorStoreManager # For initializing agents
# from knowledge_graph import KnowledgeGraphManager # For initializing agents

class MasterControlProgram:
    """
    Orchestrates the question-answering process by managing various agents
    and fallback mechanisms.
    """
    def __init__(self, agents: list, fallback_handler, confidence_threshold: float = 0.5):
        """
        Initializes the MasterControlProgram.

        Args:
            agents (list): A list of instantiated QA agent objects (derived from BaseAgent).
            fallback_handler (FallbackHandler): An instance of the FallbackHandler.
            confidence_threshold (float): Minimum confidence score for an answer to be considered acceptable.
        """
        self.agents = agents
        self.fallback_handler = fallback_handler
        self.confidence_threshold = confidence_threshold

        if not self.agents:
            raise ValueError("At least one agent must be provided to the MasterControlProgram.")
        if not self.fallback_handler:
            raise ValueError("A FallbackHandler must be provided.")
        
        print(f"MasterControlProgram initialized with {len(self.agents)} agents and confidence threshold: {self.confidence_threshold}")
        for agent in self.agents:
            print(f"  - Registered Agent: {agent.name}")

    def handle_question(self, question: str, context: dict = None) -> dict:
        """
        Handles an incoming question, routes it to agents, and returns the best answer.

        Args:
            question (str): The user's question.
            context (dict, optional): Additional context for the query (e.g., chat history).

        Returns:
            dict: The chosen answer response from an agent or the fallback handler.
        """
        print(f"\nMCP handling question: '{question}'")
        if not context:
            context = {}

        # --- Step 0: Manually route exact-match KG questions ---
        kg_routed_questions = {
            "What condition does Steal Phenomenon cause?": {
                "start_node": "Steal Phenomenon",
                "relationship": "associated_with",
                "target_type": "Symptom"
            },
            "Which measurement is used to assess stenosis severity?": {
                "start_node": "ICA/CCA Ratio",
                "relationship": "used_to_classify",
                "target_type": "Condition"
            },
            "What artery is required for an arteriovenous fistula?": {
                "start_node": "Arteriovenous Fistula",
                "relationship": "requires",
                "target_type": "Vessel"
            }
        }

        if question in kg_routed_questions:
            qmeta = kg_routed_questions[question]
            for agent in self.agents:
                if getattr(agent, "name", "") == "KnowledgeGraphAgent":
                    try:
                        result_nodes = agent.kg_manager.query_graph(
                            start_node=qmeta["start_node"],
                            relationship=qmeta["relationship"],
                            target_node_type=qmeta["target_type"]
                        )
                        answer = ", ".join(result_nodes) if result_nodes else "No related nodes found."
                        return {
                            "answer": answer,
                            "confidence": 0.95 if result_nodes else 0.3,
                            "source": "KG",
                            "agent_name": "KnowledgeGraphAgent"
                        }
                    except Exception as e:
                        return {
                            "answer": f"Error accessing knowledge graph: {e}",
                            "confidence": 0.0,
                            "source": "KG",
                            "agent_name": "KnowledgeGraphAgent"
                        }

        
        all_agent_responses = []

        # 1. Query all registered agents
        # (Could be made more sophisticated, e.g., sequenced, parallel, conditional routing)
        for agent in self.agents:
            try:
                print(f"  Querying agent: {agent.name}...")
                agent_response = agent.query(question, context=context.get("agent_specific_context", {}).get(agent.name))
                all_agent_responses.append(agent_response)
                print(f"  Agent {agent.name} responded. Confidence: {agent_response.get('confidence', 0.0)}")
            except Exception as e:
                print(f"  Error querying agent {agent.name}: {e}")
                all_agent_responses.append({
                    "answer": f"Error in {agent.name}.",
                    "confidence": 0.0,
                    "source": agent.name,
                    "error": str(e),
                    "agent_name": agent.name
                })
        
        context["agent_responses"] = all_agent_responses # For fallback handler

        # 2. Evaluate responses and select the best one
        best_response = None
        highest_confidence = -1.0 # Start with a value lower than any possible confidence

        for response in all_agent_responses:
            if response.get("error"): # Skip responses that are purely errors
                continue
            
            confidence = response.get("confidence", 0.0)
            if confidence > highest_confidence:
                highest_confidence = confidence
                best_response = response
        
        print(f"MCP evaluated responses. Highest confidence: {highest_confidence}")

        # 3. If no satisfactory answer, use fallback
        if best_response and highest_confidence >= self.confidence_threshold:
            print(f"MCP selected answer from {best_response.get('agent_name', 'Unknown Agent')} with confidence {highest_confidence}.")
            # Optionally, add a marker that this answer was chosen by MCP
            best_response["chosen_by_mcp"] = True
            return best_response
        else:
            print(f"MCP: No agent met confidence threshold ({self.confidence_threshold}). Using FallbackHandler.")
            if best_response: # Log the best attempt even if below threshold
                 print(f"  Best attempt was from {best_response.get('agent_name')} with confidence {highest_confidence}")
            
            fallback_context = {
                "agent_responses": all_agent_responses,
                "original_question": question,
                # "user_history": context.get("user_history") # if you track history
            }
            return self.fallback_handler.get_fallback_response(question, context=fallback_context)

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    # Mock classes for testing (assuming they are defined as in their respective files or here)
    class MockBaseAgent: # Simplified BaseAgent for this test
        def __init__(self, name="MockAgent"):
            self.name = name
        def query(self, question, context=None):
            raise NotImplementedError

    class MockGoodAgent(MockBaseAgent):
        def __init__(self, name="GoodAgent"):
            super().__init__(name)
        def query(self, question, context=None):
            if "health" in question.lower():
                return {"answer": "Health is important.", "confidence": 0.8, "source": self.name, "agent_name": self.name}
            return {"answer": "GoodAgent unsure.", "confidence": 0.4, "source": self.name, "agent_name": self.name}

    class MockOkAgent(MockBaseAgent):
        def __init__(self, name="OkAgent"):
            super().__init__(name)
        def query(self, question, context=None):
            if "medical" in question.lower():
                return {"answer": "Medical queries are complex.", "confidence": 0.6, "source": self.name, "agent_name": self.name}
            return {"answer": "OkAgent doesn't know.", "confidence": 0.2, "source": self.name, "agent_name": self.name}
    
    class MockErrorAgent(MockBaseAgent):
        def __init__(self, name="ErrorAgent"):
            super().__init__(name)
        def query(self, question, context=None):
            # This agent always raises an error
            raise ValueError("Simulated processing error in ErrorAgent")


    class MockFallbackHandler:
        def __init__(self):
            print("MockFallbackHandler initialized.")
        def get_fallback_response(self, question, context=None):
            return {"answer": f"Sorry, couldn't answer: '{question}'. Fallback.", "confidence": 0.01, "source": "Fallback", "agent_name": "FallbackHandler"}

    print("Running MasterControlProgram example...\n")

    # Initialize agents and fallback handler
    good_agent = MockGoodAgent()
    ok_agent = MockOkAgent()
    error_agent = MockErrorAgent()
    
    agents_list = [good_agent, ok_agent, error_agent]
    fallback_h = MockFallbackHandler()

    # Initialize MCP
    mcp_instance = MasterControlProgram(agents=agents_list, fallback_handler=fallback_h, confidence_threshold=0.7)

    # Test case 1: Good agent should answer
    question1 = "Tell me about health."
    response1 = mcp_instance.handle_question(question1)
    print(f"\nFinal Response for '{question1}':\n{response1}\n")
    assert response1["agent_name"] == "GoodAgent"

    # Test case 2: Ok agent answers, but below threshold, fallback should be used
    question2 = "Any medical advice?"
    response2 = mcp_instance.handle_question(question2)
    print(f"\nFinal Response for '{question2}':\n{response2}\n")
    assert response2["agent_name"] == "FallbackHandler"
    
    # Test case 3: No agent can answer confidently, fallback should be used
    question3 = "What is the weather like?"
    response3 = mcp_instance.handle_question(question3)
    print(f"\nFinal Response for '{question3}':\n{response3}\n")
    assert response3["agent_name"] == "FallbackHandler"

    # Test case 4: Change threshold so OkAgent's response is accepted
    print("--- Changing confidence threshold to 0.5 ---")
    mcp_instance.confidence_threshold = 0.5
    question4 = "Any medical advice again?" # Same as question2
    response4 = mcp_instance.handle_question(question4)
    print(f"\nFinal Response for '{question4}' (threshold 0.5):\n{response4}\n")
    assert response4["agent_name"] == "OkAgent"
    
    # Test case 5: Ensure error agent doesn't break the chain and fallback is used
    print("--- Testing with an agent that always errors (but good agent can still answer) ---")
    mcp_instance_with_error_priority = MasterControlProgram(agents=[error_agent, good_agent], fallback_handler=fallback_h, confidence_threshold=0.7)
    question5 = "A question about health and wellness."
    response5 = mcp_instance_with_error_priority.handle_question(question5)
    print(f"\nFinal Response for '{question5}':\n{response5}\n")
    assert response5["agent_name"] == "GoodAgent" # GoodAgent should still be chosen if its confidence is high enough despite ErrorAgent failing first

    print("MasterControlProgram example finished.")
