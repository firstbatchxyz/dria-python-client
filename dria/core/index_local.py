from typing import Optional

from dria.core.client import DriaLocalClient


class DriaLocal:
    def __init__(self):
        self.client_local = DriaLocalClient()

    def fetch(self, ids: list):
        """
        Fetch data for a list of IDs.

        Args:
            ids (list): The list of IDs to fetch.

        Returns:
            List[FetchResult]: A list containing the response from the fetch method.
        """
        response = self.client_local.fetch(ids)
        return response
    def query(self, vector: list, query: Optional[str] = None, top_n: int = 10, level: int = 2):
        """
        Perform a query operation.

        Args:
            vector (list): The query vector.
            query (str): The query string.
            top_n (int): The number of results to retrieve.
            level (int): The search level.


        Returns:
            List[QueryResult]: A list containing the response from the query method.
        """
        response = self.client_local.query(vector, top_n, level, query)
        return response

    def insert_vector(self, batch: list):
        """
        Batch insert data.

        Args:
            batch (list): The batch data to insert. Each dictionary should have "vector" (list)
                          and "metadata" (dict). Maximum size is 1000.

        Returns:
            InsertResponse: A response containing the response from the batch insert method.
        """
        response = self.client_local.batch_vector_insert(batch)
        return response
