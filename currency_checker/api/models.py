from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    service: str = Field(default="currency_checker")
    version: str = Field(..., example='0.1.0')
    hostname: str = Field(..., example="localhost")


class Course(BaseModel):
    direction: str = Field(..., example="BTC-RUB")
    value: float


class CoursesResponse(BaseModel):
    exchanger: str = Field(..., example="binance")
    courses: list[Course]
