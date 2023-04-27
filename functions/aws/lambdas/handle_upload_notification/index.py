import json
import os

from aws_lambda_powertools import Logger

from gpt_retrieval.utils.common.iterable import batched
from gpt_retrieval.utils.aws.s3 import S3ObjectId
from gpt_retrieval.utils.aws.s3 import S3ObjectPartitioner
from gpt_retrieval.utils.aws.sqs import SqsQueueId
from gpt_retrieval.utils.aws.sqs import SqsMessageSender


UPLOAD_BUCKET_NAME = os.environ['UPLOAD_BUCKET_NAME']
PART_SIZE = int(os.environ['PART_SIZE'])
UNPROCESSED_OBJECT_PART_QUEUE_URL = os.environ['UNPROCESSED_OBJECT_PART_QUEUE_URL']
OBJECT_PART_IDS_PER_BATCH = 10

logger = Logger()
s3_object_partitioner = S3ObjectPartitioner()
sqs_queue_id = SqsQueueId(UNPROCESSED_OBJECT_PART_QUEUE_URL)
sqs_message_sender = SqsMessageSender()


@logger.inject_lambda_context()
def handler(event, context):
    sqs_records = event['Records']
    for sqs_record in sqs_records:
        sqs_body = json.loads(sqs_record['body'])

        if 'Event' in sqs_body and sqs_body['Event'] == 's3:TestEvent':
            logger.info('Skipping S3 test event')
            continue

        object_key = sqs_body['Records'][0]['s3']['object']['key']
        object_id = S3ObjectId(UPLOAD_BUCKET_NAME, object_key)
        object_part_ids = s3_object_partitioner.iter_part_ids(object_id, PART_SIZE)

        for object_part_id_batch in batched(object_part_ids, OBJECT_PART_IDS_PER_BATCH):
            logger.info(
                'Sending batch of object part IDs to SQS',
                batch_size=len(object_part_id_batch),
            )
            sqs_message_sender.send_batch(
                sqs_queue_id,
                [
                    {
                        'Id': str(i),
                        'MessageBody': json.dumps(object_part_id.to_json()),
                    }
                    for i, object_part_id in enumerate(object_part_id_batch)
                ],
            )
