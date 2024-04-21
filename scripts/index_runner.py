from dria import Dria, Models

dria_index = Dria(api_key="<YOUR_API_KEY>")
text = "What is the capital of France?"
dria_index.create(name="test", embedding=Models.jina_embeddings_v2_base_en, category="Science", description="test")
dria_index.insert_text([{"text": text,
                        "metadata": {"id": 1, "description": text, "topic": "France"}}])
print(dria_index.search(text, top_n=10))
print(dria_index.query([0.1, 0.2, 0.3], 10))
print(dria_index.fetch([1, 2, 3]))
