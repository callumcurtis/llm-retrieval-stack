import enum

import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential

from gpt_retrieval.embedding.provider.base import EmbeddingProvider


class OpenAIEmbeddingModel(enum.Enum):
    ADA_002 = "text-embedding-ada-002"


OPENAI_EMBEDDING_MODEL_DEFAULT = OpenAIEmbeddingModel.ADA_002
MAX_TEXTS_PER_BATCH = 2048


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        api_key: str,
        engine: str = OPENAI_EMBEDDING_MODEL_DEFAULT,
    ):
        openai.api_key = api_key
        self.engine = engine

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    async def _embed_batch_async(self, texts: list[str]) -> list[list[float]]:
        # The following is taken from openai.embeddings_utils
        # It has been duplicatd here to avoid the heavy dependencies required by openai.embeddings_utils
        assert len(texts) <= MAX_TEXTS_PER_BATCH, f"Batch size should not be larger than {MAX_TEXTS_PER_BATCH}."

        # replace newlines, which can negatively affect performance.
        texts = [text.replace("\n", " ") for text in texts]

        data = (await openai.Embedding.acreate(input=texts, engine=self.engine)).data
        data = sorted(data, key=lambda x: x["index"])  # maintain the same order as input.
        return [d["embedding"] for d in data]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OpenAIEmbeddingProvider):
            return False
        return self.engine == other.engine
