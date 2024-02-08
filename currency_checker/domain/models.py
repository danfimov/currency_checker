from pydantic import BaseModel


class Account(BaseModel):
    token: str

    class Config:
        orm_mode = True
