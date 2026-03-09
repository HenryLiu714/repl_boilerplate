from pydantic import BaseModel
from enum import Enum

class CellType(Enum):
    NUMBER = "number"
    STRING = "string"
    FORMULA = "formula"
    REF = "ref"

class Expression(BaseModel):
    raw: str
    type: CellType | None = None
    value: float | str | None = None

    operator: str | None = None
    operands: list['Expression'] = []

    def __str__(self):
        return self.raw