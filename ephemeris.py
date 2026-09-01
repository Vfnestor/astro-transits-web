import swisseph as swe
from datetime import datetime
from math import degrees

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

ASPECTS = {
    "conjunction": 0,
    "opposition": 180,
    "square": 90,
    "trine": 120,
}

def get_planet_positions(year, month, day, hour=12):
    swe.set_ephe_path(".")
    jd = swe.julday(year, month, day, hour)

    positions = {}
    for name, planet in PLANETS.items():
        lon, lat, dist, speed = swe.calc_ut(jd, planet)
        positions[name] = lon

    return positions

def get_houses(year, month, day, hour, lat, lon):
    jd = swe.julday(year, month, day, hour)
    cusps, ascmc = swe.houses(jd, lat, lon)
    return cusps, ascmc

def detect_aspects(natal_positions, transit_positions, orb=3):
    results = []

    for t_name, t_lon in transit_positions.items():
        for n_name, n_lon in natal_positions.items():
            diff = abs(t_lon - n_lon)
            diff = min(diff, 360 - diff)

            for asp_name, asp_angle in ASPECTS.items():
                if abs(diff - asp_angle) <= orb:
                    results.append({
                        "transit": t_name,
                        "natal": n_name,
                        "aspect": asp_name,
                        "orb": round(abs(diff - asp_angle), 2)
                    })

    return results
