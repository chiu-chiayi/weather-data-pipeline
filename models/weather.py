from sqlmodel import SQLModel, Field, Column, TIMESTAMP, text
from datetime import date, time, datetime

# ORM(物件關係映射): 將資料庫中的表格映射到 python 類別的定義
class Dim_Location(SQLModel, table=True):
    # __tablename__ = "dim_location" # 預設情況下，SQLModel 會把類別名稱轉成小寫
    sk: int = Field(default=None, primary_key=True)
    location_name: str = Field(nullable=False, unique=True)

class Dim_Date(SQLModel, table=True):
    id: int = Field(primary_key=True)
    full_date: date = Field(unique=True, nullable=False)
    year: int = Field(nullable=False)
    month: int = Field(nullable=False)
    day: int = Field(nullable=False)
    day_of_week: int = Field(nullable=False)
    is_weekend: bool = Field(default=False)

class Dim_Time(SQLModel, table=True):
    id: int = Field(primary_key=True)
    full_time: time = Field(unique=True, nullable=False)
    hour: int = Field(nullable=False)
    minute: int = Field(nullable=False)

class Fact_Weather_Forecast(SQLModel, table=True):
    sk: int = Field(default=None, primary_key=True)
    location_sk: int = Field(nullable=False)
    start_date_id: int = Field(nullable=False)
    start_time_id: int = Field(nullable=False)
    end_date_id: int = Field(nullable=False)
    end_time_id: int = Field(nullable=False)

    wx: str = Field(default=None, description='天氣現象')
    pop: float = Field(default=None, description='降雨機率(%)')
    mint: float = Field(default=None, description='最低溫度(℃)')
    maxt: float = Field(default=None, description='最高溫度(℃)')
    ci: str = Field(default=None, description='舒適度')

    data_pull_time: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False
        )
    )