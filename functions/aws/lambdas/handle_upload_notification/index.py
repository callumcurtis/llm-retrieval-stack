import json
import os

import boto3
from aws_lambda_powertools import Logger

from utils.chunk import wrap_raw_encoded_chunk_stream
from utils.chunk import encoded_to_decoded_chunk_stream
from utils.chunk import resize_decoded_chunks_in_stream_by_num_tokens


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
        text_stream = wrap_raw_encoded_chunk_stream(text_stream, 'utf-8')
        text_stream = encoded_to_decoded_chunk_stream(text_stream)
        text_stream = resize_decoded_chunks_in_stream_by_num_tokens(text_stream)

        logger.info('Dispatching text for processing', objectKey=object_key)

        for text_chunk in text_stream:
            sf_client.start_execution(
                stateMachineArn=TEXT_PROCESSING_STATE_MACHINE,
                input=json.dumps({
                    'objectKey': object_key,
                    'text': text_chunk,
                }),
            )