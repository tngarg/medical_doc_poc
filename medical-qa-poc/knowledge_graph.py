import os
import networkx as nx
import matplotlib.pyplot as plt # For visualization, optional

class KnowledgeGraphManager:
    def __init__(self, kg_file_path: str = "data/medical_kg.gml"):
        """
        Initializes the KnowledgeGraphManager.

        Args:
            kg_file_path (str): Path to save/load the knowledge graph file (e.g., GML, GraphML).
        """
        self.kg_file_path = kg_file_path
        self.graph = nx.MultiDiGraph()  # Using a directed graph that allows multiple edges between nodes

        # Ensure the directory for the KG file exists
        kg_dir = os.path.dirname(self.kg_file_path)
        if kg_dir and not os.path.exists(kg_dir):
            os.makedirs(kg_dir)
            print(f"Created directory for KG file: {kg_dir}")

        self.load_graph()
        print(f"KnowledgeGraphManager initialized. Graph has {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")

    def add_node(self, node_id: str, node_type: str = None, **attributes):
        """Adds a node to the graph."""
        if not self.graph.has_node(node_id):
            self.graph.add_node(node_id, type=node_type, **attributes)
            # print(f"Added node: {node_id} with type: {node_type} and attributes: {attributes}")
        else:
            # Optionally update attributes if node already exists
            # print(f"Node {node_id} already exists. Updating attributes.")
            for key, value in attributes.items():
                self.graph.nodes[node_id][key] = value
            if node_type and 'type' not in self.graph.nodes[node_id]:
                 self.graph.nodes[node_id]['type'] = node_type


    def add_edge(self, source_node_id: str, target_node_id: str, relationship: str, **attributes):
        """Adds a directed edge (relationship) between two nodes."""
        if not self.graph.has_node(source_node_id):
            print(f"Warning: Source node '{source_node_id}' not found. Adding it implicitly.")
            self.add_node(source_node_id, node_type="Unknown") # Add with a default type
        if not self.graph.has_node(target_node_id):
            print(f"Warning: Target node '{target_node_id}' not found. Adding it implicitly.")
            self.add_node(target_node_id, node_type="Unknown")

        # Add edge with relationship type and any other attributes
        self.graph.add_edge(source_node_id, target_node_id, key=relationship, relationship_type=relationship, **attributes)
        # print(f"Added edge: ({source_node_id})-[{relationship}]->({target_node_id}) with attributes: {attributes}")

    def add_triplets(self, triplets: list):
        """
        Adds a list of triplets (subject, predicate, object) to the graph.

        Args:
            triplets (list): A list of tuples, where each tuple is
                             (subject_id, subject_type, predicate, object_id, object_type, edge_attributes).
                             Types and edge_attributes are optional.
                             Example: [("EHR_System", "Software", "processes", "Patient_Data", "Data", {"version": "1.0"})]
                                      [("Aspirin", "Drug", "treats", "Headache", "Symptom")]
        """
        for triplet in triplets:
            s, s_type, p, o, o_type = None, None, None, None, None
            edge_attrs = {}

            if len(triplet) == 3: # (s, p, o)
                s, p, o = triplet
            elif len(triplet) == 5: # (s, s_type, p, o, o_type)
                s, s_type, p, o, o_type = triplet
            elif len(triplet) == 6: # (s, s_type, p, o, o_type, edge_attrs)
                s, s_type, p, o, o_type, edge_attrs = triplet
            else:
                print(f"Warning: Skipping invalid triplet format: {triplet}")
                continue

            self.add_node(s, node_type=s_type)
            self.add_node(o, node_type=o_type)
            self.add_edge(s, o, relationship=p, **edge_attrs)
        print(f"Added {len(triplets)} triplets. Graph now has {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")


    def get_neighbors(self, node_id: str):
        """Returns neighbors of a node."""
        if self.graph.has_node(node_id):
            return list(self.graph.neighbors(node_id))
        return []

    def get_node_attributes(self, node_id: str):
        """Returns attributes of a node."""
        if self.graph.has_node(node_id):
            return self.graph.nodes[node_id]
        return None

    def get_edge_data(self, source_node_id: str, target_node_id: str, key: str = None):
        """Returns data of an edge (or all edges between two nodes if key is None)."""
        if self.graph.has_edge(source_node_id, target_node_id):
            return self.graph.get_edge_data(source_node_id, target_node_id, key=key)
        return None

    def query_graph(self, start_node: str, relationship: str = None, target_node_type: str = None):
        """
        Simple query function. Finds nodes connected to start_node via a specific relationship.
        Can further filter by target_node_type.

        Args:
            start_node (str): The ID of the node to start the query from.
            relationship (str, optional): The type of relationship to follow.
            target_node_type (str, optional): Filter targets by their 'type' attribute.

        Returns:
            list: A list of target node IDs that match the query.
        """
        results = []
        if not self.graph.has_node(start_node):
            print(f"Query failed: Start node '{start_node}' not in graph.")
            return results

        for s, t, data in self.graph.edges(start_node, data=True):
            edge_relationship = data.get('relationship_type') # or 'key' if you used add_edge with key=relationship

            match_relationship = (relationship is None) or (edge_relationship == relationship)

            if match_relationship:
                if target_node_type:
                    node_attrs = self.get_node_attributes(t)
                    if node_attrs and node_attrs.get('type') == target_node_type:
                        results.append(t)
                else:
                    results.append(t)
        return results


    def save_graph(self, file_path: str = None):
        """Saves the graph to a file (e.g., GML format)."""
        path_to_save = file_path if file_path else self.kg_file_path
        try:
            if path_to_save.endswith(".gml"):
                nx.write_gml(self.graph, path_to_save)
            elif path_to_save.endswith(".graphml"):
                nx.write_graphml(self.graph, path_to_save)
            # Add other formats like JSON if needed
            else:
                print(f"Warning: Unsupported file format for saving: {path_to_save}. Defaulting to GML.")
                # Ensure the path has a .gml extension if it was originally different and unsupported
                base, _ = os.path.splitext(path_to_save)
                path_to_save_gml = base + ".gml"
                nx.write_gml(self.graph, path_to_save_gml)
                if path_to_save != path_to_save_gml:
                     print(f"Graph saved to {path_to_save_gml} instead.")
                else:
                    print(f"Graph saved to {path_to_save_gml}")
                return

            print(f"Knowledge graph saved to {path_to_save}")
        except Exception as e:
            print(f"Error saving knowledge graph to {path_to_save}: {e}")

    def load_graph(self, file_path: str = None):
        """Loads the graph from a file."""
        path_to_load = file_path if file_path else self.kg_file_path
        if os.path.exists(path_to_load):
            try:
                if path_to_load.endswith(".gml"):
                    self.graph = nx.read_gml(path_to_load)
                elif path_to_load.endswith(".graphml"):
                    self.graph = nx.read_graphml(path_to_load)
                else:
                    print(f"Warning: Unsupported file format for loading: {path_to_load}. Trying GML by default.")
                    self.graph = nx.read_gml(path_to_load) # Attempt GML
                print(f"Knowledge graph loaded from {path_to_load}. Nodes: {self.graph.number_of_nodes()}, Edges: {self.graph.number_of_edges()}")
            except Exception as e:
                print(f"Error loading knowledge graph from {path_to_load}: {e}. Initializing an empty graph.")
                self.graph = nx.MultiDiGraph()
        else:
            print(f"Knowledge graph file not found at {path_to_load}. Initializing an empty graph.")
            self.graph = nx.MultiDiGraph()

    def visualize_graph(self, layout_type='spring', show_labels=True, output_file=None):
        """Visualizes the graph using Matplotlib."""
        if not self.graph.nodes():
            print("Graph is empty. Nothing to visualize.")
            return

        plt.figure(figsize=(12, 10))

        if layout_type == 'spring':
            pos = nx.spring_layout(self.graph, k=0.5, iterations=50) # k adjusts spacing, iterations for convergence
        elif layout_type == 'circular':
            pos = nx.circular_layout(self.graph)
        elif layout_type == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(self.graph)
        else: # default to spring
            pos = nx.spring_layout(self.graph)

        nx.draw_networkx_nodes(self.graph, pos, node_size=700, alpha=0.8)
        nx.draw_networkx_edges(self.graph, pos, width=1.0, alpha=0.5, arrowsize=15)

        if show_labels:
            nx.draw_networkx_labels(self.graph, pos, font_size=9)

        # For drawing edge labels (relationship types)
        # edge_labels = {(u,v):d['relationship_type'] for u,v,d in self.graph.edges(data=True) if 'relationship_type' in d}
        # For MultiDiGraph, edge labels are trickier if multiple edges exist between nodes.
        # This example just picks one if multiple exist for simplicity for visualization.
        simple_edge_labels = {}
        for u, v, data in self.graph.edges(data=True):
             # If you have multiple edges, this will only show one label per pair (u,v)
            simple_edge_labels[(u,v)] = data.get('relationship_type', '')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=simple_edge_labels, font_size=7)

        plt.title("Knowledge Graph Visualization")
        plt.axis('off') # Turn off the axis

        if output_file:
            plt.savefig(output_file)
            print(f"Graph visualization saved to {output_file}")
        else:
            plt.show()


# --- Example Usage (for testing) ---
if __name__ == "__main__":
    kg_file = "data/test_medical_kg.gml" # Use a test-specific file
    if os.path.exists(kg_file): # Clean up previous test runs
        os.remove(kg_file)

    print("Running KnowledgeGraphManager example...")
    kg_manager = KnowledgeGraphManager(kg_file_path=kg_file)

    # 1. Add nodes and edges
    print("\nAdding nodes and edges...")
    kg_manager.add_node("Aspirin", node_type="Drug", description="Common pain reliever")
    kg_manager.add_node("Ibuprofen", node_type="Drug")
    kg_manager.add_node("Headache", node_type="Symptom")
    kg_manager.add_node("Fever", node_type="Symptom")

    kg_manager.add_edge("Aspirin", "Headache", relationship="treats", dosage="500mg")
    kg_manager.add_edge("Aspirin", "Fever", relationship="reduces")
    kg_manager.add_edge("Ibuprofen", "Fever", relationship="reduces", note="Also an anti-inflammatory")

    # 2. Add triplets
    print("\nAdding triplets...")
    triplets_to_add = [
        ("Paracetamol", "Drug", "treats", "Pain", "Symptom"),
        ("Pain", "Symptom", "is_a", "Symptom", "MedicalCondition"), # Example of different types for same node ID if not careful
        ("Paracetamol", "Drug", "reduces", "Fever", "Symptom", {"dosage_adult": "500-1000mg"})
    ]
    kg_manager.add_triplets(triplets_to_add)

    print(f"\nGraph after additions: {kg_manager.graph.number_of_nodes()} nodes, {kg_manager.graph.number_of_edges()} edges.")

    # 3. Query the graph
    print("\nQuerying graph: What does Aspirin treat?")
    aspirin_treats = kg_manager.query_graph(start_node="Aspirin", relationship="treats")
    print(f"Aspirin treats: {aspirin_treats}")

    print("\nQuerying graph: What reduces Fever and is a Drug?")
    fever_reducers = kg_manager.query_graph(start_node="Fever", relationship="reduces") # This gets what Fever is reduced BY
                                                                                      # Need to iterate or change query logic for "what reduces fever"

    # A more complex query: find drugs that reduce fever
    drugs_reducing_fever = []
    for node_id, attrs in kg_manager.graph.nodes(data=True):
        if attrs.get('type') == 'Drug':
            # Check if this drug reduces fever
            # This requires iterating through edges or a reverse lookup if not directly stored
            # For simplicity, let's check outgoing edges from this drug node
            if "Fever" in kg_manager.query_graph(start_node=node_id, relationship="reduces"):
                 drugs_reducing_fever.append(node_id)
    print(f"Drugs that reduce Fever: {drugs_reducing_fever}")


    # 4. Save and load the graph
    print("\nSaving graph...")
    kg_manager.save_graph()

    print("\nLoading graph into new manager...")
    kg_manager_loaded = KnowledgeGraphManager(kg_file_path=kg_file)
    # Verify loaded graph
    print(f"Loaded graph has {kg_manager_loaded.graph.number_of_nodes()} nodes and {kg_manager_loaded.graph.number_of_edges()} edges.")
    aspirin_treats_loaded = kg_manager_loaded.query_graph(start_node="Aspirin", relationship="treats")
    print(f"Aspirin (from loaded graph) treats: {aspirin_treats_loaded}")

    # 5. Visualize (optional, will pop up a window or save to file)
    print("\nVisualizing graph (if matplotlib is correctly configured)...")
    # kg_manager.visualize_graph(output_file="data/test_kg_visualization.png") # Save to file
    # kg_manager.visualize_graph() # Show plot

    # Clean up test file
    if os.path.exists(kg_file):
        # os.remove(kg_file) # Keep it for inspection if needed
        pass
    if os.path.exists("data/test_kg_visualization.png"):
        # os.remove("data/test_kg_visualization.png")
        pass

    print("KnowledgeGraphManager example finished.")
