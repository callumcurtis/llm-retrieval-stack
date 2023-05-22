import os

from gpt_retrieval.api.model import GetUploadUrlResponse
from gpt_retrieval.utils.aws.s3 import S3ObjectId
from gpt_retrieval.utils.aws.s3 import S3MethodPresigner


UPLOAD_BUCKET_NAME = os.environ['UPLOAD_BUCKET_NAME']
PRESIGNED_URL_LIFETIME = int(os.environ['PRESIGNED_URL_LIFETIME'])

s3_method_presigner = S3MethodPresigner()


def handler(event, context):
    object_key = event['pathParameters']['objectKey']
    object_id = S3ObjectId(bucket=UPLOAD_BUCKET_NAME, key=object_key)
    upload_url = s3_method_presigner.presign(
        S3MethodPresigner.Method.PUT,
        object_id,
        lifetime=PRESIGNED_URL_LIFETIME,
    )
    body = GetUploadUrlResponse(upload_url=upload_url).json(by_alias=True)
    return {
        'statusCode': 200,
        'body': body,
    }