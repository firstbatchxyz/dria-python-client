import base64
from typing import List, Dict, Tuple, Optional

import dria.core.grpc.vector_pb2 as vector_pb2
from dria.constants import DRIA_HOST, DRIA_HNSW_ROOT
from dria.core.api.api import API
from dria.exceptions import DriaParameterError
from dria.models import SearchRequest, QueryResponse, FetchResponse, QueryResult
from dria.models.models import FetchRequest, InsertRequest, InsertResponse


class DriaClient:
    def __init__(self, api_key: str):
        """
        Initialize the DriaClient with an API key.
        Args:
            api_key (str): The API key for authentication.
        """

        self._api = API(host=DRIA_HOST, api_key=api_key)
        self._root_path = DRIA_HNSW_ROOT

    def search(self, query: str, contract_id: str, top_n: int,
               field: Optional[str] = None, model: Optional[str] = None,
               re_rank: Optional[bool] = None, level: Optional[int] = None):
        """
        Perform a search operation.
        Args:
            query (str): The search query.
            contract_id (str): The contract ID.
            top_n (int): The number of results to retrieve.
            field (Optional[str]): The field to search in (This field only for CSV sourced knowledge bases).
            model (Optional[str]): The search model to use.
            re_rank (Optional[bool]): Whether to perform re-ranking.
            level (Optional[int]): The search level.

        Example:
            dria.search("What is the capital of France?", "<CONTRACT_ID>", top_n=10)
            dria.search("Where is the Eiffel Tower?", "<CONTRACT_ID>", top_n=10, model="text-embedding-ada-002")

        Returns:
            QueryResponse: The query response.
        """

        sr = SearchRequest(query=query, contract_id=contract_id, top_n=top_n,
                           field=field, model=model, re_rank=re_rank, level=level)
        resp = self._api.post(self._root_path + "/search", payload=sr.to_json())
        return QueryResponse(results=[QueryResult.from_dict(result) for result in resp])

    def query(self, vector: List[float], contract_id: str, top_n: int = 10):
        """
        Perform a query operation.
        Args:
            vector (List[float]): The query vector.
            contract_id (str): The contract ID.
            top_n (int): The number of results to retrieve.

        Example:
            dria.query([0.1, 0.2, 0.3], "<CONTRACT_ID>", top_n=10)

        Returns:
            QueryResponse: The query response.
        """

        qr = QueryResponse(vector=vector, contract_id=contract_id, top_n=top_n)

        resp = self._api.post(self._root_path + "/query", payload=qr.model_dump())
        return QueryResponse(results=[QueryResult.from_dict(result) for result in resp])

    def fetch(self, ids: List[int], contract_id: str):
        """
        Fetch data for a list of IDs.
        Args:
            ids (List[int]): The list of IDs to fetch.
            contract_id (str): The contract ID.

        Example:
            dria.fetch([1, 2, 3], "<CONTRACT_ID>")

        Returns:
            FetchResponse: The fetch response.
        """

        fr = FetchRequest(contract_id=contract_id, id=ids)

        resp = self._api.post(self._root_path + "/fetch", payload=fr.model_dump())
        return FetchResponse(results=(ids, resp))

    def batch_insert(self, batch: List[Dict], contract_id: str):
        """
        Batch insert data.

        Args:
            batch (List[Dict]): The batch data to insert. Each dictionary should have "vectors" (List[float])
                                and "metadata" (Dict). Maximum size is 1000.
            contract_id (str): The contract ID.

        Returns:
            InsertResponse: The response from the batch insert operation.
        Raises:
            ValueError: If the batch size exceeds the maximum limit (1000) or if the format of the batch is invalid.
        """
        if len(batch) > 1000:
            raise DriaParameterError("Batch size exceeds the maximum limit of 1000")
        try:
            formatted_batch = [(item["vectors"], item["metadata"]) for item in batch]
        except KeyError:
            raise DriaParameterError("Batch data must be a list of dictionaries with keys 'vectors' and 'metadata'")

        data = self.__serialize_batch(formatted_batch)
        br = InsertRequest(data=data, contract_id=contract_id, batch_size=len(batch))
        resp = self._api.post(self._root_path + "/insert_batch", payload=br.to_json())
        return InsertResponse(**resp)

    @staticmethod
    def __serialize_batch(batch: List[Tuple[List[float], Dict]]):
        """
        Serialize a batch of data.
        Args:
            batch (List[Tuple[List[float], Dict]]): The batch data to serialize.
        Returns:
            str: The serialized batch as a base64-encoded string.
        """
        singletons = []
        for vec, metadata in batch:
            temp = vector_pb2.Singleton(v=vec, metadata=metadata).SerializeToString()
            base64_encoded_data = base64.b64encode(temp)
            base64_string = base64_encoded_data.decode('utf-8')
            singletons.append(base64_string)

        temp = vector_pb2.Batch(b=singletons).SerializeToString()
        base64_encoded_data = base64.b64encode(temp)
        base64_string = base64_encoded_data.decode('utf-8')
        return base64_string
