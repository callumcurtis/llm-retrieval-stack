import json
import os

import boto3
from aws_lambda_powertools import Logger


TEXT_PROCESSING_STATE_MACHINE = os.environ['TEXT_PROCESSING_STATE_MACHINE']
UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET']

logger = Logger()
s3_client = boto3.client('s3')
sf_client = boto3.client('stepfunctions')


@logger.inject_lambda_context()
def handler(event, context):
    sqs_records = event['Records']
    for sqs_record in sqs_records:
        sqs_body = json.loads(sqs_record['body'])
        object_key = sqs_body['Records'][0]['s3']['object']['key']

        logger.info(object_key=object_key)

        object = s3_client.get_object(Bucket=UPLOAD_BUCKET, Key=object_key)
        object_data = object['Body'].read().decode('utf-8')

        sf_client.start_execution(
            stateMachineArn=TEXT_PROCESSING_STATE_MACHINE,
            input=json.dumps({
                'objectKey': object_key,
                'text': object_data,
            }),
        )