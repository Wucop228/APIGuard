from pydantic import BaseModel, EmailStr, Field


class AuthUser(BaseModel):
    email: EmailStr = Field(..., description="Почта пользователя")
    password: str = Field(..., description="Пароль пользователя")


class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=6, max_length=32, description="Пароль от 6 до 32 символов")