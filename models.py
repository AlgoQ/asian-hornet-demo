from typing import Optional
from time import time
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator

class Photo(SQLModel, table=True):
    __tablename__ = "photos"
    
    id: int = Field(default=None, primary_key=True)
    url: str
    license_code: Optional[str] = None
    attribution: Optional[str] = None
    observation_id: Optional[int] = Field(default=None, foreign_key="observations.id", nullable=False)
    observation: Optional["Observation"] = Relationship(
        back_populates="photos"
    )

class Observation(SQLModel, table=True):
    __tablename__ = "observations"
    
    id: int = Field(default=None, primary_key=True)
    external_id: int = Field(unique=True, nullable=False)
    provider: str = Field(default="INaturalist")
    observer: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    place: Optional[str] = None
    observed_on: Optional[int] = None
    posted_on: int = Field(default_factory=lambda: round(time()))
    description: Optional[str] = Field(None, max_length=2000)
    photos: list[Photo] = Relationship(
        back_populates="observation",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "single_parent": True
        }
    )

    @field_validator("description")
    def validate_description(cls, v):
        if v and len(v) > 2000:
            return v[:2000]  # Truncate to 2000 characters
        return v

    @field_validator("observed_on")
    def validate_observed_on(cls, v):
        if v is not None:
            current_time = round(time())
            if v > current_time:
                raise ValueError("Observation date cannot be in the future")
            if v < 946684800:
                raise ValueError("Observation date cannot be before year 2000")
        return v
    
    @field_validator("posted_on")
    def validate_posted_on(cls, v):
        current_time = round(time())
        if v > current_time:
            raise ValueError("Posted date cannot be in the future")
        if v < 946684800:
            raise ValueError("Posted date cannot be before year 2000")
        return v

    @field_validator("provider")
    def validate_provider(cls, v):
        allowed_providers = ["INaturalist", "Waarnemingen"]
        if v not in allowed_providers:
            raise ValueError(f"Provider must be one of: {", ".join(allowed_providers)}")
        return v
