import pytest

from dria import DriaParameterError
from dria.core.proto.serialization import ProtoBufConverter
from dria_test.utils.utils import expect_vectors_to_be_close, random_vector

proto = ProtoBufConverter()


@pytest.mark.parametrize("data", [
    [
        {"metadata": {"foo": "bar1", "age": 20, "score": 0.12345, "is": True}, "text": "I am a test data."},
        {"metadata": {"foo": "bar2", "age": 40, "score": 0.98765, "is": False}, "text": "I am another test data."},
    ]
])
def test_batch_texts_encode_decode(data):
    enc = proto.serialize_batch_str(data)
    assert isinstance(enc, str), "Encoded data should be a string"

    dec = proto.deserialize_batch_str(enc)
    for d, original in zip(dec, data):
        assert d["text"] == original["text"], "Texts do not match"
        for key in original["metadata"]:
            if isinstance(original["metadata"][key], float):
                assert pytest.approx(d["metadata"][key]) == original["metadata"][key], f"Metadata {key} does not match"
            else:
                assert d["metadata"][key] == original["metadata"][key], f"Metadata {key} does not match"


def test_batch_texts_encode_decode_without_metadata():
    data = [{"metadata": {}, "text": "ABC"}]
    enc = proto.serialize_batch_str(data)
    assert isinstance(enc, str), "Encoded data should be a string"

    dec = proto.deserialize_batch_str(enc)
    assert len(dec) == 1, "Decoded list should contain one item"
    assert dec[0]["metadata"] == {}, "Metadata should be empty"
    assert dec[0]["text"] == data[0]["text"], "Texts do not match"


def test_batch_texts_not_encode_empty_text():
    data = [{"metadata": {}, "text": ""}]
    with pytest.raises(DriaParameterError, match="Can't encode empty text."):
        proto.serialize_batch_str(data)


@pytest.mark.parametrize("dim", [64])
def test_batch_vectors_encode_decode(dim):
    data = [
        {"metadata": {"foo": "bar1", "age": 20, "score": 0.12345, "is": True}, "vector": random_vector(dim)},
        {"metadata": {"foo": "bar2", "age": 40, "score": 0.98765, "is": False}, "vector": random_vector(dim)},
    ]
    enc = proto.serialize_batch_vec(data)
    assert isinstance(enc, str), "Encoded data should be a string"

    dec = proto.deserialize_batch_vec(enc)
    for d, original in zip(dec, data):
        expect_vectors_to_be_close(d["vector"], original["vector"])
        for key in original["metadata"]:
            if isinstance(original["metadata"][key], float):
                assert pytest.approx(d["metadata"][key]) == original["metadata"][key], f"Metadata {key} does not match"
            else:
                assert d["metadata"][key] == original["metadata"][key], f"Metadata {key} does not match"


def test_batch_vectors_encode_decode_without_metadata():
    data = [{"metadata": {}, "vector": [1, 2, 3, 4, 5]}]
    enc = proto.serialize_batch_vec(data)
    assert isinstance(enc, str), "Encoded data should be a string"

    dec = proto.deserialize_batch_vec(enc)
    assert len(dec) == 1, "Decoded list should contain one item"
    assert dec[0]["metadata"] == {}, "Metadata should be empty"
    assert dec[0]["vector"] == data[0]["vector"], "Vectors do not match"


def test_batch_vectors_not_encode_empty_vector():
    data = [{"metadata": {}, "vector": []}]
    with pytest.raises(DriaParameterError, match="Can't encode empty vector."):
        proto.serialize_batch_vec(data)
