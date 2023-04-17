## AWS Deployment

Navigate to the deployment directory of your choice:

```bash
cd deployment/aws
```

Create a Terraform variables file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit the Terraform variables file to provide your credentials and preferences:

```bash
vi terraform.tfvars
```

Initialize Terraform:

```bash
terraform init
```

Deploy the stack:

```bash
terraform apply
```

## LocalStack Deployment

Start LocalStack docker container:

```bash
scripts/start-localstack.sh
```

Navigate to the deployment directory of your choice:

```bash
cd deployment/aws
```

Deploy the stack to the LocalStack container:

```bash
tflocal apply
```

Access the API Gateway endpoints:

```bash
curl http://localhost:4566/restapis/<gpt_retrieval_api_id>/local/_user_request_/<resource>
```

> **_NOTE:_** Replace `<gpt_retrieval_api_id>` with the API ID (output by step 3) and `<resource>` with the desired resource path (ex. `documents`)

Access S3 bucket contents:

```bash
awslocal s3 ls s3://<bucket-name>/
```