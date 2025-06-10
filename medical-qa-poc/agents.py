from abc import ABC, abstractmethod

# Assuming vector_store.py and knowledge_graph.py are in the same directory
# from vector_store import VectorStoreManager
# from knowledge_graph import KnowledgeGraphManager
# from langchain.llms import HuggingFacePipeline, OpenAI # Example LLMs
# from langchain.chains import RetrievalQA

class BaseAgent(ABC):
    """
    Abstract base class for all Question Answering agents.
    """
    def __init__(self):
        self.name = self.__class__.__name__
        print(f"Initializing agent: {self.name}")

    @abstractmethod
    def query(self, question: str, context: dict = None) -> dict:
        """
        Processes a question and returns an answer, confidence, and source.

        Args:
            question (str): The question to be answered.
            context (dict, optional): Additional context for the agent,
                                      which might include chat history, user profile, etc.

        Returns:
            dict: A dictionary containing:
                  - "answer" (str): The generated answer.
                  - "confidence" (float): The confidence score of the answer (0.0 to 1.0).
                  - "source" (str or list): The source(s) of the information used for the answer.
                                           Could be document names, KG entities, etc.
                  - "error" (str, optional): Any error message if processing failed.
        """
        pass

    def _prepare_response(self, answer: str, confidence: float, source: str or list, error: str = None) -> dict:
        """
        Helper method to format the response dictionary.
        """
        return {
            "answer": answer,
            "confidence": confidence,
            "source": source,
            "agent_name": self.name,
            "error": error
        }

class SimpleVectorStoreAgent(BaseAgent):
    """
    A simple agent that uses a VectorStoreManager to find relevant documents
    and then (optionally) a Language Model to generate an answer.
    """
    def __init__(self, vector_store_manager, llm_pipeline=None, top_k_results: int = 3):
        """
        Args:
            vector_store_manager (VectorStoreManager): Instance of the vector store manager.
            llm_pipeline (langchain.chains.base.Chain, optional): A Langchain QA chain or LLM pipeline.
                                                                  If None, will return raw document snippets.
            top_k_results (int): Number of relevant documents to retrieve from the vector store.
        """
        super().__init__()
        self.vector_store_manager = vector_store_manager
        self.llm_pipeline = llm_pipeline # This could be a RetrievalQA chain
        self.top_k_results = top_k_results

        if not self.vector_store_manager or not hasattr(self.vector_store_manager, 'similarity_search'):
            raise ValueError("Valid VectorStoreManager instance is required for SimpleVectorStoreAgent.")

        # Example: Initialize a default LLM if none provided (and if desired)
        # if self.llm_pipeline is None:
        #     # This is a placeholder. You'd need to configure your LLM properly.
        #     # from langchain.llms import SomeDefaultLLM
        #     # from langchain.chains import RetrievalQA
        #     # llm = SomeDefaultLLM()
        #     # self.llm_pipeline = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff",
        #     #                                               retriever=self.vector_store_manager.vector_store.as_retriever(search_kwargs={"k": top_k_results}))
        #     print("Warning: No LLM pipeline provided to SimpleVectorStoreAgent. Will return raw document snippets if not using a full QA chain.")


    def query(self, question: str, context: dict = None) -> dict:
        """
        Queries the vector store for relevant documents and uses an LLM to generate an answer.
        """
        print(f"{self.name} received question: '{question}'")
        if not self.vector_store_manager.vector_store:
            return self._prepare_response(
                answer="Vector store not initialized.",
                confidence=0.0,
                source="System",
                error="Vector store is not available."
            )

        try:
            # 1. Retrieve relevant documents
            print(f"Searching vector store with k={self.top_k_results}...")
            # The `similarity_search` in our VectorStoreManager returns (doc, score) tuples
            # Langchain's QA chains usually expect a retriever that returns Document objects directly.
            # If using a full Langchain QA chain passed as self.llm_pipeline, it might handle retrieval itself.

            retrieved_docs_with_scores = self.vector_store_manager.similarity_search(question, k=self.top_k_results)

            if not retrieved_docs_with_scores:
                return self._prepare_response(
                    answer="No relevant documents found in the vector store.",
                    confidence=0.1, # Low confidence as nothing was found
                    source="Vector Store"
                )

            sources = list(set([doc.metadata.get("source", "Unknown") for doc, score in retrieved_docs_with_scores]))

            # For now, let's consider the highest score among retrieved docs as a proxy for confidence
            # This is a simplistic approach; more sophisticated confidence scoring would be needed.
            highest_score = max(score for doc, score in retrieved_docs_with_scores) if retrieved_docs_with_scores else 0.0
            # FAISS scores are L2 distance, so lower is better. We might want to invert or normalize this.
            # For simplicity, let's assume higher score from similarity_search_with_score means more similar (needs checking based on FAISS version/config)
            # If it's distance, then confidence should be inversely proportional.
            # Let's assume it's similarity for now (0 to 1, higher is better - this is NOT how FAISS score usually works)
            # A more robust way: use softmax over scores or a calibrated model.
            # For FAISS, score is distance. So confidence ~ 1 / (1 + distance) or similar.
            # Let's assume a simple heuristic: if best score (distance) is < 0.5, high confidence, < 1.0 medium, etc.
            # This needs proper calibration. For now, just pass the raw score or a transformation.
            confidence_proxy = 1.0 / (1.0 + retrieved_docs_with_scores[0][1]) if retrieved_docs_with_scores[0][1] >= 0 else 0.0 # Example for distance


            # 2. Generate answer using LLM (if available)
            if self.llm_pipeline:
                print("Using LLM pipeline to generate answer...")
                # If self.llm_pipeline is a Langchain QA chain (e.g., RetrievalQA):
                # It expects a question and returns a dict like {"result": "answer text"}
                # The retriever for such a chain should be configured from vector_store_manager.vector_store
                try:
                    # If the llm_pipeline is a chain that does its own retrieval:
                    # result = self.llm_pipeline({"query": question})
                    # If it expects documents to be passed:
                    documents_for_llm = [doc for doc, score in retrieved_docs_with_scores]
                    # result = self.llm_pipeline({"input_documents": documents_for_llm, "question": question})

                    # This part depends heavily on how self.llm_pipeline is defined.
                    # For a generic `Chain` that might not be a QA chain:
                    # We'll assume it's a QA chain for now.
                    # Placeholder for actual call:
                    # response = self.llm_pipeline.run(question=question, context=retrieved_docs_with_scores) # This is not standard

                    # Let's assume llm_pipeline is a RetrievalQA chain for this example.
                    # For RetrievalQA, it would internally use its retriever.
                    # So, the 'documents' are implicitly used if the chain is set up correctly.
                    # qa_result = self.llm_pipeline(question) # Langchain often uses __call__
                    # generated_answer = qa_result.get("result", "LLM failed to generate an answer.")
                    # sources_from_llm = qa_result.get("source_documents", []) # Some chains provide this
                    # if sources_from_llm:
                    #    sources = list(set([doc.metadata.get("source", "Unknown") for doc in sources_from_llm]))

                    # SIMPLIFIED: For now, just combine snippets if no LLM, or placeholder if LLM.
                    # This part needs to be properly implemented with a chosen LLM and chain type.
                    generated_answer = f"LLM processed answer for: '{question}'. Top document: {retrieved_docs_with_scores[0][0].page_content[:100]}..."
                    print(f"LLM generated answer (placeholder): {generated_answer}")

                except Exception as e:
                    print(f"Error during LLM processing: {e}")
                    return self._prepare_response(
                        answer="Failed to generate answer using LLM.",
                        confidence=0.3, # Low confidence due to error
                        source=sources,
                        error=str(e)
                    )
            else:
                # No LLM, return snippets from top documents
                print("No LLM pipeline. Returning snippets from retrieved documents.")
                snippets = [f"Source: {doc.metadata.get('source', 'N/A')}, Content: ...{doc.page_content[:200]}..."
                            for doc, score in retrieved_docs_with_scores]
                generated_answer = "\n".join(snippets)

            return self._prepare_response(generated_answer, confidence_proxy, sources)

        except Exception as e:
            print(f"Error in SimpleVectorStoreAgent query: {e}")
            return self._prepare_response(
                answer="An unexpected error occurred.",
                confidence=0.0,
                source="System",
                error=str(e)
            )


class KnowledgeGraphAgent(BaseAgent):
    """
    Agent that queries the Knowledge Graph.
    (Further implementation needed)
    """
    def __init__(self, kg_manager):
        super().__init__()
        self.kg_manager = kg_manager
        if not self.kg_manager or not hasattr(self.kg_manager, 'query_graph'):
             raise ValueError("Valid KnowledgeGraphManager instance is required for KnowledgeGraphAgent.")

    def query(self, question: str, context: dict = None) -> dict:
        # This is highly dependent on how questions are translated to KG queries.
        # For a PoC, it might look for known entities and relationships in the question.
        # Example: "What are the symptoms of Aspirin?" -> KG query (Aspirin, has_symptom, ?)
        print(f"{self.name} received question: '{question}' - (KG querying logic TBD)")

        # Placeholder logic:
        # Attempt to parse entities and relationships from the question (complex NLP task)
        # For now, let's assume a very simple direct lookup if the question matches a node name.
        node_info = self.kg_manager.get_node_attributes(question)
        if node_info:
            answer = f"Found information about '{question}' in Knowledge Graph: {node_info}"
            neighbors = self.kg_manager.get_neighbors(question)
            source_info = f"Node: {question}, Neighbors: {neighbors[:3]}" # Show first 3 neighbors
            return self._prepare_response(answer, 0.7, source_info) # Arbitrary confidence

        # Try a sample query based on keywords (very naive)
        if "treats" in question.lower():
            parts = question.lower().split("treats")
            if len(parts) == 2:
                drug = parts[0].strip().capitalize() # Simple capitalization
                results = self.kg_manager.query_graph(start_node=drug, relationship="treats")
                if results:
                    return self._prepare_response(f"{drug} treats: {', '.join(results)}", 0.75, f"KG: {drug}-treats->?")

        return self._prepare_response(
            answer=f"Knowledge Graph couldn't directly answer: '{question}'. Requires NLP to KG query translation.",
            confidence=0.2,
            source="Knowledge Graph"
        )

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    # Mock VectorStoreManager and KnowledgeGraphManager for testing
    class MockVectorStoreManager:
        def __init__(self):
            self.vector_store = True # Simulate it's loaded
            print("MockVectorStoreManager initialized.")
        def similarity_search(self, query, k):
            print(f"MockVSM: Searching for '{query}' with k={k}")
            # Mock Document structure
            class MockDoc:
                def __init__(self, page_content, metadata):
                    self.page_content = page_content
                    self.metadata = metadata
            return [(MockDoc(f"Content related to {query}", {"source": "mock_doc.txt"}), 0.5)] # (doc, score)

    class MockKnowledgeGraphManager:
        def __init__(self):
            print("MockKnowledgeGraphManager initialized.")
        def get_node_attributes(self, node_id):
            if node_id == "Aspirin": return {"type": "Drug", "description": "Pain reliever"}
            return None
        def get_neighbors(self, node_id):
            if node_id == "Aspirin": return ["Headache", "Fever"]
            return []
        def query_graph(self, start_node, relationship, target_node_type=None):
            if start_node == "Aspirin" and relationship == "treats": return ["Headache"]
            return []

    print("Running Agents example...\n")

    # Test SimpleVectorStoreAgent
    mock_vs_manager = MockVectorStoreManager()
    vs_agent = SimpleVectorStoreAgent(vector_store_manager=mock_vs_manager)
    vs_response = vs_agent.query("What is good for a headache?")
    print(f"VectorStoreAgent Response:\n{vs_response}\n")

    # Test KnowledgeGraphAgent
    mock_kg_manager = MockKnowledgeGraphManager()
    kg_agent = KnowledgeGraphAgent(kg_manager=mock_kg_manager)
    kg_response_direct = kg_agent.query("Aspirin")
    print(f"KnowledgeGraphAgent Response (direct node): \n{kg_response_direct}\n")
    kg_response_query = kg_agent.query("What does Aspirin treats?")
    print(f"KnowledgeGraphAgent Response (query): \n{kg_response_query}\n")

    print("Agents example finished.")
