import streamlit as st
from kg import KnowledgeGraph
from reasoning import find_substitutes


kg = KnowledgeGraph("data/products.json")


st.title("Product Substitution Assistant")


product = st.text_input("Requested Product ID")
max_price = st.number_input("Max Price", min_value=0)
req_tags = st.multiselect("Required Tags", ["veg", "lactose_free", "sugar_free"])
brand = st.text_input("Preferred Brand (optional)")

if st.button("Find Alternative"):
    if product in kg.graph and kg.graph.nodes[product]["stock"] > 0:
        st.success("Exact product available")
        st.write(kg.graph.nodes[product])

    else:
        results, err = find_substitutes(
            kg,
            product,
            max_price,
            req_tags,
            brand if brand else None
        )
        if err or not results:
            st.warning("No suitable alternative found")
        else:
            for _, prod, rules in results:
                st.subheader(prod["names"])
                st.write(f"Price: ${prod['price']}")
                st.write("Explanation:")
                for r in rules:
                    st.write(f"- {r}")

                            
