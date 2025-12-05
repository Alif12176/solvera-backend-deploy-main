from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel

T = TypeVar('T')

class APIResponse(GenericModel, Generic[T]):
    success: bool
    data: Optional[T]
    error: Optional[str]