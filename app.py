import streamlit as st
import json
import networkx as nx

# -------------------------------
# Load Knowledge Graph Data
# -------------------------------
with open("kg.json", "r") as f:
    data = json.load(f)

# -------------------------------
# Build Knowledge Graph
# -------------------------------
G = nx.Graph()

# Add category nodes
for category in data["categories"]:
    G.add_node(category, type="category")

# Add brand nodes
for brand in data["brands"]:
    G.add_node(brand, type="brand")

# Add attribute nodes
for attr in data["attributes"]:
    G.add_node(attr, type="attribute")

# Add product nodes and edges
for product, info in data["products"].items():
    G.add_node(product, type="product", price=info["price"], stock=info["stock"])

    G.add_edge(product, info["category"], relation="IS_A")
    G.add_edge(product, info["brand"], relation="HAS_BRAND")

    for attr in info["attributes"]:
        G.add_edge(product, attr, relation="HAS_ATTRIBUTE")

# Add category similarity edges
for cat, similars in data["category_similarity"].items():
    for s in similars:
        G.add_edge(cat, s, relation="SIMILAR_TO")

# -------------------------------
# Rule Text Mapping
# -------------------------------
RULE_TEXT = {
    "same_category_same_brand": "Same category and same brand as requested product",
    "same_category_diff_brand": "Same category but different brand",
    "similar_category": "From a related category",
    "all_required_tags_matched": "Matches all required attributes",
    "cheaper_option": "Cheaper than requested product"
}

# -------------------------------
# Helper Functions
# -------------------------------
def get_product_info(product):
    return data["products"].get(product)

def find_alternatives(requested_product, max_price, required_tags, preferred_brand):
    requested_info = get_product_info(requested_product)
    results = []

    if not requested_info:
        return []

    requested_category = requested_info["category"]
    requested_price = requested_info["price"]

    # Step 1: Same category products
    candidate_categories = [requested_category]

    # Step 2: Similar categories
    for neighbor in G.neighbors(requested_category):
        if G.edges[requested_category, neighbor]["relation"] == "SIMILAR_TO":
            candidate_categories.append(neighbor)

    # Traverse graph
    for product, info in data["products"].items():
        if product == requested_product:
            continue

        explanation_rules = []

        # Stock check
        if info["stock"] <= 0:
            continue

        # Price check
        if info["price"] > max_price:
            continue

        # Attribute check
        if not all(tag in info["attributes"] for tag in required_tags):
            continue
        else:
            explanation_rules.append("all_required_tags_matched")

        # Brand preference
        if preferred_brand and info["brand"] != preferred_brand:
            continue

        # Category logic
        if info["category"] == requested_category:
            if info["brand"] == requested_info["brand"]:
                explanation_rules.append("same_category_same_brand")
            else:
                explanation_rules.append("same_category_diff_brand")
        elif info["category"] in candidate_categories:
            explanation_rules.append("similar_category")
        else:
            continue

        # Price comparison
        if info["price"] < requested_price:
            explanation_rules.append("cheaper_option")

        score = len(explanation_rules)
        results.append((product, info, explanation_rules, score))

    results.sort(key=lambda x: x[3], reverse=True)
    return results[:3]

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("🛒 Shopkeeper Product Substitution Assistant")

product_list = list(data["products"].keys())
requested_product = st.selectbox("Select Product", product_list)

max_price = st.number_input("Maximum Price", min_value=1, value=100)

required_tags = st.multiselect(
    "Required Attributes",
    data["attributes"]
)

preferred_brand = st.selectbox(
    "Preferred Brand (Optional)",
    [""] + data["brands"]
)

if st.button("Find Alternatives"):
    info = get_product_info(requested_product)

    if info["stock"] > 0:
        st.success(f"✅ {requested_product} is available at ₹{info['price']}")
    else:
        st.warning("❌ Product out of stock. Searching alternatives...")

        alternatives = find_alternatives(
            requested_product,
            max_price,
            required_tags,
            preferred_brand if preferred_brand else None
        )

        if not alternatives:
            st.error("No suitable alternative found.")
        else:
            for product, info, rules, score in alternatives:
                st.subheader(product)
                st.write(f"Price: ₹{info['price']}")
                st.write(f"Brand: {info['brand']}")
                st.write("Explanation:")
                for r in rules:
                    st.write(f"- {RULE_TEXT[r]}")
