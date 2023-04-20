from aws_lambda_powertools import Logger


logger = Logger()


@logger.inject_lambda_context()
def handler(event, context):
    vector = event['vector']

    # TODO: specify which vector database is in use
    logger.info('Storing vector')

    return {}