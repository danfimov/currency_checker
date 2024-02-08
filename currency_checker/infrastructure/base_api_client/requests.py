from pydantic import BaseModel
from yarl import URL


class RequestInfo(BaseModel):
    url: URL
    method: str

    class Config:
        arbitrary_types_allowed = True
