import re
import pycountry
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE

COUNTRIES = sorted(c.name for c in pycountry.countries)

_NATIONALITY_OVERRIDES = {
    "Portugal": "Portuguese", "Spain": "Spanish", "France": "French",
    "Germany": "German", "United Kingdom": "British", "Ireland": "Irish",
    "Netherlands": "Dutch", "Belgium": "Belgian", "Luxembourg": "Luxembourgish",
    "Switzerland": "Swiss", "Austria": "Austrian", "Italy": "Italian",
    "Sweden": "Swedish", "Norway": "Norwegian", "Denmark": "Danish",
    "Finland": "Finnish", "Iceland": "Icelandic", "Poland": "Polish",
    "Czechia": "Czech", "Slovakia": "Slovak", "Hungary": "Hungarian",
    "Romania": "Romanian", "Bulgaria": "Bulgarian", "Greece": "Greek",
    "Croatia": "Croatian", "Slovenia": "Slovenian", "Serbia": "Serbian",
    "Ukraine": "Ukrainian", "Russian Federation": "Russian",
    "Estonia": "Estonian", "Latvia": "Latvian", "Lithuania": "Lithuanian",
    "Malta": "Maltese", "Cyprus": "Cypriot", "Turkey": "Turkish",
    "United States": "American", "Canada": "Canadian", "Mexico": "Mexican",
    "Brazil": "Brazilian", "Argentina": "Argentinian", "Chile": "Chilean",
    "Colombia": "Colombian", "Peru": "Peruvian", "Venezuela": "Venezuelan",
    "Uruguay": "Uruguayan", "Paraguay": "Paraguayan", "Ecuador": "Ecuadorian",
    "Bolivia": "Bolivian", "Cuba": "Cuban",
    "Angola": "Angolan", "Mozambique": "Mozambican", "Cabo Verde": "Cape Verdean",
    "Guinea-Bissau": "Bissau-Guinean", "Sao Tome and Principe": "Sao Tomean",
    "Timor-Leste": "Timorese", "Equatorial Guinea": "Equatorial Guinean",
    "South Africa": "South African", "Nigeria": "Nigerian", "Kenya": "Kenyan",
    "Morocco": "Moroccan", "Egypt": "Egyptian", "Algeria": "Algerian",
    "Tunisia": "Tunisian", "Ghana": "Ghanaian", "Ethiopia": "Ethiopian",
    "China": "Chinese", "Japan": "Japanese", "India": "Indian",
    "Pakistan": "Pakistani", "Bangladesh": "Bangladeshi", "Indonesia": "Indonesian",
    "Philippines": "Filipino", "Thailand": "Thai", "Vietnam": "Vietnamese",
    "South Korea": "South Korean", "Korea, Republic of": "South Korean",
    "Malaysia": "Malaysian", "Singapore": "Singaporean", "Israel": "Israeli",
    "Saudi Arabia": "Saudi", "United Arab Emirates": "Emirati",
    "Australia": "Australian", "New Zealand": "New Zealander",
}

def _fallback_demonym(country_name: str) -> str:
    name = country_name
    if name.endswith("ia"):
        return name + "n"
    if name.endswith("land"):
        return name + "ish" if not name.endswith("erland") else name + "ic"
    if name.endswith("y"):
        return name[:-1] + "ian"
    if name.endswith("a"):
        return name + "n"
    return name + "ian"

NATIONALITIES = sorted(
    {_NATIONALITY_OVERRIDES.get(c, _fallback_demonym(c)) for c in COUNTRIES}
)

# Display calling codes as "+351 PT", "+44 GB", etc.
_entries = []
for code, regions in COUNTRY_CODE_TO_REGION_CODE.items():
    for region in regions:
        if region == "001" or len(region) != 2:
            continue
        country = pycountry.countries.get(alpha_2=region)
        if not country:
            continue
        _entries.append((f"+{code} {region}", country.name))
CALLING_CODES = sorted(set(x[0] for x in _entries), key=lambda x: (int(re.search(r"\d+", x).group()), x))

def clean_phone_code(value: str) -> str:
    """Store only +digits from a display value such as '+351 PT'."""
    digits = re.sub(r"\D", "", str(value or ""))
    return f"+{digits}" if digits else ""
