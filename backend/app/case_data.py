"""Authoritative case data for The Vanishing Aurora Diamond.
Contains strictly the authorized facts, suspects, and evidence items A through G.
"""

from typing import List, Dict, Any
from copy import deepcopy

CASE_TITLE = "The Vanishing Aurora Diamond"
LOCATION = "Northbridge Museum, Grand Gallery"

INCIDENT_DETAILS = {
    "case_id": "001",
    "title": CASE_TITLE,
    "location": LOCATION,
    "events": [
        {"time": "8:00 PM", "description": "Diamond displayed in a locked glass case."},
        {"time": "8:20 PM - 8:24 PM", "description": "Power failure occurs in the museum."},
        {"time": "8:30 PM", "description": "Diamond discovered missing."},
    ],
    "key_conditions": [
        "Glass remained intact.",
        "Electronic lock is battery-backed.",
        "Valid-card access is recorded during power failure."
    ]
}

SUSPECTS: List[Dict[str, Any]] = [
    {
        "name": "Lena Ortiz",
        "background": "Recently denied a promotion.",
        "statement": "Says she restarted basement generator from 8:19 to 8:26.",
        "card_activity": "Her card opened basement at 8:20.",
        "movement": "She crossed a wet courtyard earlier."
    },
    {
        "name": "Theo Park",
        "background": "Wanted publicity for museum event.",
        "statement": "Says he remained on stage. Says he did not enter Grand Gallery during blackout.",
        "card_activity": "No unauthorized card activity recorded.",
        "movement": "Camera shows him continuously from 8:15 to 8:29 on stage."
    },
    {
        "name": "Arjun Vale",
        "background": "Has large private debt.",
        "statement": "Says he worked in archive. Says his card remained in his jacket inside archive.",
        "card_activity": "His card opened archive at 8:12. His card opened display case at 8:23.",
        "movement": "At 8:25 he leaves archive carrying a flat catalogue folder. Camera does NOT show folder contents."
    },
    {
        "name": "Sofia Reed",
        "background": "Wanted exclusive news story.",
        "statement": "Says she interviewed lobby guests.",
        "card_activity": "No gallery card access recorded.",
        "movement": "Three guests remember speaking with her during blackout. None reports seeing her enter gallery."
    }
]

EVIDENCE_ITEMS: List[Dict[str, str]] = [
    {
        "id": "A",
        "description": "Electronic lock is battery-backed and records valid-card access during power failure."
    },
    {
        "id": "B",
        "description": "Arjun Vale's card opened display case at 8:23 PM."
    },
    {
        "id": "C",
        "description": "Arjun says his card remained in his jacket inside archive."
    },
    {
        "id": "D",
        "description": "Camera image at 8:25 shows Arjun leaving archive carrying a flat catalogue folder. Contents are not visible."
    },
    {
        "id": "E",
        "description": "Blue velvet fibers found inside folder. Display cushion is blue velvet."
    },
    {
        "id": "F",
        "description": "Muddy shoeprint near case matches Lena's boot size. Records show she crossed wet courtyard earlier."
    },
    {
        "id": "G",
        "description": "If diamond remains missing, insurance pays museum rather than any named suspect."
    }
]


def get_authoritative_case() -> Dict[str, Any]:
    """Returns a fresh deep copy of the complete authoritative case data."""
    return {
        "case_id": INCIDENT_DETAILS["case_id"],
        "title": CASE_TITLE,
        "location": LOCATION,
        "incident": deepcopy(INCIDENT_DETAILS),
        "suspects": deepcopy(SUSPECTS),
        "evidence": deepcopy(EVIDENCE_ITEMS)
    }


def get_modified_case() -> Dict[str, Any]:
    """Returns the case data with ONLY Evidence E removed."""
    case = get_authoritative_case()
    case["evidence"] = [e for e in case["evidence"] if e["id"] != "E"]
    return case
