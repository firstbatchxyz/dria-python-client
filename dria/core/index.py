from typing import Optional, Union

from dria.core.client import DriaClient
from dria.exceptions import DriaParameterError
from dria.models.models import Models


class Dria:
    def __init__(self, api_key: Optional[str] = None, contract_id: Optional[str] = None):
        """
        Initialize the Dria with an API key.

        Args:
            api_key (str): The API key for authentication.
            contract_id (str): The contract ID.
        """
        self.client = DriaClient(api_key)
        self.contract = contract_id
        self.model = self.client.get_model(contract_id) if contract_id is not None else None

    def _ensure_contract(self):
        if self.contract is None:
            raise DriaParameterError("Contract ID is not set. Please set the contract ID or create a new index.")

    def set_contract(self, contract_id: str):
        """
        Set the contract ID.

        Args:
            contract_id (str): The contract ID.
        """
        self.contract = contract_id
        self.model = self.client.get_model(contract_id)

    def create(self, name: str, embedding: Union[Models, str], category: str, description: str = None) -> str:
        """
        Create a knowledge base index.

        Args:
            name (str): The name of the knowledge base.
            embedding (Union[Models, str]): The embedding model to use.
            category (str): The category of the knowledge base.
            description (str): The description of the knowledge base (optional).

        """
        response = self.client.create(name, embedding, category, description)
        self.contract = response.contract_id
        self.model = embedding
        return self.contract

    def search(self, query: str, top_n: int = 10, field: str = None, rerank: bool = True, level: int = 2):
        """
        Perform a search operation.

        Args:
            query (str): The search query.
            top_n (int): The number of results to retrieve.
            field (str): The field to search in (for CSV sourced knowledge bases).
            rerank (bool): Whether to perform re-ranking.
            level (int): The search level.

        Returns:
            List[SearchResponse]: A list containing the response from the search method.

        Example:
            dria.search("What is the capital of France?", top_n=10)
            dria.search("Where is the Eiffel Tower?", top_n=5)
        """
        self._ensure_contract()
        response = self.client.search(query, self.contract, top_n, self.model, field, rerank, level)
        return response

    def query(self, vector: list, top_n: int = 10, level: int = 2):
        """
        Perform a query operation.

        Args:
            vector (list): The query vector.
            top_n (int): The number of results to retrieve.
            level (int): The search level.

        Returns:
            List[QueryResult]: A list containing the response from the query method.
        """
        self._ensure_contract()
        response = self.client.query(vector, self.contract, top_n, level)
        return response

    def fetch(self, ids: list):
        """
        Fetch data for a list of IDs.

        Args:
            ids (list): The list of IDs to fetch.

        Returns:
            List[FetchResult]: A list containing the response from the fetch method.
        """
        self._ensure_contract()
        response = self.client.fetch(ids, self.contract)
        return response

    def remove(self):
        """
        Remove the knowledge base index.

        Returns:
            RemoveResponse: A response containing the response from the remove method.

        """

        self._ensure_contract()
        response = self.client.remove(self.contract)
        return response

    def list(self) -> list:
        """
        List all knowledge bases.

        Returns:
            List: A response containing the contract definitions.

        """

        response = self.client.list_contracts()
        return response["contracts"]

    def get_contract(self, contract_id: str):
        """
        Get the contract details.

        Args:
            contract_id (str): The contract ID.

        Returns:
            ContractResponse: A response containing the contract details.
        """
        response = self.client.get_contract(contract_id)
        return response

    def update(self, **kwargs):
        """
        Update the knowledge base index.

        Only specific fields can be updated. The fields that can be updated are:
        - name
        - description
        - category

        So, the kwargs should contain one or more of these fields.

        Args:
            **kwargs: The arguments to update.


        Returns:
            UpdateResponse: A response containing the response from the update method.
        """
        self._ensure_contract()
        response = self.client.update_knowledge_base(self.contract, **kwargs)
        return response
    def entry_count(self):
        """
        Get the number of entries in the knowledge base.

        Returns:
            UpdateResponse: A response containing the response from the update method.
        """
        self._ensure_contract()
        response = self.client.get_entry_count(self.contract)
        return response

    def insert_vector(self, batch: list, write_blockchain: bool = True):
        """
        Batch insert data.

        Args:
            batch (list): The batch data to insert. Each dictionary should have "vector" (list)
                          and "metadata" (dict). Maximum size is 1000.
            write_blockchain (bool): Whether to write to the blockchain.

        Returns:
            InsertResponse: A response containing the response from the batch insert method.
        """
        self._ensure_contract()
        response = self.client.batch_vector_insert(batch, write_blockchain, self.contract)
        return response

    def insert_text(self, batch: list, write_blockchain: bool = True):
        """
        Batch insert data.

        Args:
            batch (list): The batch data to insert. Each dictionary should have "text" (str)
                          and "metadata" (dict). Maximum size is 1000.
            write_blockchain (bool): Whether to write to the blockchain.

        Returns:
            InsertResponse: A dictionary containing the response from the batch insert with method.
        """
        self._ensure_contract()
        response = self.client.batch_text_insert(batch, write_blockchain,  self.model, self.contract)
        return response
