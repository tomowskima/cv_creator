from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from .config import CVVariant, ProfileType


class ExperienceItem(BaseModel):
    role: str
    company: str
    start_year: int
    end_year: Optional[int] = None  # None = obecnie
    description_raw: Optional[str] = None  # to co user wpisze


class EducationItem(BaseModel):
    school: str
    degree: str
    start_year: int
    end_year: int


class CVInput(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    profile_type: ProfileType
    cv_variant: CVVariant
    target_role: str  # np. "Solution Architect"
    summary_hint: Optional[str] = None
    education: List[EducationItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)

