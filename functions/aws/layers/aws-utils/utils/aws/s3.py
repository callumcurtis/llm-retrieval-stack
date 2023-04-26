from typing import Iterable

import boto3


class S3ObjectId:

    def __init__(self, bucket: str, key: str):
        self.bucket = bucket
        self.key = key

    def to_json(self) -> dict:
        return {
            'bucket': self.bucket,
            'key': self.key
        }

    @classmethod
    def from_json(cls, json: dict) -> 'S3ObjectId':
        return cls(
            json['bucket'],
            json['key'],
        )


class S3ObjectPartId:

    def __init__(self, object_id: S3ObjectId, start: int, end: int):
        self.object_id = object_id
        self.start = start
        self.end = end

    def to_json(self) -> dict:
        return {
            'object': self.object_id.to_json(),
            'start': self.start,
            'end': self.end,
        }

    @classmethod
    def from_json(cls, json: dict) -> 'S3ObjectPartId':
        return cls(
            S3ObjectId.from_json(json['object']),
            json['start'],
            json['end'],
        )


class S3ObjectRetriever:

    def __init__(self, client = None):
        self._client = client or boto3.client('s3')

    def get(
        self,
        object_id: S3ObjectId,
        metadata_only: bool = False,
        **kwargs,
    ) -> dict:
        if metadata_only:
            return self._client.head_object(
                Bucket=object_id.bucket,
                Key=object_id.key,
                **kwargs,
            )
        else:
            return self._client.get_object(
                Bucket=object_id.bucket,
                Key=object_id.key,
                **kwargs,
            )


class S3ObjectPartitioner:

    def __init__(self, retriever: S3ObjectRetriever = None):
        self._retriever = retriever or S3ObjectRetriever()

    def iter_part_ids(
        self,
        object_id: S3ObjectId,
        part_size: int,
    ) -> Iterable[S3ObjectPartId]:
        object_metadata = self._retriever.get(object_id, metadata_only=True)
        object_size = object_metadata['ContentLength']
        for start in range(0, object_size, part_size):
            end = min(start + part_size, object_size)
            yield S3ObjectPartId(object_id, start, end)
