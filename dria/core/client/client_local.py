from typing import List, Dict, Optional

from dria.core.api import APILocal
from dria.exceptions import DriaParameterError
from dria.models import QueryResult
from dria.models.models_local import InsertResponse, QueryRequest, VectorInsertRequest, FetchRequest, FetchResult


class DriaLocalClient:
    def __init__(self):
        """
        Initialize the DriaLocalClient.
        """

        self._api = APILocal()

    def query(self, vector: List[float], top_n: int = 10, level: int = 2, query: Optional[str] = None):
        """
        Perform a query operation.
        Args:
            vector (List[float]): The query vector.
            top_n (int): The number of results to retrieve.
            level (int): The search level.
            query (Optional[str]): The query string.

        Example:
            dria.query([0.1, 0.2, 0.3], "<CONTRACT_ID>", top_n=10)

        Returns:
            QueryResult: The query response.
        """

        qr = QueryRequest(vector=vector, top_n=top_n, level=level, query=query)

        resp = self._api.post("/query", payload=qr.model_dump())
        return [QueryResult(**{"id": result["id"], "score": result["score"],
                               "metadata": result["metadata"]}).to_dict() for result in resp]

    def batch_vector_insert(self, batch: List[Dict]):
        """
        Batch insert data.

        Args:
            batch (List[Dict]): The batch data to insert. Each dictionary should have "vector" (List[float])
                                and "metadata" (Dict). Maximum size is 1000.

        Returns:
            InsertResponse: The response from the batch insert operation.
        Raises:
            ValueError: If the batch size exceeds the maximum limit (1000), if the format of the batch is invalid,
                        or if any value under "metadata" is not a string.
        """
        if len(batch) > 1000:
            raise DriaParameterError("Batch size exceeds the maximum limit of 1000")
        try:
            formatted_batch = []
            for item in batch:
                vector = item["vector"]
                metadata = item["metadata"]

                if not all(isinstance(value, (str, float, int, bool)) for value in metadata.values()):
                    raise DriaParameterError("All values under 'metadata' should be string, float, int or bool")

                formatted_batch.append((vector, metadata))
        except KeyError:
            raise DriaParameterError("Batch data must be a list of dictionaries with keys 'vectors' and 'metadata'")

        br = VectorInsertRequest(data=formatted_batch)
        resp = self._api.post("/insert_vector", payload=br.to_json())
        return InsertResponse(**{"message": resp})

    def fetch(self, ids: List[int]):
        """
        Fetch data for a list of IDs.
        Args:
            ids (List[int]): The list of IDs to fetch.

        Example:
            dria.fetch([1, 2, 3], "<CONTRACT_ID>")

        Returns:
            FetchResult: The fetch result.
        """

        if not ids:
            raise DriaParameterError("No IDs provided")

        fr = FetchRequest(id=ids)

        resp = self._api.post("/fetch", payload=fr.model_dump())

        return [FetchResult(metadata={"id": ids[idx], "metadata": result}) for idx, result in enumerate(resp)]
