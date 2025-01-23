from datetime import datetime

from sqlmodel import Field, SQLModel

class Plot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    lot : str = Field(index=True)
    saleOrder : str = Field(index=True)
    case : str = Field(index=True)
    type : str = Field(index=True)
    size : str = Field(index=True)
    price : float = Field(index=True)
    district : str = Field(index=True)
    subDistrict : str = Field(index=True)
    province : str = Field(index=True)
    created_at: datetime = Field(default=datetime.now)
    isAvailable: bool = Field(default=True)
    