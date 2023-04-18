import os
import logging

import boto3
from botocore.exceptions import ClientError


UPLOAD_BUCKET_NAME = os.environ['UPLOAD_BUCKET']


def create_presigned_url(bucket_name, object_name, expiration=120):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    s3_client = boto3.client('s3')
    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name
            },
            ExpiresIn=expiration
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return presigned_url


def handler(event, context):
    return {
        'statusCode': 200,
        'body': {
            'UPLOAD_BUCKET': UPLOAD_BUCKET_NAME,
            'UPLOAD_URL': create_presigned_url(UPLOAD_BUCKET_NAME, event["object_name"])
        }
    }