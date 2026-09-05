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


# Notable active titles and major studio franchises registered with MPA / theatrical distributors
NOTABLE_TITLE_REGISTRY: List[Dict[str, Any]] = [
    {
        "title": "The Apprentice",
        "year": 2024,
        "distributor": "Briarcliff Entertainment / Scythia Films",
        "notes": "Theatrical biographical drama directed by Ali Abbasi"
    },
    {
        "title": "The Godfather",
        "year": 1972,
        "distributor": "Paramount Pictures",
        "notes": "Academy Award winning studio franchise"
    },
    {
        "title": "Inception",
        "year": 2010,
        "distributor": "Warner Bros.",
        "notes": "Christopher Nolan blockbuster with entrenched secondary meaning"
    },
    {
        "title": "The Last of Us",
        "year": 2023,
        "distributor": "HBO / Sony Pictures Television",
        "notes": "Major active prestige drama franchise"
    },
    {
        "title": "Oppenheimer",
        "year": 2023,
        "distributor": "Universal Pictures",
        "notes": "Academy Award Best Picture winner"
    },
    {
        "title": "Gladiator",
        "year": 2000,
        "distributor": "DreamWorks / Paramount Pictures",
        "notes": "Major active historical epic franchise (Gladiator II in 2024)"
    },
    {
        "title": "Severance",
        "year": 2022,
        "distributor": "Apple TV+",
        "notes": "Emmy-winning workplace thriller series"
    },
    {
        "title": "Succession",
        "year": 2018,
        "distributor": "HBO",
        "notes": "Emmy-winning prestige drama franchise"
    }
]


def _normalize_title_text(t: str) -> str:
    """Normalizes title string by stripping punctuation, extra whitespace, and leading articles."""
    import re
    t = t.lower().strip()
    t = re.sub(r'^[,\.\'\"\:\-]+|[,\.\'\"\:\-]+$', '', t)
    for article in ['the ', 'a ', 'an ']:
        if t.startswith(article):
            t = t[len(article):]
            break
    return t.strip()


def check_mpaa_title_rules(title: str) -> Dict[str, Any]:
    """Evaluates film/television title clearance heuristics under MPA Title Registration Bureau (TRB) standards.
    
    Checks exact matches, normalized token overlap, possessive/substring collisions,
    and single-word generic pitfalls under Lanham Act § 43(a) secondary meaning doctrine
    (Warner Bros. v. Majestic Pictures Corp., 70 F.2d 310; Kirkland v. NBC, 425 F. Supp. 1111).
    Also generates 2-3 distinctive replacement titles pre-screened to ensure 0 collisions.
    """
    import re
    if not title:
        return {"error": "Title must be non-empty"}

    norm_title = _normalize_title_text(title)
    title_words = set(re.findall(r'\b\w+\b', norm_title))
    title_lower = title.lower().strip()

    flags = []
    collisions = []

    # 1. Check generic single-word pitfalls
    common_single_words = {"love", "revenge", "the end", "fear", "run", "darkness", "home", "blood", "truth", "justice"}
    if title_lower in common_single_words:
        flags.append({
            "issue": "Extremely common generic single-word title",
            "risk": "High vulnerability under secondary meaning doctrine; lack of distinctiveness prevents exclusive registration.",
            "suggestion": "Add a distinctive subtitle, thematic noun, or modifier."
        })

    # Common grammatical stopwords to ignore during token overlap
    stopwords = {"the", "a", "an", "of", "and", "in", "on", "at", "to", "for", "with", "by"}
    meaningful_title_words = title_words - stopwords

    # 2. Check collisions against notable studio/franchise title registry (exact, fuzzy, substring, token overlap)
    for reg in NOTABLE_TITLE_REGISTRY:
        reg_title = reg["title"]
        reg_norm = _normalize_title_text(reg_title)
        reg_words = set(re.findall(r'\b\w+\b', reg_norm))
        meaningful_reg_words = reg_words - stopwords

        sim_score = calculate_string_similarity(norm_title, reg_norm)
        is_substring = (reg_norm in norm_title) or (norm_title in reg_norm)
        token_overlap = meaningful_title_words.intersection(meaningful_reg_words)

        # High-collision criteria: exact match, substring/possessive root overlap, or high token overlap
        if reg_norm == norm_title:
            collisions.append({
                "competing_work": f"{reg_title} ({reg.get('year', 'N/A')})",
                "distributor": reg.get("distributor", "Unknown"),
                "similarity_type": "EXACT_MATCH",
                "similarity_score": 1.0,
                "risk_level": "HIGH",
                "trb_advisory": "MPA TRB protest guaranteed; active commercial release with entrenched secondary meaning."
            })
        elif is_substring or (token_overlap and len(token_overlap) == len(meaningful_reg_words)) or sim_score >= 0.55:
            collisions.append({
                "competing_work": f"{reg_title} ({reg.get('year', 'N/A')})",
                "distributor": reg.get("distributor", "Unknown"),
                "similarity_type": f"SUBSTRING_OR_TOKEN_OVERLAP ({', '.join(token_overlap)})" if token_overlap else "PHONETIC_OR_ORTHOGRAPHIC_PROXIMITY",
                "similarity_score": round(sim_score, 3),
                "risk_level": "HIGH" if (is_substring or sim_score >= 0.60) else "MEDIUM",
                "trb_advisory": "Confusing similarity likely to trigger an MPA TRB dispute or reverse-confusion claim under Lanham Act § 43(a)."
            })

    # Overall risk level
    if any(c["risk_level"] == "HIGH" for c in collisions):
        overall_risk = "HIGH"
    elif collisions or flags:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    # 3. Generate distinctive alternative working titles
    raw_alternatives = [
        "The Architect's Reckoning",
        "Protocol of Shadows",
        "Echoes of Retribution",
        "Vanguard of Silence",
        "The Syndicate Breach"
    ]

    # Pre-screen alternatives back through the collision checker to guarantee zero collision
    verified_alternatives = []
    for cand in raw_alternatives:
        cand_norm = _normalize_title_text(cand)
        cand_words = set(re.findall(r'\b\w+\b', cand_norm)) - stopwords
        cand_collision = False

        for reg in NOTABLE_TITLE_REGISTRY:
            reg_norm = _normalize_title_text(reg["title"])
            reg_words = set(re.findall(r'\b\w+\b', reg_norm)) - stopwords
            if (reg_norm in cand_norm) or (cand_norm in reg_norm) or cand_words.intersection(reg_words):
                cand_collision = True
                break

        if not cand_collision:
            verified_alternatives.append(cand)
        if len(verified_alternatives) >= 3:
            break


    return {
        "title": title,
        "normalized_title": norm_title,
        "overall_risk": overall_risk,
        "has_collisions": len(collisions) > 0,
        "collisions": collisions,
        "flags": flags,
        "verified_alternative_titles": verified_alternatives,
        "legal_advisory": "Titles are not copyrightable (37 C.F.R. § 202.1(a); Kirkland v. NBC), but are heavily protected under Lanham Act § 43(a) secondary meaning (Warner Bros. v. Majestic Pictures) and MPA Title Registration Bureau rules."
    }



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

