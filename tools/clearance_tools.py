from typing import Dict, Any, List, Optional
import difflib
import logging

logger = logging.getLogger("greenlight.tools.clearance")


def calculate_string_similarity(str1: str, str2: str) -> float:
    """Calculates SequenceMatcher similarity ratio between two strings (0.0 to 1.0)."""
    if not str1 or not str2:
        return 0.0
    return difflib.SequenceMatcher(None, str1.lower().strip(), str2.lower().strip()).ratio()


def soundex(name: str) -> str:
    """Generates standard American Soundex phonetic code for a name string."""
    name = "".join([c for c in name.upper() if c.isalpha()])
    if not name:
        return "Z000"

    first_letter = name[0]
    mapping = {
        "B": "1", "F": "1", "P": "1", "V": "1",
        "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
        "D": "3", "T": "3",
        "L": "4",
        "M": "5", "N": "5",
        "R": "6"
    }

    encoded = [first_letter]
    prev = mapping.get(first_letter, "0")

    for char in name[1:]:
        digit = mapping.get(char, "0")
        if digit != "0":
            if digit != prev:
                encoded.append(digit)
            prev = digit
        else:
            prev = "0"
        if len(encoded) == 4:
            break

    while len(encoded) < 4:
        encoded.append("0")

    return "".join(encoded)


def check_name_phonetic_similarity(character_name: str, comparison_name: str) -> Dict[str, Any]:
    """Evaluates phonetic and homophone similarity between a character name and a real person or registered name.
    
    Uses American Soundex phonetic coding combined with Levenshtein ratio to detect homophones
    and near-miss spellings (e.g. 'Gabrielle Sterlin' vs 'Gabriel Sterling').
    """
    if not character_name or not comparison_name:
        return {"error": "Both names must be non-empty"}

    ratio = calculate_string_similarity(character_name, comparison_name)
    
    # Check soundex on first and last names if available
    char_parts = character_name.strip().split()
    comp_parts = comparison_name.strip().split()

    char_last = char_parts[-1] if char_parts else character_name
    comp_last = comp_parts[-1] if comp_parts else comparison_name

    soundex_char_last = soundex(char_last)
    soundex_comp_last = soundex(comp_last)
    last_name_phonetic_match = (soundex_char_last == soundex_comp_last)

    soundex_char_full = soundex("".join(char_parts))
    soundex_comp_full = soundex("".join(comp_parts))
    full_phonetic_match = (soundex_char_full == soundex_comp_full)

    if full_phonetic_match or (last_name_phonetic_match and ratio >= 0.75):
        risk_level = "HIGH"
        verdict = "Potential homophone or confusing phonetic equivalent"
    elif ratio >= 0.70 or last_name_phonetic_match:
        risk_level = "MEDIUM"
        verdict = "Moderate phonetic or orthographic similarity"
    else:
        risk_level = "LOW"
        verdict = "Phonetically and orthographically distinct"

    return {
        "character_name": character_name,
        "comparison_name": comparison_name,
        "similarity_score": round(ratio, 3),
        "phonetic_code_character": soundex_char_full,
        "phonetic_code_comparison": soundex_comp_full,
        "last_name_soundex_match": last_name_phonetic_match,
        "phonetic_risk": risk_level,
        "assessment": verdict
    }


def check_mpaa_title_rules(title: str) -> List[Dict[str, Any]]:
    """Checks general MPAA / industry title clearance heuristics."""
    flags = []
    title_lower = title.lower().strip()
    
    # Generic or high-collision title warnings
    common_single_words = {"love", "revenge", "the end", "fear", "run", "darkness", "home", "blood"}
    if title_lower in common_single_words:
        flags.append({
            "issue": "Extremely common single-word title",
            "risk": "High likelihood of confusing similarity with dozens of existing registered works",
            "suggestion": "Add a distinctive subtitle or qualifying noun"
        })
        
    return flags


# Curated dictionary of vetted fictional brand names across common entertainment industry categories
GREEKING_CATALOG: Dict[str, List[str]] = {
    "firearms_tactical": [
        "Vanguard Arms", "Titan-9", "Aegis Tactical", "Valor Defense", "Centurion Armory"
    ],
    "automotive_luxury": [
        "Veloce Motors", "Castiglione GT", "Aurelia", "Monte Carlo Prestige", "Valente"
    ],
    "automotive_everyday": [
        "Centurion", "Metro Motors", "Valor Auto", "Pacifica Motors", "Apex Sedans"
    ],
    "tech_hardware": [
        "Apex Systems", "Syntron Devices", "OmniTech", "Novus Tech", "Spectra Systems"
    ],
    "software_ai": [
        "Neuralis", "Sentient Core", "Cognita Technologies", "Aegis AI", "Vektor Cloud"
    ],
    "pharma_biotech": [
        "Nexura Health", "TheraCorp", "BioVance Labs", "GeneSys Pharma", "Solas Life Sciences"
    ],
    "beverage_food": [
        "FizzCo", "Summit Springs", "Sunburst Cola", "Alpine Crisp", "Zest Refresh"
    ],
    "alcohol_spirits": [
        "Old Sovereign Bourbon", "Crown & Anchor Gin", "Glenmont Single Malt", "Bellerose Vineyard"
    ],
    "financial_banking": [
        "Meridian Standard Bank", "Vanguard Trust", "Sterling & Holt", "Crown Atlantic Capital"
    ],
    "luxury_goods_watches": [
        "Horlogerie Vaneau", "Kavell Chronometrics", "Aurelius Watchmakers", "Belmont & Co."
    ]
}


def suggest_greeking_alternatives(category: str, original_brand: str = "") -> Dict[str, Any]:
    """Suggests clearance-vetted fictional replacement brands ('greeking') for art departments and props.
    
    NOTE: Heuristic string-distance pre-filter only; not a substitute for a full
    likelihood-of-confusion analysis under the multi-factor Sleekcraft/Polaroid tests
    (e.g., AMF Inc. v. Sleekcraft Boats, 599 F.2d 341; Polaroid Corp. v. Polarad Elecs. Corp., 287 F.2d 492).
    """
    category_key = category.lower().strip().replace(" ", "_").replace("-", "_")
    
    # Fuzzy match category if not exact
    matching_cat = None
    for cat in GREEKING_CATALOG:
        if category_key in cat or cat in category_key:
            matching_cat = cat
            break
            
    if not matching_cat:
        # Fallback to general tech or luxury if unknown
        matching_cat = "tech_hardware"

    candidates = GREEKING_CATALOG[matching_cat]
    suggestions = []

    for cand in candidates:
        sim = calculate_string_similarity(original_brand, cand) if original_brand else 0.0
        suggestions.append({
            "fictional_brand": cand,
            "category": matching_cat,
            "string_similarity_to_original": round(sim, 3),
            "heuristic_check": "PASS (Low orthographic similarity < 0.35)" if sim < 0.35 else "CAUTION (Potential orthographic proximity)"
        })

    # Sort so least similar candidates are first
    suggestions.sort(key=lambda x: x["string_similarity_to_original"])

    return {
        "original_brand": original_brand,
        "category": matching_cat,
        "available_alternatives": suggestions[:3],
        "clearance_advisory": "Heuristic string-distance pre-filter only; not a substitute for a full likelihood-of-confusion analysis (Sleekcraft/Polaroid multi-factor test)."
    }

