import json
# import os

# import boto3
# from aws_secretsmanager_caching import SecretCacheConfig, SecretCache


# OPENAI_API_KEY_SECRET_NAME = os.environ['OPENAI_API_KEY_SECRET_NAME']
# OPENAI_API_KEY_SECRET_REGION = os.environ['OPENAI_API_KEY_SECRET_REGION']


# def create_secret_cache():
#     client = boto3.client(
#         service_name='secretsmanager',
#         region_name=OPENAI_API_KEY_SECRET_REGION,
#     )
#     secret_cache_config = SecretCacheConfig()
#     secret_cache = SecretCache(config=secret_cache_config, client=client)
#     return secret_cache


# secret_cache = create_secret_cache()


def handler(event, context):
    text = json.loads(event['text'])

    return {
        'vector': "fake-vector"
    }