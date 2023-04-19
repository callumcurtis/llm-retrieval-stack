import os

import boto3


UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET']


def handler(event, context):
    object_key = event['objectKey']

    s3_client = boto3.client('s3')
    s3_object = s3_client.get_object(Bucket=UPLOAD_BUCKET, Key=object_key)
    s3_object_data = s3_object['Body'].read().decode('utf-8')

    return {
        'objectData': s3_object_data,
    }