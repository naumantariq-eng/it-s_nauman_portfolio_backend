from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=5)
    type: str = Field(default="general", max_length=50)  # "achievement", "project", "announcement", "general"
    is_active: bool = Field(default=True)


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    message: Optional[str] = Field(None, min_length=5)
    type: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationStatusUpdate(BaseModel):
    is_active: bool
