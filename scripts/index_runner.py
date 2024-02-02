from dria import Dria, Models

dria_index = Dria(api_key="<YOUR_API_KEY>")

dria_index.create(name="test", embedding=Models.jina_embeddings_v2_base_en, category="Science", description="test")
print(dria_index.search("What is the capital of France?", top_n=10))
print(dria_index.query([0.1, 0.2, 0.3], 10))
print(dria_index.fetch([1, 2, 3]))
