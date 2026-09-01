from pydantic import BaseModel

class PlanetPosition(BaseModel):
    name: str
    sign: str
    degree: float
    house: int | None = None

class NatalChart(BaseModel):
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: float
    lat: float
    lon: float

    asc: str
    houses: dict[int, str]
    planets: dict[str, PlanetPosition]


natal = NatalChart(
    birth_year=1995,
    birth_month=3,
    birth_day=11,
    birth_hour=20.5833,  # 20:35 ≈ 20.5833
    lat=35.7063066,
    lon=51.4509970,

    asc="22° میزان",
    houses={
        1: "2° میزان",
        2: "20° عقرب",
        3: "21° قوس",
        4: "24° جدی",
        5: "27° دلو",
        6: "26° حوت",
        7: "2° حمل",
        8: "20° ثور",
        9: "21° جوزا",
        10: "24° سرطان",
        11: "27° اسد",
        12: "26° سنبله",
    },
    planets={
        "Sun": PlanetPosition(name="Sun", sign="حوت", degree=20.67, house=6),
        "Moon": PlanetPosition(name="Moon", sign="سرطان", degree=15.83, house=10),
        "Mercury": PlanetPosition(name="Mercury", sign="دلو", degree=25.0, house=5),
        "Venus": PlanetPosition(name="Venus", sign="دلو", degree=10.0, house=5),
        "Mars": PlanetPosition(name="Mars", sign="اسد", degree=14.0, house=11),
        "Jupiter": PlanetPosition(name="Jupiter", sign="قوس", degree=14.0, house=3),
        "Saturn": PlanetPosition(name="Saturn", sign="حوت", degree=15.0, house=6),
        "Uranus": PlanetPosition(name="Uranus", sign="جدی", degree=29.0, house=4),
        "Neptune": PlanetPosition(name="Neptune", sign="جدی", degree=24.0, house=4),
        "Pluto": PlanetPosition(name="Pluto", sign="قوس", degree=0.0, house=3),
        "Node": PlanetPosition(name="Node", sign="عقرب", degree=6.0, house=2),
    }
)
