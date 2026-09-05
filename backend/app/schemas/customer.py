from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=100)
    phone: str = Field(default="", max_length=20)
    segment: str = Field(default="standard", max_length=50)
    lifetime_value: float = Field(default=0.0, ge=0.0)


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    phone: str
    segment: str
    lifetime_value: float