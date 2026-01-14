import json
import networkx as nx

class KnowledgeGraph:
    def __init__(self, data_path):
        self.graph = nx.DiGraph()
        self.load_data(data_path)

    def load_data(self, path):
        with open(path, "r", encoding="utf-8") as f:
            products = json.load(f)

        for product in products:
            pid = product["id"]

            self.graph.add_node(pid, type="product", **product)

            # Category
            category = product.get("category")
            if category:
                self.graph.add_node(category, type="category")
                self.graph.add_edge(pid, category, relation="IS_A")

            # Brand
            brand = product.get("brand")
            if brand:
                self.graph.add_node(brand, type="brand")
                self.graph.add_edge(pid, brand, relation="HAS_BRAND")

            # Attributes (SAFE)
            for attr in product.get("attributes", []):
                self.graph.add_node(attr, type="attribute")
                self.graph.add_edge(pid, attr, relation="HAS_ATTRIBUTE")
