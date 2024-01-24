from dria import DriaIndex, ModelEnum


api_key = "<api_key>"
dria_index = DriaIndex(api_key=api_key,
                       contract_id="<contract_id>",
                       model=ModelEnum.jina_embeddings_v2_base_en)

print(dria_index.search_query("What is the capital of France?", top_n=10))
print(dria_index.query_data([0.1, 0.2, 0.3], 10))
print(dria_index.fetch_data([1, 2, 3]))
