import pydantic


class GetUploadUrlResponse(pydantic.BaseModel):
    upload_url: str = pydantic.Field(alias='uploadUrl')

    class Config:
        allow_population_by_field_name = True
