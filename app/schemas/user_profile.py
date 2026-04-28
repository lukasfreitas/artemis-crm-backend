from pydantic import BaseModel, ConfigDict


class UserProfileResponse(BaseModel):
    id: str
    cell_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    cell_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None
