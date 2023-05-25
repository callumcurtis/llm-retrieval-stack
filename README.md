# LLM Retrieval Stack: Prompt Augmentation for Large Language Models (LLMs) using Semantic Search

## Description

This project aims to develop a cloud-based system to embed and store arbitrary user data, facilitating semantic search and retrieval of personal or organizational knowledge for input to GPT-4 and other language models.

Systems like this one are useful for improving the relevance and quality of large language model outputs, as they supply the model with additional context from a knowledge base of the user's choosing - allowing the model's knowledge to be supplemented on the fly. For more information, see the [Retrieval-Augmented Generation (RAG) paper](https://arxiv.org/abs/2005.11401).

## Advantages over Existing Solutions

### ChatGPT Retrieval Plugin

The [ChatGPT Retrieval Plugin](https://github.com/openai/chatgpt-retrieval-plugin#chatgpt-retrieval-plugin) by OpenAI serves the same purpose: "it allows users to obtain the most relevant document snippets from their data sources, such as files, notes, or emails, by asking questions or expressing needs in natural language. Enterprises can make their internal documents available to their employees through ChatGPT using this plugin."

Advantages of this project:

- Serverless: this project is deployed serverlessly instead of as a container
    - Improved scalability
    - Cost benefits depend on use case and workload
- Stream processing: this project processes input as a stream
    - Constant amount of memory required, regardless of input size
    - API requests for chunks in the stream can proceed asynchronously during stream processing, rather than after the entire input is processed
- Data parallelism: this project splits input into parts (e.g., 1 MB in size) and allocates these parts across an arbitrary number of cloud function instances instead of processing the entire input sequentially
    - More efficient processing of large inputs
- Coupling to OpenAI services: this project is designed to be extensible to support arbitrary clients, LLMs, and text embedding services instead of only OpenAI services (i.e., ChatGPT web interface and OpenAI embedding models)
- Storage of original data: this project uses an object storage service (e.g., AWS S3) as a single source of truth for the original data instead of storing it alongside the embeddings in the vector store (e.g., Pinecone, Weaviate)
    - Improved data durability
    - Larger supported uploads
    - Lower costs

## Architecture

<div align="center">
  <img src="https://github.com/callumcurtis/llm-retrieval-stack/blob/main/docs/aws-system-architecture.png?raw=true">
</div>

## Project Structure

- [deploy](deploy/): deployment configurations
    - [aws](deploy/aws/): AWS Serverless Application Model (SAM) templates
- [functions](functions/): cloud functions
    - [aws](functions/aws/): AWS Lambda functions and layers
        - [lambdas](functions/aws/lambdas/): AWS Lambda functions
            - [get-upload-url](functions/aws/lambdas/get-upload-url/): returns a presigned URL for uploading a file to an S3 bucket
            - [handle-unprocessed-object-part](functions/aws/lambdas/handle-unprocessed-object-part/): handles an unprocessed object part ID
            - [handle-upload-notification](functions/aws/lambdas/handle-upload-notification/): handles an upload event notification
        - [layers](functions/aws/layers/): AWS Lambda layers
            - [llm-retrieval](functions/aws/layers/llm-retrieval/): core utilities and services layer
            - [llm-retrieval-aws-utils](functions/aws/layers/llm-retrieval-aws-utils/): AWS-specific utilities layer
- [llm_retrieval](llm_retrieval/): core utilities and services, common across cloud providers
- [tests](tests/): unit and integration tests

## Getting Started

Prerequisites:
- SAM CLI
- AWS account
- OpenAI API key
- Pinecone API key

To get started with this project, follow the steps below:

1. Clone the repository
2. Run [sam deploy --guided](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-deploy.html) in [`deploy/aws`](deploy/aws) and follow the instructions

## Milestone Progress

### :white_check_mark: Milestone 1: Scalable Processing and Storage for Text Embeddings

Goal: Develop a cloud-based system to embed and store arbitrary user data, facilitating semantic search and retrieval of personal or organizational knowledge for input to GPT-4 and other language models.

### :white_large_square: Milestone 2: Semantic Search and Prompt Augmentation

Goal: Develop a cloud-based system to perform semantic search and prompt augmentation for large language models (LLMs) using the system developed in Milestone 1.

### :white_large_square: Milestone 3: User Interface

Goal: Develop a demo web application to showcase the system developed in previous milestones.
