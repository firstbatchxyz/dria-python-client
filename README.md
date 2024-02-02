# Dria Python Client

## Description
The **Dria Python Client** is a powerful Python library that seamlessly integrates with the Dria API, providing a convenient interface to harness the capabilities of Dria's vector search and retrieval services. Dria is a cutting-edge platform designed to streamline your AI-powered search and data retrieval tasks, and this client empowers Python developers to leverage its full potential.

## Features
- Knowledge Base Management: Create and manage knowledge bases effortlessly.
- Vector Search: Perform vector-based searches and retrieve relevant results.
- Query with Vectors: Utilize vector queries to obtain contextually accurate responses.
- Data Fetching: Fetch specific data entries by their IDs.
- Batch Data Insertion: Efficiently insert data in bulk into Dria's knowledge base.
- Model Variety: Support for a range of text embedding models, including OpenAI's Text Embeddings and Jina's Embeddings V2.

## Installation
To install the **Dria Python Client**, you can use pip:

```bash
pip install dria
```

## Supported Embedding Models

The Dria Python Client supports a variety of text embedding models, including:

- OpenAI's Text Embeddings-2 Ada (text-embedding-ada-002)
- OpenAI's Text Embedding-3 Small (text-embedding-3-large)
- OpenAI's Text Embedding-3 Large (text-embedding-ada-002)
- Jina's Embeddings V2 Base EN (jina-embeddings-v2-base-en)
- Jina's Embeddings V2 Small EN (jina-embeddings-v2-small-en)

## Custom Embedding Models

In addition to the pre-defined text embedding models, the Dria Python Client also allows you to use custom embedding models. Custom embedding models can be useful when you have specific requirements or when you want to fine-tune your text embeddings for your knowledge base.

Please note that when using custom embedding models, you won't be able to perform text-based searches through the Dria API or UI. You can only perform vector-based queries using your custom embeddings.


## Usage
### Querying the Existing Knowledge Base
```python
from dria import Dria

# Initialize the DriaIndex instance with your API key and knowledge contract ID
dria_index = Dria(api_key="<YOUR_API_KEY>", contract_id="<KNOWLEDGE_CONTRACT_ID>")

# Perform a text-based search
results = dria_index.search("What is the capital of France?", top_n=10)
print(results)

# Perform a vector-based query
vector_query_results = dria_index.query([0.1, 0.2, 0.3], top_n=10)
print(vector_query_results)

# Fetch data for specific IDs
fetched_data = dria_index.fetch([1, 2, 3])
print(fetched_data)


```

### Create New Knowledge Base

#### Using Pre-defined Embedding Models
```python
from dria import Dria, Models

# Initialize the Dria instance with your API key
dria_index = Dria(api_key="<YOUR_API_KEY>")

# Create a new knowledge base
dria_index.create(
    name="France's AI Development",
    embedding=Models.jina_embeddings_v2_base_en,
    category="Artificial Intelligence",
    description="Explore the growth and contributions of France in the field of Artificial Intelligence."
)

```
#### Using Custom Embedding Models
```python
from dria import Dria

# Initialize the Dria instance with your API key
dria_index = Dria(api_key="<YOUR_API_KEY>")

# Create a new knowledge base
dria_index.create(
    name="France's AI Development",
    embedding="meta-llama/Llama-2-7b",
    category="Artificial Intelligence",
    description="Explore the growth and contributions of France in the field of Artificial Intelligence."
)

```
## Usage Example

Let's try with existing knowledge base. We will use the [The Library of Alexandria](https://dria.co/knowledge/DA9F3YqTRrYEXCFhzaFgOW6jZ0NGn3PK9Q6DjuDHN0E) for this example.
```python
from dria import Dria

dria_index = Dria(api_key="<YOUR_API_KEY>",
                       contract_id="DA9F3YqTRrYEXCFhzaFgOW6jZ0NGn3PK9Q6DjuDHN0E")

print(dria_index.search("Who found the first library catalog in the history?", top_n=10, rerank=True))
```

