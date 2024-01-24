from dria.core.client import DriaClient
from dria.models.models import ModelEnum


class DriaIndex:
    def __init__(self, api_key: str, contract_id: str, model: ModelEnum):
        """
        Initialize the DriaIndex with an API key.

        Args:
            api_key (str): The API key for authentication.
            contract_id (str): The contract ID.
            model (ModelEnum): The embedding model to use.
        """
        self.client = DriaClient(api_key)
        self.contract = contract_id
        self.model = model

    def create_index(self, name: str, embedding: ModelEnum, category: str, description: str = None):
        """
        Create a knowledge base index.

        Args:
            name (str): The name of the knowledge base.
            embedding (str): The embedding model to use.
            category (str): The category of the knowledge base.
            description (str): The description of the knowledge base (optional).

        Returns:
            dict: A dictionary containing the response from the create method.
        """
        response = self.client.create(name, embedding, category, description)
        return response

    def search_query(self, query: str, top_n: int, field: str = None, re_rank: bool = None, level: int = 2):
        """
        Perform a search operation.

        Args:
            query (str): The search query.
            top_n (int): The number of results to retrieve.
            field (str): The field to search in (for CSV sourced knowledge bases).
            re_rank (bool): Whether to perform re-ranking.
            level (int): The search level.

        Returns:
            dict: A dictionary containing the response from the search method.

        Example:
            dria.search("What is the capital of France?", top_n=10)
            dria.search("Where is the Eiffel Tower?", top_n=5)
        """
        response = self.client.search(query, self.contract, top_n, self.model, field, re_rank, level)
        return response

    def query_data(self, vector: list, top_n: int = 10):
        """
        Perform a query operation.

        Args:
            vector (list): The query vector.
            top_n (int): The number of results to retrieve.

        Returns:
            dict: A dictionary containing the response from the query method.
        """
        response = self.client.query(vector, self.contract, top_n)
        return response

    def fetch_data(self, ids: list):
        """
        Fetch data for a list of IDs.

        Args:
            ids (list): The list of IDs to fetch.

        Returns:
            dict: A dictionary containing the response from the fetch method.
        """
        response = self.client.fetch(ids, self.contract)
        return response

    def insert_batch(self, batch: list):
        """
        Batch insert data.

        Args:
            batch (list): The batch data to insert. Each dictionary should have "vectors" (list)
                          and "metadata" (dict). Maximum size is 1000.

        Returns:
            dict: A dictionary containing the response from the batch insert method.
        """
        response = self.client.batch_insert(batch, self.contract)
        return response
