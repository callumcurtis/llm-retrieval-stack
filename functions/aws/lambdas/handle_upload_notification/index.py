import json
import os

import boto3
from aws_lambda_powertools import Logger

from utils.chunk import EncodedChunkStream
from utils.chunk import DecodedChunkStreamSplitWordHealer
from utils.chunk import DecodedChunkStreamResizerByNumTokens


TEXT_PROCESSING_STATE_MACHINE = os.environ['TEXT_PROCESSING_STATE_MACHINE']
UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET']

MAX_CHUNK_SIZE_BYTES = 500

logger = Logger()
s3_client = boto3.client('s3')
sf_client = boto3.client('stepfunctions')


@logger.inject_lambda_context()
def handler(event, context):
    sqs_records = event['Records']
    for sqs_record in sqs_records:
        sqs_body = json.loads(sqs_record['body'])

        if 'Event' in sqs_body and sqs_body['Event'] == 's3:TestEvent':
            logger.info('Skipping S3 test event')
            continue

        object_key = sqs_body['Records'][0]['s3']['object']['key']
        object = s3_client.get_object(Bucket=UPLOAD_BUCKET, Key=object_key)

        text_stream = object['Body'].iter_chunks(MAX_CHUNK_SIZE_BYTES)
        text_stream = EncodedChunkStream().append_wrapped(text_stream, encoding='utf-8', start=0)
        text_stream = text_stream.decode()
        text_stream = DecodedChunkStreamSplitWordHealer(text_stream)
        text_stream = DecodedChunkStreamResizerByNumTokens(text_stream)

        logger.info('Dispatching text for processing', objectKey=object_key)

        for text_chunk in text_stream:
            sf_client.start_execution(
                stateMachineArn=TEXT_PROCESSING_STATE_MACHINE,
                input=json.dumps({
                    'objectKey': object_key,
                    'text': text_chunk,
                }),
            )