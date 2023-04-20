import os
import json

import boto3


UPLOAD_BUCKET_NAME = os.environ['UPLOAD_BUCKET']

s3_client = boto3.client('s3')


def create_presigned_url(client_method, bucket_name, object_key, expiration=120):
    return s3_client.generate_presigned_url(
        ClientMethod=client_method,
        Params={
            'Bucket': bucket_name,
            'Key': object_key
        },
        ExpiresIn=expiration
    )


def handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'uploadUrl': create_presigned_url('put_object', UPLOAD_BUCKET_NAME, event['pathParameters']['objectKey'])
        })
    }