import boto3
import pydantic


class SqsQueueId(pydantic.BaseModel):
    url: str


class SqsMessageSenderError(Exception):
    
        def __init__(self, sender_errors: list):
            self.sender_errors = sender_errors
        
        def __str__(self):
            return f'{self.__class__.__name__}: {self.sender_errors}'
        
        def __repr__(self):
            return f'{self.__class__.__name__}({self.sender_errors})'


class SqsMessageSender:

    def __init__(self, client = None):
        self._client = client or boto3.client('sqs')

    def send(
        self,
        queue_id: SqsQueueId,
        message: str,
        **kwargs,
    ) -> dict:
        return self._client.send_message(
            QueueUrl=queue_id.url,
            MessageBody=message,
            **kwargs,
        )

    def send_batch(
        self,
        queue_id: SqsQueueId,
        entries: list,
        **kwargs,
    ) -> dict:
        """Send a batch of messages to a queue.

        See the boto3 documentation for the format of the entries list.

        Args:
            queue_id: The queue to send the messages to.
            entries: A list of entries to send.
            **kwargs: Additional arguments to pass to the batch send method.

        Raises:
            SqsMessageSenderError: If any of the entries failed to send due to a sender error.
        """
        response = self._client.send_message_batch(
            QueueUrl=queue_id.url,
            Entries=entries,
            **kwargs,
        )
        self._raise_on_sender_error(response)
        return response

    def _raise_on_sender_error(
        self,
        response: dict,
    ) -> None:
        failed = response.get('Failed')
        if failed:
            sender_errors = [e for e in failed if e['SenderFault']]
            if sender_errors:
                raise SqsMessageSenderError(sender_errors)
