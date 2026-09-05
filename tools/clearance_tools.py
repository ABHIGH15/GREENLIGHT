from typing import Dict, Any, List, Optional
import difflib
import logging

logger = logging.getLogger("greenlight.tools.clearance")


def calculate_string_similarity(str1: str, str2: str) -> float:
    """Calculates SequenceMatcher similarity ratio between two strings (0.0 to 1.0)."""
    if not str1 or not str2:
        return 0.0
    return difflib.SequenceMatcher(None, str1.lower().strip(), str2.lower().strip()).ratio()


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
