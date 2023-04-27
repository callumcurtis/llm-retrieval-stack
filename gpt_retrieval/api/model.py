from pydantic import BaseModel


class GetUploadUrlResponse(BaseModel):
    uploadUrl: str
