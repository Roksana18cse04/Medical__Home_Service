from pydantic import BaseModel
from typing import Optional, Literal, List

class User_SymptomsRequest(BaseModel):
    age: int
    gender: Literal["Male", "Female", "Other"]
    symptoms:list[str]