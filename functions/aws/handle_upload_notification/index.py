import json
import os

import boto3


TEXT_PROCESSING_STATE_MACHINE = os.environ['TEXT_PROCESSING_STATE_MACHINE']
UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET']


def handler(event, context):
    object_key = event['Records'][0]['s3']['object']['key']

    s3_client = boto3.client('s3')
    object = s3_client.get_object(Bucket=UPLOAD_BUCKET, Key=object_key)
    object_data = object['Body'].read().decode('utf-8')

    sf_client = boto3.client('stepfunctions')
    sf_client.start_execution(
        stateMachineArn=TEXT_PROCESSING_STATE_MACHINE,
        input=json.dumps({
            'objectKey': object_key,
            'text': object_data,
        }),
    )