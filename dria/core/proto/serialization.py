import base64
import dria.core.proto.vector_pb2 as insert_buffer
from typing import List, Tuple, Dict, Any


class ProtoBufConverter:

    @staticmethod
    def dict_to_metadata_value(value: Any):
        metadata_value = insert_buffer.MetadataValue()
        if isinstance(value, float):
            metadata_value.float_value = value
        elif isinstance(value, int):
            metadata_value.int_value = value
        elif isinstance(value, str):
            metadata_value.string_value = value
        elif isinstance(value, bool):
            metadata_value.bool_value = value
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
        return metadata_value

    @staticmethod
    def metadata_value_to_dict(metadata_value: insert_buffer.MetadataValue):
        if metadata_value.HasField("float_value"):
            return metadata_value.float_value
        elif metadata_value.HasField("int_value"):
            return metadata_value.int_value
        elif metadata_value.HasField("string_value"):
            return metadata_value.string_value
        elif metadata_value.HasField("bool_value"):
            return metadata_value.bool_value
        else:
            raise ValueError("Unsupported MetadataValue")

    @staticmethod
    def serialize_batch_vec(batch: List[Tuple[List[float], Dict[str, Any]]]) -> str:
        batch_vec = insert_buffer.BatchVec()
        for vec, metadata in batch:
            singleton_vec = insert_buffer.SingletonVec(v=vec)
            for key, value in metadata.items():
                metadata_value = ProtoBufConverter.dict_to_metadata_value(value)
                singleton_vec.map[key].CopyFrom(metadata_value)
            batch_vec.s.append(singleton_vec)

        # Serialize the BatchVec
        temp = batch_vec.SerializeToString()
        base64_encoded_data = base64.b64encode(temp)
        base64_string = base64_encoded_data.decode('utf-8')
        return base64_string


    @staticmethod
    def deserialize_batch_vec(base64_string: str) -> List[Tuple[List[float], Dict[str, Any]]]:
        # Decode the base64 string to bytes and deserialize to BatchVec
        base64_bytes = base64_string.encode('utf-8')
        serialized_batch_vec = base64.b64decode(base64_bytes)
        batch_vec = insert_buffer.BatchVec()
        batch_vec.ParseFromString(serialized_batch_vec)

        # Process each SingletonVec in the BatchVec
        result_batch = []
        for singleton_vec in batch_vec.s:
            vec = singleton_vec.v
            metadata = {key: ProtoBufConverter.metadata_value_to_dict(value) for key, value in singleton_vec.map.items()}
            result_batch.append((vec, metadata))

    @staticmethod
    def serialize_batch_str(batch: List[Tuple[str, Dict[str, Any]]]) -> str:
        batch_vec = insert_buffer.BatchStr()
        for text, metadata in batch:
            singleton_str = insert_buffer.SingletonStr(v=text)
            for key, value in metadata.items():
                metadata_value = ProtoBufConverter.dict_to_metadata_value(value)
                singleton_str.map[key].CopyFrom(metadata_value)
            batch_vec.s.append(singleton_str)

        # Serialize the BatchVec
        temp = batch_vec.SerializeToString()
        base64_encoded_data = base64.b64encode(temp)
        base64_string = base64_encoded_data.decode('utf-8')
        return base64_string

    @staticmethod
    def deserialize_batch_str(base64_string: str) -> List[Tuple[str, Dict[str, Any]]]:
        # Decode the base64 string to bytes and deserialize to BatchVec
        base64_bytes = base64_string.encode('utf-8')
        serialized_batch_str = base64.b64decode(base64_bytes)
        batch_str = insert_buffer.BatchStr()
        batch_str.ParseFromString(serialized_batch_str)

        # Process each SingletonVec in the BatchVec
        result_batch = []
        for singleton_str in batch_str.s:
            text = singleton_str.v
            metadata = {key: ProtoBufConverter.metadata_value_to_dict(value) for key, value in
                        singleton_str.map.items()}
            result_batch.append((text, metadata))

        return result_batch

