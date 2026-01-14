from collections import deque

def find_substitutes(kg, query_product, max_price, req_attrs, req_brand):
    G = kg.graph

    if query_product not in G:
        return [], "Product not found"

    results = []

    q_cat = None
    for succ in G.successors(query_product):
        if G.nodes[succ].get("type") == "category":
            q_cat = succ
            break

    if q_cat is None:
        return [], "Category not found"

    categories = [q_cat]
    for succ in G.successors(q_cat):
        categories.append(succ)

    for node, data in G.nodes(data=True):
        if data.get("type") != "product":
            continue
        if node == query_product:
            continue

        if data.get("stock", 0) <= 0:
            continue
        if data.get("price", 0) > max_price:
            continue

        prod_cat = None
        for succ in G.successors(node):
            if G.nodes[succ].get("type") == "category":
                prod_cat = succ
                break

        if prod_cat not in categories:
            continue

        if not set(req_attrs).issubset(set(data.get("attributes", []))):
            continue

        score = 0
        explanation = []

        if prod_cat == q_cat:
            score += 2
            explanation.append("same_category")
        else:
            score += 1
            explanation.append("related_category")

        if req_brand and data.get("brand") == req_brand:
            score += 1
            explanation.append("same_brand")

        explanation.append("all_required_tags_matched")

        results.append((score, data, explanation))

    results.sort(key=lambda x: x[0], reverse=True)
    return results[:3], None
