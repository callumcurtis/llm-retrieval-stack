## LocalStack Deployment:

Start LocalStack docker container:

```bash
scripts/start-localstack.sh
```

Navigate to the deployment directory of your choice

```bash
cd deployment/aws
```

Deploy the stack to the LocalStack container

```bash
tflocal apply
```

Access the API Gateway endpoints:

```bash
curl http://localhost:4566/restapis/<gpt_retrieval_api_id>/local/_user_request_/<resource>
```

> **_NOTE:_** Replace `<gpt_retrieval_api_id>` with the API ID (output by step 3) and `<resource>` with the desired resource path (ex. `documents`)