import pinecone
from tenacity import retry, stop_after_attempt, wait_random_exponential

from gpt_retrieval.vector.store import StoredVector
from gpt_retrieval.vector.store import StoredVectorMetadata
from gpt_retrieval.vector.store.provider.base import VectorStoreClient


class PineconeVectorStoreClient(VectorStoreClient):
    UPSERT_BATCH_SIZE = 100
    REQUIRED_METADATA_FIELDS = {}

    def __init__(
        self,
        api_key: str,
        environment: str,
        dimension: int,
        index_name: str,
        metadata_type: type[StoredVectorMetadata],
    ):
        self.metadata_type = metadata_type
        self._verify_metadata_shape()
        self.dimension = dimension
        self.environment = environment
        pinecone.init(api_key=api_key, environment=environment)
        self.index = self._create_or_get_index(index_name)
    
    def _verify_metadata_shape(self):
        metadata_fields = set(self.metadata_type.__fields__.keys())
        assert self.REQUIRED_METADATA_FIELDS.issubset(metadata_fields), f"Metadata must contain the following fields: {self.REQUIRED_METADATA_FIELDS}."

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def _create_or_get_index(self, name: str):
        if name not in pinecone.list_indexes():
            metadata_fields = list(self.metadata_type.__fields__.keys())
            metadata_config = {
                "indexed": metadata_fields,
            }
            pinecone.create_index(
                name,
                dimension=self.dimension,
                metadata_config=metadata_config,
            )
        return pinecone.Index(name)

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    async def _upsert_batch_async(self, vectors: list[StoredVector]) -> None:
        assert len(vectors) <= self.UPSERT_BATCH_SIZE, f"Batch size should not be larger than {self.UPSERT_BATCH_SIZE}."
        payload = [(v.id, v.vector, v.metadata.dict()) for v in vectors]
        self.index.upsert(payload)
