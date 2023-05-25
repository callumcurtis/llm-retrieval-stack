import json
import os

from aws_lambda_powertools import Logger

from gpt_retrieval.utils.aws.s3 import S3ObjectPartId
from gpt_retrieval.utils.aws.s3 import S3ObjectPartReader
from gpt_retrieval.utils.aws.secrets import SecretsReader
from gpt_retrieval.configuration import Configuration
from gpt_retrieval.document.chunk.stream import EncodedChunkStream
from gpt_retrieval.document.chunk.stream.conversion import EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing
from gpt_retrieval.document.chunk.stream.transformation import DecodedChunkStreamSplitWordHealer
from gpt_retrieval.document.chunk.stream.transformation import DecodedChunkStreamResizerByNumTokens
from gpt_retrieval.document.chunk.stream.processing import embed_and_upsert_decoded_chunk_stream
from gpt_retrieval.vector.store import StoredVectorMetadata
from gpt_retrieval.embedding.factory import get_embedding_client
from gpt_retrieval.vector.store.factory import get_vector_store_client


CHUNK_SIZE = int(os.environ['CHUNK_SIZE'])
MAX_CONCURRENT_BATCHES = int(os.environ['MAX_CONCURRENT_BATCHES'])
OPENAI_API_KEY_SECRET_ARN = os.environ['OPENAI_API_KEY_SECRET_ARN']
PINECONE_API_KEY_SECRET_ARN = os.environ['PINECONE_API_KEY_SECRET_ARN']


logger = Logger()

s3_object_part_reader = S3ObjectPartReader()

secrets_reader = SecretsReader()
configuration = Configuration()
configuration.set_openai_api_key_callback(lambda: secrets_reader.get_secret_string(OPENAI_API_KEY_SECRET_ARN))
configuration.set_pinecone_api_key_callback(lambda: secrets_reader.get_secret_string(PINECONE_API_KEY_SECRET_ARN))

embedding_client = get_embedding_client(configuration)
vector_store_client = get_vector_store_client(configuration)


@logger.inject_lambda_context()
def handler(event, context):
    sqs_records = event['Records']
    for sqs_record in sqs_records:
        sqs_body = json.loads(sqs_record['body'])

        object_part_id = S3ObjectPartId.parse_raw(sqs_body)

        logger.info('Processing unprocessed object part', object_part_id=object_part_id)

        object_part = s3_object_part_reader.get(object_part_id)

        encoded_chunk_stream = object_part['Body'].iter_chunks(CHUNK_SIZE)
        # TODO: add support for other encodings
        # TODO: add text extraction for PDFs, images, etc.
        encoded_chunk_stream = EncodedChunkStream('utf-8').append_wrapped(encoded_chunk_stream, start=object_part_id.start)
        decoded_chunk_stream = EncodedToDecodedChunkStreamConverterWithSplitCharacterHealing().decode(encoded_chunk_stream)
        decoded_chunk_stream = DecodedChunkStreamSplitWordHealer(decoded_chunk_stream)
        decoded_chunk_stream = DecodedChunkStreamResizerByNumTokens(decoded_chunk_stream)

        try:
            embed_and_upsert_decoded_chunk_stream(
                decoded_chunk_stream=decoded_chunk_stream,
                vector_prefixes=f"{object_part_id.object_id.bucket}/{object_part_id.object_id.key}",
                metadata=StoredVectorMetadata(),
                embedding_client=embedding_client,
                vector_store_client=vector_store_client,
                max_concurrent_batches=MAX_CONCURRENT_BATCHES,
            )
        except UnicodeDecodeError:
            logger.exception("Failed to decode unprocessed object part", object_part_id=object_part_id)
            raise

        logger.info('Successfully processed unprocessed object part', object_part_id=object_part_id)
