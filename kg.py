import networkx as nx
import json

class KnowledgeGraph:
    def __init__(self, data_path):
        self.graph = nx.DiGraph()
        self.load_data(data_path)

    def load_data(self, path):
        with open(path) as f:
            data = json.load(f)

        for product in data["products"]:
            pid = product["id"]
            self.graph.add_node(pid, type="product", **product)

            # Category
            cat = product["id"]
            self.graph.add_node(cat, type="category")
            self.graph.add_edge(pid, cat, relation="IS_A")

            #Brand
            brand = product["brand"]
            self.graph.add_node(brand, type="brand")
            self.graph.add_edge(pid, brand, relation="HAS_BRAND")

            #Attributes
            for attr in product["atrributes"]:
                self.graph.add_node(attr, type="attribute")
                self.graph.add_edge(pid, attr, relation="HAS_ATTRIBUTE")

        #Category similarity
        for cat, similars in data["category_similarity"].items():
            for s in similars:
                self.graph.add_edge(cat, s, relation="SIMILAR_TO")
                        
