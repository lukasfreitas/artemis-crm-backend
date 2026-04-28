from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.contact_message import ContactMessageStatus


class ContactMessageCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    whatsapp: str = Field(min_length=8, max_length=32)
    company: str | None = Field(default=None, max_length=160)
    message: str = Field(min_length=5, max_length=2000)


class ContactMessageStatusUpdate(BaseModel):
    status: ContactMessageStatus


class ContactMessagePublicResponse(BaseModel):
    id: str
    status: ContactMessageStatus

    model_config = ConfigDict(from_attributes=True)


class ContactMessageResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    whatsapp: str
    company: str | None = None
    message: str
    status: ContactMessageStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
