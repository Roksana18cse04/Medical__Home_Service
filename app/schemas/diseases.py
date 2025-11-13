from pydantic import BaseModel
from typing import Optional, Literal, List

class User_SymptomsRequest(BaseModel):
    age: int
    gender: str
    symptoms:list[str]