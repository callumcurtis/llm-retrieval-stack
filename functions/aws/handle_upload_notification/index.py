import json
import os

import boto3


PROCESS_UPLOADED_OBJECTS_STATE_MACHINE = os.environ['PROCESS_UPLOADED_OBJECTS_STATE_MACHINE']


def handler(event, context):
    s3_object_key = event['Records'][0]['s3']['object']['key']

    sf_client = boto3.client('stepfunctions')
    sf_client.start_execution(
        stateMachineArn=PROCESS_UPLOADED_OBJECTS_STATE_MACHINE,
        input=json.dumps({'objectKey': s3_object_key}),
    )