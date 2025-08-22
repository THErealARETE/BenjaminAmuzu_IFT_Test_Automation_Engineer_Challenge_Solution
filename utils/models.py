from pydantic import BaseModel, field_validator
from typing import List

class NodeInfo(BaseModel):
    """Pydantic model for validating the /debug/v1/info response schema."""
    listenAddresses: List[str]
    enrUri: str

    @field_validator('enrUri')
    @classmethod
    def enr_must_start_with_enr(cls, v):
        if not v.startswith('enr:'):
            raise ValueError('enrUri must start with "enr:"')
        return v


class WakuMessage(BaseModel):
    """Pydantic model for validating Waku message schema."""
    payload: str
    contentTopic: str
    version: int
    timestamp: int

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v):
        """Validate that timestamp is a reasonable Unix timestamp in nanoseconds"""
        # Convert nanoseconds to seconds
        timestamp_seconds = v / 1_000_000_000
        
        # Check if it's a reasonable timestamp (between 2000-01-01 and 2030-01-01)
        if timestamp_seconds < 946684800 or timestamp_seconds > 1893456000:
            raise ValueError(f'Timestamp {v} is not within a reasonable range')
        return v