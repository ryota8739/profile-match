from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)

    age: int = Field(ge=18, le=100)
    gender: str
    height: int = Field(gt=0, le=250)

    job: str
    income: int = Field(ge=0)

    region: str

    hobbies: list[str] = []


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
