import boto3
import aws_secretsmanager_caching as secret_caching


class SecretsReader:

    def __init__(self, client = None):
        client = client or boto3.client('secretsmanager')
        secrets_cache_config = secret_caching.SecretCacheConfig()
        self._cache = secret_caching.SecretCache(config=secrets_cache_config, client=client)

    def get_secret_string(self, secret_id: str) -> str:
        return self._cache.get_secret_string(secret_id)
