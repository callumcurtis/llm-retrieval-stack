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
}