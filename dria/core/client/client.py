import base64
import json
from typing import List, Dict, Tuple, Optional

import dria.core.grpc.vector_pb2 as vector_pb2
from dria.constants import DRIA_HOST, DRIA_HNSW_ROOT, DRIA_UTIL_HOST, DRIA_HNSW_ROOT_TRAIN
from dria.core.api.api import API
from dria.exceptions import DriaParameterError
from dria.models import SearchRequest, SearchResult, QueryResult
from dria.models.models import FetchRequest, InsertRequest, InsertResponse, ModelEnum, CreateIndex, CreateIndexResponse, \
    QueryRequest, FetchResult


class DriaClient:
    def __init__(self, api_key: str):
        """
        Initialize the DriaClient with an API key.
        Args:
            api_key (str): The API key for authentication.
        """

        self._api = API(host=DRIA_HOST, api_key=api_key)
        self._root_path_train = DRIA_HNSW_ROOT_TRAIN
        self._root_path = DRIA_HNSW_ROOT
        self._utils_host = DRIA_UTIL_HOST

    def create(self, name: str, embedding: ModelEnum, category: str,
               description: Optional[str] = None):
        """
        Perform a search operation.
        Args:
            description (Optional[str]): The description of the knowledge base.
            category (str): The category of the knowledge base.
            name (str): The name of the knowledge base.
            embedding (str): The embedding model to use.

        Supported Embedding Models:
            - jina_embeddings_v2_base_en
            - jina_embeddings_v2_small_en
            - text_embedding_ada_002

        Example:
            contract_id = dria.create(name="History of France",
               embedding="jina_embeddings_v2_base_en",
               category="History",
               description="A knowledge base about the history of France.")

        Returns:
            QueryResponse: The query response.
        """

        sr = CreateIndex(name=name, embedding=embedding.value, category=category, description=description)
        resp = self._api.post("/v1/knowledge/index/create", host=DRIA_UTIL_HOST, payload=sr.to_json())
        return CreateIndexResponse(**resp)

    def search(self, query: str, contract_id: str, top_n: int, model: str,
               field: Optional[str] = None, rerank: Optional[bool] = None, level: Optional[int] = 2):
        """
        Perform a search operation.
        Args:
            query (str): The search query.
            contract_id (str): The contract ID.
            top_n (int): The number of results to retrieve.
            field (Optional[str]): The field to search in (This field only for CSV sourced knowledge bases).
            model (Optional[str]): The search model to use.
            rerank (Optional[bool]): Whether to perform re-ranking.
            level (Optional[int]): The search level.

        Returns:
            QueryResponse: The query response.
        """

        sr = SearchRequest(query=query, contract_id=contract_id, top_n=top_n,
                           field=field, model=model, rerank=rerank, level=level)
        sr.model = sr.model.split("/")[-1] if model is not None else None
        resp = self._api.post(self._root_path + "/search", payload=sr.to_json())
        return [SearchResult(**result).to_dict() for result in resp]

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

        qr = QueryRequest(vector=vector, contract_id=contract_id, top_n=top_n)

        resp = self._api.post(self._root_path + "/query", payload=qr.model_dump())
        return [QueryResult(**result).to_dict() for result in resp]

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

        if "vectors" not in resp or "metadata" not in resp:
            raise DriaParameterError("Invalid Fetch Response from API")

        return [FetchResult(vectors=resp["vectors"][idx],
                            metadata={"id": ids[idx], "metadata": json.loads(result)}).to_json() for idx, result in
                enumerate(resp["metadata"])]

    def batch_insert(self, batch: List[Dict], contract_id: str):
        """
        Batch insert data.

        Args:
            batch (List[Dict]): The batch data to insert. Each dictionary should have "vector" (List[float])
                                and "metadata" (Dict). Maximum size is 1000.
            contract_id (str): The contract ID.

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

                if not all(isinstance(value, str) for value in metadata.values()):
                    raise DriaParameterError("All values under 'metadata' should be strings")

                formatted_batch.append((vector, metadata))
        except KeyError:
            raise DriaParameterError("Batch data must be a list of dictionaries with keys 'vectors' and 'metadata'")

        data = self.__serialize_batch(formatted_batch)
        br = InsertRequest(data=data, contract_id=contract_id, batch_size=len(batch))
        resp = self._api.post(self._root_path_train + "/insert_batch", payload=br.to_json())
        return InsertResponse(**{"message": resp})

    def get_model(self, contract_id: str) -> ModelEnum:
        """
        Get the model of a knowledge base.
        Args:
            contract_id (str): The contract ID.
        Returns:
            str: The model of the knowledge base.
        """
        resp = self._api.get("/v1/knowledge/index/get_model?contract_id=" + contract_id, host=DRIA_UTIL_HOST)

        if "model" not in resp:
            raise DriaParameterError("Invalid response from server")

        def get_enum_member(value) -> ModelEnum:
            for member in ModelEnum:
                if member.value == value["embedding"]:
                    return ModelEnum(member)
            raise DriaParameterError("Unsupported model type")

        return get_enum_member(resp["model"])

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
