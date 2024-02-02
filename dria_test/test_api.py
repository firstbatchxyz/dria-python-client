import pytest
from pydantic import ValidationError

from dria import Dria, DriaParameterError, Models
from dria_test.utils.utils import random_vector

dria = Dria(api_key="<API_KEY>",
            contract_id="<CONTRACT_ID>")


def test_fetch_vectors_with_given_ids():
    ids = [0, 1, 2]
    res = dria.fetch(ids)
    for r in res:
        assert isinstance(r["metadata"]['id'], str)
        assert isinstance(r["metadata"]['text'], str)


def test_fetch_without_ids_raises_error():
    with pytest.raises(DriaParameterError) as exc_info:
        dria.fetch([])
    assert "No IDs provided" in str(exc_info.value)


def test_fetch_without_contract_id_raises_error():
    dria.contract_id = None
    with pytest.raises(DriaParameterError) as exc_info:
        print(dria.contract_id)
        dria.fetch([0])
    assert "ContractID was not set" in str(exc_info.value)
    dria.contract_id = dria.contract_id  # Reset after the test


def test_search_with_text():
    text = "What is a Union type?"
    res = dria.search(text)
    assert len(res) == 10  # Assuming default top_n is 10
    for r in res:
        assert isinstance(r['id'], int)
        assert r['score'] > 0
        assert isinstance(r['metadata'], str)


def test_search_with_custom_parameters():
    top_n = 5
    text = "What is a Union type?"
    res = dria.search(text, rerank=False, level=1, top_n=top_n)
    assert len(res) == top_n
    for r in res:
        assert isinstance(r['id'], int)
        assert r['score'] > 0
        assert isinstance(r['metadata'], str)


def test_search_with_wrong_topn_raises_error():
    with pytest.raises(ValidationError):
        dria.search("hi", top_n=21)
    with pytest.raises(ValidationError):
        dria.search("hi", top_n=10.05)
    with pytest.raises(ValidationError):
        dria.search("hi", top_n=0)


def test_search_with_wrong_level_raises_error():
    with pytest.raises(DriaParameterError):
        dria.search("hi", level=5)
    with pytest.raises(DriaParameterError):
        dria.search("hi", level=2.5)
    with pytest.raises(DriaParameterError):
        dria.search("hi", level=-1)


def test_query_with_vector():
    vector = random_vector(768)
    res = dria.query(vector)
    assert len(res) == 10  # default top_n
    for r in res:
        assert isinstance(r['id'], int)
        assert isinstance(r['score'], float)
        assert 'id' in r['metadata']
        assert 'text' in r['metadata']


def test_query_with_custom_parameters():
    top_n = 5
    vector = random_vector(768)
    res = dria.query(vector, top_n=top_n)
    assert len(res) == top_n
    for r in res:
        assert isinstance(r['id'], int)
        assert isinstance(r['score'], float)
        assert 'id' in r['metadata']
        assert 'text' in r['metadata']


def test_query_with_wrong_top_n_raises_error():
    with pytest.raises(DriaParameterError):
        dria.query(random_vector(768), top_n=10.05)


def test_insert_texts():
    # This will require modification based on how your API handles text insertion and its success response
    texts = [
        {"text": "I am an inserted text.", "metadata": {"id": "112233", "info": "Test_1"}},
        {"text": "I am another inserted text.", "metadata": {"id": "223344", "info": "Test_2"}}
    ]
    res = dria.insert_text(texts)
    assert res == "Values are successfully added to index."


def test_insert_too_many_texts_at_once_raises_error():
    texts = [{"text": "foo", "metadata": {}} for _ in range(1001)]
    with pytest.raises(DriaParameterError):
        dria.insert_vector(texts)


def test_insert_vectors():
    vectors = [
        {"vector": random_vector(768), "metadata": {"id": "112233", "info": "Test_1"}},
        {"vector": random_vector(768), "metadata": {"id": "223344", "info": "Test_2"}}
    ]
    res = dria.insert_vector(vectors)
    assert res == "Values are successfully added to index."


def test_insert_too_many_vectors_at_once_raises_error():
    vectors = [{"vector": random_vector(3), "metadata": {}} for _ in range(1001)]
    with pytest.raises(DriaParameterError):
        dria.insert_vector(vectors)

