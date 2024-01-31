from pydantic import BaseModel, ConfigDict
from datetime import datetime


class PriceHistoryShow(BaseModel):
    id: int
    book_id: int
    price: int
    time: datetime

    model_config = ConfigDict(from_attributes=True)

