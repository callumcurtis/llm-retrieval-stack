import os
from typing import Callable

from llm_retrieval.vector.store import StoredVectorMetadata


class Configuration:

    def __init__(
        self,
        embedding_model_name: str = None,
        vector_store_provider_name: str = None,
        pinecone_environment: str = None,
        pinecone_dimension: int = None,
        pinecone_index_name: str = None,
        pinecone_metadata_type: type = None,
    ):
        self._embedding_model_name = embedding_model_name
        self._vector_store_provider_name = vector_store_provider_name
        self._pinecone_environment = pinecone_environment
        self._pinecone_dimension = pinecone_dimension
        self._pinecone_index_name = pinecone_index_name
        self._pinecone_metadata_type = pinecone_metadata_type
        self._openai_api_key_callback = None
        self._pinecone_api_key_callback = None

    @property
    def embedding_model_name(self) -> str:
        return self._embedding_model_name or os.environ.get("EMBEDDING_MODEL_NAME")

    @embedding_model_name.setter
    def embedding_model_name(self, value: str) -> None:
        self._embedding_model_name = value

    @property
    def vector_store_provider_name(self) -> str:
        return self._vector_store_provider_name or os.environ.get("VECTOR_STORE_PROVIDER_NAME")

    @vector_store_provider_name.setter
    def vector_store_provider_name(self, value: str) -> None:
        self._vector_store_provider_name = value

    @property
    def openai_api_key(self) -> str:
        return self._openai_api_key_callback() if self._openai_api_key_callback else os.environ.get("OPEN_AI_API_KEY")

    def set_openai_api_key_callback(self, callback: Callable[[], str]) -> None:
        self._openai_api_key_callback = callback

    @property
    def pinecone_api_key(self) -> str:
        return self._pinecone_api_key_callback() if self._pinecone_api_key_callback else os.environ.get("PINECONE_API_KEY")

    def set_pinecone_api_key_callback(self, callback: Callable[[], str]) -> None:
        self._pinecone_api_key_callback = callback

    @property
    def pinecone_environment(self) -> str:
        return self._pinecone_environment or os.environ.get("PINECONE_ENVIRONMENT")

    @pinecone_environment.setter
    def pinecone_environment(self, value: str) -> None:
        self._pinecone_environment = value

    @property
    def pinecone_dimension(self) -> int:
        return self._pinecone_dimension or int(os.environ.get("PINECONE_DIMENSION"))

    @pinecone_dimension.setter
    def pinecone_dimension(self, value: int) -> None:
        self._pinecone_dimension = value

    @property
    def pinecone_index_name(self) -> str:
        return self._pinecone_index_name or os.environ.get("PINECONE_INDEX_NAME")

    @pinecone_index_name.setter
    def pinecone_index_name(self, value: str) -> None:
        self._pinecone_index_name = value

    @property
    def pinecone_metadata_type(self) -> type[StoredVectorMetadata]:
        return self._pinecone_metadata_type or StoredVectorMetadata

    @pinecone_metadata_type.setter
    def pinecone_metadata_type(self, value: type[StoredVectorMetadata]) -> None:
        self._pinecone_metadata_type = value
