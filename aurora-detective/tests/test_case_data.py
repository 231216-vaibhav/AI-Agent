"""Unit tests for authoritative case data in aurora-detective."""

import pytest
from case_data import (
    get_case_data,
    get_modified_case_data,
    CASE_NAME,
    LOCATION,
    CRITICAL_OPPORTUNITY_WINDOW
)


def test_case_metadata():
    case = get_case_data()
    assert case["case_name"] == "The Vanishing Aurora Diamond"
    assert case["location"] == "Northbridge Museum, Grand Gallery"
    assert case["critical_opportunity_window"] == "8:20 PM – 8:24 PM (Power Failure)"


def test_timeline_structure():
    case = get_case_data()
    timeline = case["timeline"]
    assert len(timeline) >= 8

    times = [e["time"] for e in timeline]
    assert "8:00 PM" in times
    assert "8:20 PM – 8:24 PM" in times
    assert "8:30 PM" in times

    # Ensure key events exist
    assert any("confirmed inside locked display case" in e["description"] for e in timeline)
    assert any("Arjun Vale's card opened the display case" in e["description"] for e in timeline)
    assert any("Power failure" in e["description"] for e in timeline)


def test_four_suspects():
    case = get_case_data()
    suspects = case["suspects"]
    assert len(suspects) == 4

    names = [s["name"] for s in suspects]
    assert names == ["Lena Ortiz", "Theo Park", "Arjun Vale", "Sofia Reed"]

    # Verify specific details
    arjun = next(s for s in suspects if s["name"] == "Arjun Vale")
    assert "large private debt" in arjun["background"]
    assert "card opened display case at 8:23 PM" in arjun["access"]
    assert "flat catalogue folder" in arjun["movement"]

    theo = next(s for s in suspects if s["name"] == "Theo Park")
    assert "8:15–8:29 PM" in theo["alibi"]

    lena = next(s for s in suspects if s["name"] == "Lena Ortiz")
    assert "wet courtyard" in lena["movement"]

    sofia = next(s for s in suspects if s["name"] == "Sofia Reed")
    assert "Three guests remember speaking with her" in sofia["alibi"]


def test_evidence_a_through_g():
    case = get_case_data()
    evidence = case["evidence"]
    assert len(evidence) == 7

    e_ids = [e["id"] for e in evidence]
    assert e_ids == ["A", "B", "C", "D", "E", "F", "G"]


def test_modified_case_removes_only_e():
    orig_case = get_case_data()
    mod_case = get_modified_case_data()

    orig_ids = [e["id"] for e in orig_case["evidence"]]
    mod_ids = [e["id"] for e in mod_case["evidence"]]

    assert "E" in orig_ids
    assert "E" not in mod_ids
    assert len(mod_ids) == 6
    assert mod_ids == ["A", "B", "C", "D", "F", "G"]
