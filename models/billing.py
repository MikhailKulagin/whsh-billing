from datetime import datetime
from pydantic import BaseModel
from pydantic.fields import Optional


class Invoice(BaseModel):
    id: Optional[int]
    id_account: Optional[int]
    operation: Optional[int]
    tstamp: Optional[datetime]

    class Config:
        orm_mode = True
