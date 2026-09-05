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
