"""Unit tests for Authoritative Case Data."""

import pytest
from app.case_data import (
    get_authoritative_case,
    get_modified_case,
    CASE_TITLE,
    LOCATION,
    SUSPECTS,
    EVIDENCE_ITEMS
)


def test_authoritative_case_structure():
    case = get_authoritative_case()
    assert case["title"] == "The Vanishing Aurora Diamond"
    assert case["location"] == "Northbridge Museum, Grand Gallery"
    assert case["case_id"] == "001"
    assert "incident" in case
    assert "suspects" in case
    assert "evidence" in case


def test_incident_timeline_and_conditions():
    case = get_authoritative_case()
    incident = case["incident"]
    events = incident["events"]
    assert len(events) == 3
    times = [e["time"] for e in events]
    assert "8:00 PM" in times
    assert "8:20 PM - 8:24 PM" in times
    assert "8:30 PM" in times

    conditions = incident["key_conditions"]
    assert any("Glass remained intact" in c for c in conditions)
    assert any("Electronic lock is battery-backed" in c for c in conditions)
    assert any("Valid-card access is recorded" in c for c in conditions)


def test_four_suspects_present_and_accurate():
    case = get_authoritative_case()
    suspects = case["suspects"]
    assert len(suspects) == 4

    names = [s["name"] for s in suspects]
    assert "Lena Ortiz" in names
    assert "Theo Park" in names
    assert "Arjun Vale" in names
    assert "Sofia Reed" in names

    # Verify specific details
    arjun = next(s for s in suspects if s["name"] == "Arjun Vale")
    assert "large private debt" in arjun["background"]
    assert "card opened archive at 8:12" in arjun["card_activity"]
    assert "card opened display case at 8:23" in arjun["card_activity"]
    assert "flat catalogue folder" in arjun["movement"]

    theo = next(s for s in suspects if s["name"] == "Theo Park")
    assert "continuously from 8:15 to 8:29" in theo["movement"]

    lena = next(s for s in suspects if s["name"] == "Lena Ortiz")
    assert "wet courtyard" in lena["movement"]

    sofia = next(s for s in suspects if s["name"] == "Sofia Reed")
    assert "Three guests remember speaking with her" in sofia["movement"]


def test_evidence_items_a_through_g():
    case = get_authoritative_case()
    evidence = case["evidence"]
    assert len(evidence) == 7

    evidence_ids = [e["id"] for e in evidence]
    assert evidence_ids == ["A", "B", "C", "D", "E", "F", "G"]

    # Verify key evidence item texts
    ev_map = {e["id"]: e["description"] for e in evidence}
    assert "battery-backed" in ev_map["A"]
    assert "Arjun Vale's card opened display case at 8:23 PM" in ev_map["B"]
    assert "jacket inside archive" in ev_map["C"]
    assert "catalogue folder" in ev_map["D"]
    assert "Blue velvet fibers" in ev_map["E"]
    assert "Muddy shoeprint" in ev_map["F"]
    assert "insurance pays museum" in ev_map["G"]


def test_modified_case_removes_only_evidence_e():
    orig_case = get_authoritative_case()
    mod_case = get_modified_case()

    orig_ids = [e["id"] for e in orig_case["evidence"]]
    mod_ids = [e["id"] for e in mod_case["evidence"]]

    assert "E" in orig_ids
    assert "E" not in mod_ids
    assert len(mod_ids) == 6
    assert mod_ids == ["A", "B", "C", "D", "F", "G"]

    # Ensure other components are identical
    assert orig_case["suspects"] == mod_case["suspects"]
    assert orig_case["incident"] == mod_case["incident"]
