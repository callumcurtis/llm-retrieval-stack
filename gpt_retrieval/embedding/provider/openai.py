import enum

import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential

from gpt_retrieval.embedding import Embedding
from gpt_retrieval.embedding.provider.base import EmbeddingClient


class OpenAIEmbeddingModel(enum.Enum):
    ADA_002 = "text-embedding-ada-002"


class OpenAIEmbeddingClient(EmbeddingClient):
    EMBED_BATCH_SIZE = 2048

    def __init__(
        self,
        api_key: str,
        engine: str,
    ):
        openai.api_key = api_key
        self.engine = engine

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    async def _embed_batch_async(self, texts: list[str]) -> list[Embedding]:
        # The following is taken from openai.embeddings_utils
        # It has been duplicatd here to avoid the heavy dependencies required by openai.embeddings_utils
        assert len(texts) <= self.EMBED_BATCH_SIZE, f"Batch size should not be larger than {self.EMBED_BATCH_SIZE}."

        # replace newlines, which can negatively affect performance.
        texts = [text.replace("\n", " ") for text in texts]

        data = (await openai.Embedding.acreate(input=texts, engine=self.engine)).data
        data = sorted(data, key=lambda x: x["index"])  # maintain the same order as input.
        return [d["embedding"] for d in data]
