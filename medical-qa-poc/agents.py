from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self):
        self.name = self.__class__.__name__
        print(f"Initializing agent: {self.name}")

    @abstractmethod
    def query(self, question: str, context: dict = None) -> dict:
        pass

    def _prepare_response(self, answer: str, confidence: float, source: str or list, error: str = None) -> dict:
        return {
            "answer": answer,
            "confidence": confidence,
            "source": source,
            "agent_name": self.name,
            "error": error
        }

class SimpleVectorStoreAgent(BaseAgent):
    def __init__(self, name: str, vector_store_manager, llm_pipeline=None, top_k_results: int = 3):
        self.name = name
        self.vector_store_manager = vector_store_manager
        self.llm_pipeline = llm_pipeline
        self.top_k_results = top_k_results

        if not self.vector_store_manager or not hasattr(self.vector_store_manager, 'similarity_search'):
            raise ValueError("Valid VectorStoreManager instance is required for SimpleVectorStoreAgent.")

    def query(self, question: str, context: dict = None) -> dict:
        print(f"{self.name} received question: '{question}'")

        if not self.vector_store_manager.vector_store:
            return self._prepare_response("Vector store not initialized.", 0.0, "System", "Vector store not available.")

        try:
            retrieved_docs_with_scores = self.vector_store_manager.similarity_search(question, k=self.top_k_results)
            if not retrieved_docs_with_scores:
                return self._prepare_response("No relevant documents found.", 0.1, "Vector Store")

            sources = list(set([doc.metadata.get("source", "Unknown") for doc, score in retrieved_docs_with_scores]))
            confidence_proxy = 1.0 / (1.0 + retrieved_docs_with_scores[0][1]) if retrieved_docs_with_scores[0][1] >= 0 else 0.0

            if self.llm_pipeline:
                documents_for_llm = [doc for doc, score in retrieved_docs_with_scores]
                generated_answer = f"LLM processed answer for: '{question}'. Top document: {documents_for_llm[0].page_content[:100]}..."
            else:
                snippets = [f"Source: {doc.metadata.get('source', 'N/A')}, Content: ...{doc.page_content[:200]}..." for doc, score in retrieved_docs_with_scores]
                generated_answer = "\n".join(snippets)

            return self._prepare_response(generated_answer, confidence_proxy, sources)

        except Exception as e:
            return self._prepare_response("An unexpected error occurred.", 0.0, "System", str(e))

class KnowledgeGraphAgent(BaseAgent):
    def __init__(self, name: str, kg_manager):
        self.name = name
        self.kg_manager = kg_manager

        if not self.kg_manager or not hasattr(self.kg_manager, 'query_graph'):
            raise ValueError("Valid KnowledgeGraphManager instance is required for KnowledgeGraphAgent.")

    def query(self, question: str, context: dict = None) -> dict:
        print(f"{self.name} received question: '{question}'")

        node_info = self.kg_manager.get_node_attributes(question)
        if node_info:
            answer = f"Found information about '{question}': {node_info}"
            neighbors = self.kg_manager.get_neighbors(question)
            source_info = f"Node: {question}, Neighbors: {neighbors[:3]}"
            return self._prepare_response(answer, 0.7, source_info)

        if "treats" in question.lower():
            parts = question.lower().split("treats")
            if len(parts) == 2:
                drug = parts[0].strip().capitalize()
                results = self.kg_manager.query_graph(start_node=drug, relationship="treats")
                if results:
                    return self._prepare_response(f"{drug} treats: {', '.join(results)}", 0.75, f"KG: {drug}-treats->?")

        return self._prepare_response(
            f"Knowledge Graph couldn't directly answer: '{question}'.", 0.2, "Knowledge Graph")
