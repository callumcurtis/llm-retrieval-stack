import enum
from typing import Iterable

import boto3
import pydantic


class S3ObjectId(pydantic.BaseModel):
    bucket: str
    key: str


class S3ObjectPartId(pydantic.BaseModel):
    object_id: S3ObjectId = pydantic.Field(alias='objectId')
    start: int
    end: int

    class Config:
        allow_population_by_field_name = True


class S3MethodPresigner:

    DEFAULT_LIFETIME = 120

    class Method(enum.Enum):
        PUT = 'put_object'
        GET = 'get_object'

    def __init__(self, client = None):
        self._client = client or boto3.client('s3')

    def presign(
        self,
        method: Method,
        object_id: S3ObjectId,
        lifetime: int = DEFAULT_LIFETIME,
        **kwargs,
    ) -> str:
        return self._client.generate_presigned_url(
            ClientMethod=method.value,
            Params={
                'Bucket': object_id.bucket,
                'Key': object_id.key,
            },
            ExpiresIn=lifetime,
            **kwargs,
        )


class S3ObjectReader:

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

    def __init__(self, reader: S3ObjectReader = None):
        self._reader = reader or S3ObjectReader()

    def iter_part_ids(
        self,
        object_id: S3ObjectId,
        part_size: int,
    ) -> Iterable[S3ObjectPartId]:
        object_metadata = self._reader.get(object_id, metadata_only=True)
        object_size = object_metadata['ContentLength']
        for start in range(0, object_size, part_size):
            end = min(start + part_size, object_size)
            yield S3ObjectPartId(object_id=object_id, start=start, end=end)


class S3ObjectPartReader:

    def __init__(self, reader: S3ObjectReader = None):
        self._reader = reader or S3ObjectReader()

    def get(
        self,
        object_part_id: S3ObjectPartId,
        **kwargs,
    ) -> dict:
        return self._reader.get(
            object_part_id.object_id,
            Range=f'bytes={object_part_id.start}-{object_part_id.end - 1}',
            **kwargs,
        )
