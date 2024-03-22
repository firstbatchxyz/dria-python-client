import json
from typing import List, Dict, Optional, Union

from dria.constants import DRIA_HOST, DRIA_HNSW_ROOT, DRIA_UTIL_HOST, DRIA_HNSW_ROOT_TRAIN, DRIA_HOST_TRAIN
from dria.core.api.api import API
from dria.core.proto.serialization import ProtoBufConverter
from dria.exceptions import DriaParameterError
from dria.models import SearchRequest, SearchResult, QueryResult
from dria.models.models import FetchRequest, InsertResponse, Models, CreateIndex, CreateIndexResponse, \
    QueryRequest, FetchResult, TextInsertRequest, VectorInsertRequest, ListContracts, Entry


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
        self._converter = ProtoBufConverter()

    def create(self, name: str, embedding: Union[Models, str], category: str,
               description: Optional[str] = None):
        """
        Perform a create index operation.
        Args:
            description (Optional[str]): The description of the knowledge base.
            category (str): The category of the knowledge base.
            name (str): The name of the knowledge base.
            embedding (Union[Models, str]): The embedding model to use.

        Supported Embedding Models:
            - jina_embeddings_v2_base_en
            - jina_embeddings_v2_small_en
            - text_embedding_ada_002
            - text_embedding_3_small
            - text_embedding_3_large

        Example:
            contract_id = dria.create(name="History of France",
               embedding="jina_embeddings_v2_base_en",
               category="History",
               description="A knowledge base about the history of France.")

        Returns:
            QueryResponse: The query response.
        """
        if isinstance(embedding, Models):
            embedding = embedding.value
        sr = CreateIndex(name=name, embedding=embedding, category=category, description=description)
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
        resp = self._api.post(self._root_path + "/search", payload=sr.to_json())
        return [SearchResult(id=result["id"], score=result["score"],
                             metadata=(result["metadata"]
                                       if rerank else json.loads(result["metadata"]))).to_dict() for result in
                resp]

    def query(self, vector: List[float], contract_id: str, top_n: int = 10, level: int = 2):
        """
        Perform a query operation.
        Args:
            vector (List[float]): The query vector.
            contract_id (str): The contract ID.
            top_n (int): The number of results to retrieve.
            level (int): The search level.

        Example:
            dria.query([0.1, 0.2, 0.3], "<CONTRACT_ID>", top_n=10)

        Returns:
            QueryResult: The query response.
        """

        qr = QueryRequest(vector=vector, contract_id=contract_id, top_n=top_n, level=level)

        resp = self._api.post(self._root_path + "/query", payload=qr.model_dump())
        return [QueryResult(**{"id": result["id"], "score": result["score"],
                               "metadata": json.loads(result["metadata"])}).to_dict() for result in resp]

    def fetch(self, ids: List[int], contract_id: str):
        """
        Fetch data for a list of IDs.
        Args:
            ids (List[int]): The list of IDs to fetch.
            contract_id (str): The contract ID.

        Example:
            dria.fetch([1, 2, 3], "<CONTRACT_ID>")

        Returns:
            FetchResult: The fetch result.
        """

        if not ids:
            raise DriaParameterError("No IDs provided")

        fr = FetchRequest(contract_id=contract_id, id=ids)

        resp = self._api.post(self._root_path + "/fetch", payload=fr.model_dump())

        if "vectors" not in resp or "metadata" not in resp:
            raise DriaParameterError("Invalid Fetch Response from API")

        return [FetchResult(vectors=resp["vectors"][idx],
                            metadata={"id": ids[idx], "metadata": json.loads(result)}).to_json() for idx, result in
                enumerate(resp["metadata"])]

    def remove(self, contract_id: str):
        """
        Remove a knowledge base.
        Args:
            contract_id (str): The contract ID.

        Example:
            dria.remove("<CONTRACT_ID>")

        Returns: The response from the remove operation.

        """

        resp = self._api.post("/v1/knowledge/remove", payload={"contract_id": contract_id}, host=DRIA_UTIL_HOST)
        return resp

    def batch_vector_insert(self, batch: List[Dict], write_blockchain: bool, contract_id: str):
        """
        Batch insert data.

        Args:
            batch (List[Dict]): The batch data to insert. Each dictionary should have "vector" (List[float])
                                and "metadata" (Dict). Maximum size is 1000.
            write_blockchain (bool): Whether to write to the blockchain.
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

                if not all(isinstance(value, (str, float, int, bool)) for value in metadata.values()):
                    raise DriaParameterError("All values under 'metadata' should be string, float, int or bool")

                formatted_batch.append((vector, metadata))
        except KeyError:
            raise DriaParameterError("Batch data must be a list of dictionaries with keys 'vector' and 'metadata'")

        data = self._converter.serialize_batch_vec(formatted_batch)
        br = VectorInsertRequest(data=data, write_blockchain=write_blockchain,
                                 contract_id=contract_id, batch_size=len(batch))
        resp = self._api.post(self._root_path_train + "/insert_vector", payload=br.to_json(), host=DRIA_HOST_TRAIN)
        return InsertResponse(**{"message": resp})

    def batch_text_insert(self, batch: List[Dict], write_blockchain: bool, model: Union[Models, str], contract_id: str):
        """
        Batch insert with text data.

        Args:
            batch (List[Dict]): The batch data to insert. Each dictionary should have "text" (str)
                                and "metadata" (Dict). Maximum size is 1000.
            write_blockchain (bool): Whether to write to the blockchain.
            model (Union[Models, str]): The embedding model to use.
            contract_id (str): The contract ID.

        Returns:
            InsertResponse: The response from the batch insert operation.

        Raises:
            ValueError: If the batch size exceeds the maximum limit (1000), if the format of the batch is invalid,
                        or if any value under "metadata" is not a string.
        """

        if len(batch) > 1000:
            raise DriaParameterError("Batch size exceeds the maximum limit of 1000")
        batch = [item for item in batch if item["text"] != ""]
        try:
            formatted_batch = []
            for item in batch:
                text = item["text"]
                metadata = item["metadata"]

                if not all(isinstance(value, (str, float, int, bool)) for value in metadata.values()):
                    raise DriaParameterError("All values under 'metadata' should be string, float, int or bool")

                formatted_batch.append((text, metadata))
        except KeyError:
            raise DriaParameterError("Batch data must be a list of dictionaries with keys 'text' and 'metadata'")

        data = self._converter.serialize_batch_str(formatted_batch)
        br = TextInsertRequest(data=data, write_blockchain=write_blockchain,
                               model=model, contract_id=contract_id, batch_size=len(batch))
        resp = self._api.post(self._root_path_train + "/insert_text", payload=br.to_json(), host=DRIA_HOST_TRAIN)
        return InsertResponse(**{"message": resp})

    def get_model(self, contract_id: str) -> Union[Models, str]:
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

        def get_enum_member(value) -> Models:
            for member in Models:
                if member.value == value:
                    return Models(member)
            return value

        return get_enum_member(resp["model"])

    def list_contracts(self) -> Dict:
        """
        Get a list of all knowledge bases.

        Returns:
            ListContracts: A response containing the contract id list.
        """
        resp = self._api.get("/v1/knowledge/list", host=DRIA_UTIL_HOST)
        return ListContracts(**resp).model_dump()

    def get_contract(self, contract_id: str):
        """
        Get the contract details.

        Args:
            contract_id (str): The contract ID.

        Returns:
            ContractResponse: A response containing the contract details.
        """
        resp = self._api.get("/v1/knowledge/get_knowledge_base?contract_id=" + contract_id, host=DRIA_UTIL_HOST)
        return resp

    def get_entry_count(self, contract_id: str):
        """
        Get the number of entries in the knowledge base.

        Args:
            contract_id (str): The contract ID.

        Returns:

        """
        resp = self._api.post(self._root_path + "/entry_count", payload={"contract_id": contract_id}, host=DRIA_HOST)
        return Entry(**resp).model_dump()

    def update_knowledge_base(self, contract_id: str, **kwargs):
        """
        Update a knowledge base in Dria.

        Args:
            contract_id (str): The contract ID of the knowledge base to update.
            **kwargs: The fields to update.

        Returns:
            dict: A response containing the updated knowledge base definition.

        """

        knowledge_definition = {}

        if 'name' in kwargs:
            knowledge_definition['name'] = kwargs['name']
        if 'description' in kwargs:
            knowledge_definition['description'] = kwargs['description']
        if 'category' in kwargs:
            knowledge_definition['category'] = kwargs['category']

        if knowledge_definition == {}:
            raise DriaParameterError("No fields to update")

        knowledge_definition['contract_id'] = contract_id
        response = self._api.post("/v1/knowledge/index/update",
                                  payload=knowledge_definition, host=DRIA_UTIL_HOST)
        return response
