import os
import json

import boto3


UPLOAD_BUCKET_NAME = os.environ['UPLOAD_BUCKET']


def create_presigned_url(client_method, bucket_name, object_name, expiration=120):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    s3_client = boto3.client('s3')
    return s3_client.generate_presigned_url(
        ClientMethod=client_method,
        Params={
            'Bucket': bucket_name,
            'Key': object_name
        },
        ExpiresIn=expiration
    )


def handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'uploadUrl': create_presigned_url('put_object', UPLOAD_BUCKET_NAME, event['pathParameters']['objectName'])
        })
    }