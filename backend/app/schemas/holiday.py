from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CountryCode(str, Enum):
    JAPAN = "JP"
    US = "US"
    UK = "UK"
    CA = "CA"


class HolidayBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255)
    name_en: str | None = Field(None, max_length=255)
    date: date
    country: str = Field(default="JP")
    is_national: bool = Field(default=True)
    is_recurring: bool = Field(default=True)
    description: str | None = Field(None, max_length=500)
    description_en: str | None = Field(None, max_length=500)

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v < date(1900, 1, 1) or v > date(2100, 12, 31):
            raise ValueError('Date must be between 1900 and 2100')
        return v


class HolidayCreate(HolidayBase):
    pass


class HolidayUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    name_en: str | None = Field(None, max_length=255)
    date: date | None = None
    country: str | None = None
    is_national: bool | None = None
    is_recurring: bool | None = None
    description: str | None = Field(None, max_length=500)
    description_en: str | None = Field(None, max_length=500)

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v and (v < date(1900, 1, 1) or v > date(2100, 12, 31)):
            raise ValueError('Date must be between 1900 and 2100')
        return v


class HolidayInfo(HolidayBase):
    id: int
    year: int
    created_at: datetime
    updated_at: datetime


class HolidayListResponse(BaseModel):
    holidays: list[HolidayInfo]
    total: int
    year: int | None = None
    country: str | None = None


class HolidayQueryParams(BaseModel):
    year: int | None = Field(None, ge=1900, le=2100)
    country: str | None = Field(None)
    month: int | None = Field(None, ge=1, le=12)
    is_national: bool | None = Field(None)
    date_from: date | None = Field(None)
    date_to: date | None = Field(None)

    @field_validator('date_to')
    @classmethod
    def validate_date_range(cls, v, info):
        if v and info.data.get('date_from') and v < info.data['date_from']:
            raise ValueError('date_to must be after date_from')
        return v
