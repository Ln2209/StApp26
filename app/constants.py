"""Project constants (no random sampling anywhere: everything is deterministic)."""
YEARS = [2014, 2015, 2016]
POLLUTANTS = {"no2": "NO₂", "pm10": "PM10", "o3": "Ozone (O₃)"}
POLL_HELP = {
    "no2": "nitrogen dioxide, emitted mostly by road traffic.",
    "pm10": "particles smaller than 10 µm: traffic, heating, industry.",
    "o3": "ozone, forms with sunlight, so it is higher in summer.",
}
UNIT = "pts"  # Citeair sub-index points (unitless scale, 0 to 100+), NOT µg/m³
DEP_NAMES = {75: "Paris", 77: "Seine-et-Marne", 78: "Yvelines", 91: "Essonne", 92: "Hauts-de-Seine", 93: "Seine-Saint-Denis", 94: "Val-de-Marne", 95: "Val-d'Oise"}
DEP_ZONE = {75: "Paris", 92: "Inner suburbs", 93: "Inner suburbs", 94: "Inner suburbs", 77: "Outer suburbs", 78: "Outer suburbs", 91: "Outer suburbs", 95: "Outer suburbs"}
ZONE_COLORS = {"Paris": "#0B3C6F", "Inner suburbs": "#3F7CB8", "Outer suburbs": "#9DBBDC"}

# Reference lines = band limits of the Citeair scale (to confirm in the dataset documentation):
# 0-25 very low, 25-50 low, 50-75 medium, 75-100 high, >100 very high.
BANDS = {"Citeair 25: end of 'very low'": 25, "Citeair 50: start of 'medium'": 50}
REF_ANNUAL = {p: BANDS for p in ("no2", "pm10", "o3")}
REF_DAILY = {p: BANDS for p in ("no2", "pm10", "o3")}
DAILY_KPI_THRESHOLD = {"no2": 25, "pm10": 25, "o3": 25}  # regional daily mean above the 'very low' band
MONTHS_FULL = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MONTHS = [m[:3] for m in MONTHS_FULL]
YEAR_COLORS = {2014: "#8FB3D9", 2015: "#3F7CB8", 2016: "#0B3C6F"}  # light -> dark = chronology
SOURCE_TEXT = ("Daily Citeair air quality indices by pollutant for Île-de-France communes, 2014-2016 "
               "(data.gouv.fr, dataset \"Indices Qualité de l'air (Citeair) journaliers par polluant…)")
LICENSE_TEXT = ("Data license: Open Data Commons Open Database License (ODbL) - http://opendatacommons.org/licenses/odbl/summary/. Code: academic use.")
