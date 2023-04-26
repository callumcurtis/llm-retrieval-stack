import json
import os

from aws_lambda_powertools import Logger

from utils.aws.s3 import S3ObjectId
from utils.aws.s3 import S3ObjectPartitioner


UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET']
PART_SIZE = int(os.environ['PART_SIZE'])

logger = Logger()
s3_object_partitioner = S3ObjectPartitioner()


@logger.inject_lambda_context()
def handler(event, context):
    sqs_records = event['Records']
    for sqs_record in sqs_records:
        sqs_body = json.loads(sqs_record['body'])

        if 'Event' in sqs_body and sqs_body['Event'] == 's3:TestEvent':
            logger.info('Skipping S3 test event')
            continue

        object_key = sqs_body['Records'][0]['s3']['object']['key']
        object_id = S3ObjectId(UPLOAD_BUCKET, object_key)
        object_part_ids = s3_object_partitioner.iter_part_ids(object_id, PART_SIZE)

        for object_part_id in object_part_ids:
            # TODO: Send object part to SQS
            pass
