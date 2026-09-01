from pydantic import BaseModel

class NatalChart(BaseModel):
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: float
    lat: float
    lon: float
