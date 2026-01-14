from typing import Union, Optional, TypeVar, Type, List, Any, Literal
from datetime import date

from pydantic import BaseModel, Field


T = TypeVar('T', bound=BaseModel)


# Evidence tracking models
class WithEvidence(BaseModel):
    """Base model for extracted fields with evidence tracking"""
    value: Any = Field(..., description="The extracted value")
    evidence: str = Field(..., description="Exact quote from document supporting this value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    
    class Config:
        json_encoders = {date: lambda v: v.isoformat()}


class StringWithEvidence(WithEvidence):
    value: Optional[str] = None


class IntWithEvidence(WithEvidence):
    value: Optional[int] = None


class FloatWithEvidence(WithEvidence):
    value: Optional[float] = None

def LiteralWithEvidence(*options: str):
    """
    Factory function to create a LiteralWithEvidence class with specific allowed values.
    
    Usage:
        project_category: LiteralWithEvidence("Explore Projects", "Establish Projects", "Contribute Projects") = Field(...)
    """
    literal_type = Literal[options] if len(options) > 1 else Literal[options[0]]
    
    class _LiteralWithEvidence(WithEvidence):
        value: Optional[literal_type] = None  # type: ignore
    
    return _LiteralWithEvidence