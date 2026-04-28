from pydantic import BaseModel, ConfigDict, Field


class PermissionGroupBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = None
    is_admin: bool = False
    is_influencer: bool = False


class PermissionGroupCreate(PermissionGroupBase):
    pass


class PermissionGroupUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    is_admin: bool | None = None
    is_influencer: bool | None = None


class PermissionGroupResponse(PermissionGroupBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
