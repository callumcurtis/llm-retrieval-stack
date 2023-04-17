variable region {
    type = string
    default = "us-west-2"
}

variable profile {
    type = string
}

variable openai_api_key {
    type = string
}

variable lambdas {
    type = map(object({
        src_path = string
        building_path = string
        filename = string
        handler = string
        runtime = string
    }))
    default={
        get_documents = {
            src_path = "functions/aws/get_documents/src"
            building_path = "functions/aws/get_documents/build"
            filename = "getDocuments.zip"
            handler = "index.handler"
            runtime = "python3.9"
        }
    }
}