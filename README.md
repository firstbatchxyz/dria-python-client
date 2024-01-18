# Dria Python Client

## Description
The **Dria Python Client** is a Python library that provides convenient access to the Dria API for interacting with Dria's services. Dria is a platform for efficient vector search and retrieval, and this client allows you to integrate Dria's capabilities into your Python applications.

## Features
- Search for vectors and retrieve results.
- Perform queries using vectors and get relevant results.
- Fetch data for specific IDs.
- Batch insert data into Dria's knowledge base.
- Supports different text models and options.

## Installation
To install the **Dria Python Client**, you can use pip:

```bash
pip install dria-python-client
```


## Usage
```python
from dria import DriaClient

# Initialize the client with your API key
api_key = "your_api_key_here"
dria = DriaClient(api_key)

# Perform a search
query = "What is the capital of France?"
contract_id = "your_contract_id_here"
top_n = 10

response = dria.search(query, contract_id, top_n)
print(response.results)
```

## Future Development

- Write proper README documentation.
- Implement unit tests for the client.
- Write comprehensive documentation for using the client.
- Add additional Pydantic type checks for robustness.
- Enhance client creation and configuration options.




