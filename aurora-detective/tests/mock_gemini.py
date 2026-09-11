"""Mock data and handlers for Gemini testing and offline demonstrations."""

from models import (
    DetectiveOutput,
    TimelineEvent,
    EvidenceOutput,
    EvidenceItemAnalysis,
    SuspectOutput,
    SuspectAnalysis,
    SkepticOutput,
    ChiefOutput,
    EvidenceCitation
)

MOCK_TIMELINE = [
    TimelineEvent(time="8:00 PM", description="Aurora Diamond confirmed inside locked display case in Grand Gallery.", category="FACT", source="Curator Log"),
    TimelineEvent(time="8:12 PM", description="Arjun Vale's card opened archive door.", category="FACT", source="Electronic Lock Log"),
    TimelineEvent(time="8:15 PM – 8:29 PM", description="Theo Park seen continuously on stage.", category="FACT", source="Auditorium Security Camera"),
    TimelineEvent(time="8:19 PM – 8:26 PM", description="Lena Ortiz says she restarted the basement generator.", category="INFERENCE", source="Lena Statement"),
    TimelineEvent(time="8:20 PM", description="Lena Ortiz's card opened basement door.", category="FACT", source="Electronic Lock Log"),
    TimelineEvent(time="8:20 PM – 8:24 PM", description="Power failure occurs throughout museum (Critical opportunity window).", category="FACT", source="Power Monitor"),
    TimelineEvent(time="8:23 PM", description="Arjun Vale's card opened the display case.", category="FACT", source="Electronic Lock Log"),
    TimelineEvent(time="8:25 PM", description="Camera shows Arjun leaving archive carrying flat catalogue folder (contents not visible).", category="FACT", source="Archive Security Camera"),
    TimelineEvent(time="8:30 PM", description="Aurora Diamond discovered missing. Glass remained intact.", category="FACT", source="Gallery Incident Report")
]

MOCK_DETECTIVE_OUTPUT = DetectiveOutput(
    timeline=MOCK_TIMELINE,
    confirmed_facts=[
        "Aurora Diamond was confirmed in case at 8:00 PM and discovered missing at 8:30 PM with glass intact.",
        "Power failure occurred between 8:20 PM and 8:24 PM.",
        "Electronic lock is battery-backed and recorded valid-card access during the power failure.",
        "Arjun Vale's card opened the display case at 8:23 PM.",
        "Arjun Vale left the archive carrying a flat catalogue folder at 8:25 PM.",
        "Theo Park was continuously visible on stage from 8:15 PM to 8:29 PM."
    ],
    critical_opportunity_window="8:20 PM – 8:24 PM (Power Failure)",
    unknowns=[
        "Identity of the individual physically holding and swiping Arjun's card at 8:23 PM.",
        "Exact contents of the flat catalogue folder carried by Arjun at 8:25 PM.",
        "Activities of all suspects during the exact moment of the 8:23 PM case access."
    ],
    open_questions=[
        "Did anyone enter the archive between 8:12 PM and 8:23 PM while Arjun was inside?",
        "Do laboratory tests confirm the blue velvet fibers uniquely match the Aurora Diamond cushion?"
    ]
)

MOCK_EVIDENCE_ORIGINAL = [
    EvidenceItemAnalysis(
        id="A",
        description="Electronic lock records show valid-card access during the power failure.",
        classification="FACT",
        strength="STRONG",
        supports="Confirms that the display case was unlocked using an authorized credential during the blackout.",
        alternative_explanation="System logging error (very low probability given battery-backed design)."
    ),
    EvidenceItemAnalysis(
        id="B",
        description="Arjun Vale's card opened the display case at 8:23 PM.",
        classification="FACT",
        strength="STRONG",
        supports="Confirms Arjun's card credential unlocked the case at 8:23 PM.",
        alternative_explanation="Another party took or cloned Arjun's card from his jacket without his knowledge while he worked in the archive."
    ),
    EvidenceItemAnalysis(
        id="C",
        description="Arjun says his card remained in his jacket inside the archive.",
        classification="INFERENCE",
        strength="WEAK",
        supports="Arjun's personal defense that he did not leave the archive or swipe the card.",
        alternative_explanation="Arjun is fabricating the statement, or the card was indeed stolen from his unattended jacket."
    ),
    EvidenceItemAnalysis(
        id="D",
        description="At 8:25 PM camera shows Arjun leaving the archive carrying a flat catalogue folder. Contents are not visible.",
        classification="FACT",
        strength="MODERATE",
        supports="Demonstrates departure with an object two minutes after display case unlock.",
        alternative_explanation="Folder contained routine archival research papers, museum drawings, or exhibition catalogues."
    ),
    EvidenceItemAnalysis(
        id="E",
        description="Blue velvet fibers were found inside the folder. The display cushion is blue velvet.",
        classification="FACT",
        strength="STRONG",
        supports="Physical fiber match between folder interior and display case cushion.",
        alternative_explanation="Fibers were transferred during earlier routine curation of museum exhibits using velvet materials."
    ),
    EvidenceItemAnalysis(
        id="F",
        description="A muddy shoeprint near the case matches Lena's boot size. Records show she crossed the wet courtyard earlier.",
        classification="FACT",
        strength="WEAK",
        supports="Possible presence of Lena near the case at some point.",
        alternative_explanation="Shoeprint was deposited earlier in the evening during regular duties before the power failure."
    ),
    EvidenceItemAnalysis(
        id="G",
        description="Insurance pays the museum rather than any named suspect if the diamond remains missing.",
        classification="FACT",
        strength="WEAK",
        supports="Financial context of museum coverage.",
        alternative_explanation="Standard institutional policy; does not indicate direct motive for any individual employee."
    )
]

MOCK_SUSPECT_OUTPUT = SuspectOutput(
    suspect_comparison={
        "Arjun Vale": SuspectAnalysis(
            name="Arjun Vale",
            motive="Large private debt creates urgent financial distress.",
            means="Has archive access and knowledge of museum security procedures.",
            opportunity="Inside the museum during the 8:20–8:24 PM blackout.",
            access="His card opened display case at 8:23 PM.",
            alibi="Says he worked in archive and card remained in jacket inside archive (uncorroborated).",
            evidence_for=["No camera recording inside Grand Gallery itself directly shows him opening the case."],
            evidence_against=[
                "Evidence B: His card opened display case at 8:23 PM.",
                "Evidence D: Left archive carrying folder at 8:25 PM.",
                "Evidence E: Blue velvet fibers found inside folder matching display cushion."
            ],
            contradictions=[
                "Arjun's claim that card remained in jacket directly contradicts electronic lock log B recording card swipe at 8:23 PM."
            ],
            overall_assessment="Leading PERSON OF INTEREST due to electronic card access, uncorroborated alibi, and physical fiber trace."
        ),
        "Lena Ortiz": SuspectAnalysis(
            name="Lena Ortiz",
            motive="Recently denied promotion; potential workplace grievance.",
            means="Technical facility to access electrical infrastructure and restart generator.",
            opportunity="In basement from 8:19–8:26 PM during blackout.",
            access="Card opened basement at 8:20 PM; no card record of display case access.",
            alibi="Card swipe at 8:20 PM corroborates presence at basement generator.",
            evidence_for=[
                "Verified basement card log at 8:20 PM accounts for location during blackout.",
                "Prior courtyard crossing explains muddy boots."
            ],
            evidence_against=["Evidence F: Muddy shoeprint near case matches her boot size."],
            contradictions=["None between her statement and basement logs."],
            overall_assessment="Low priority PERSON OF INTEREST; generator restart timeline is corroborated by lock logs."
        ),
        "Theo Park": SuspectAnalysis(
            name="Theo Park",
            motive="Wanted publicity for museum event.",
            means="Limited technical clandestine access.",
            opportunity="None during the 8:20–8:24 PM blackout.",
            access="No unauthorized card access recorded.",
            alibi="Continuous stage camera footage from 8:15–8:29 PM.",
            evidence_for=["Continuous unbroken video record completely verifies his stage alibi."],
            evidence_against=[],
            contradictions=["None."],
            overall_assessment="Exonerated from direct physical theft during blackout due to continuous visual alibi."
        ),
        "Sofia Reed": SuspectAnalysis(
            name="Sofia Reed",
            motive="Wanted an exclusive breaking news story.",
            means="Standard visitor/press access.",
            opportunity="Present in lobby area during blackout.",
            access="No electronic access to Grand Gallery or locked display case.",
            alibi="Three guests confirm speaking with her in the lobby during the blackout.",
            evidence_for=["Three independent witness statements corroborate her presence in the lobby."],
            evidence_against=[],
            contradictions=["None."],
            overall_assessment="Unlikely person of interest; verified lobby presence and lack of access credentials."
        )
    },
    ranking=["Arjun Vale", "Lena Ortiz", "Sofia Reed", "Theo Park"],
    leading_person_of_interest="Arjun Vale",
    reasoning="Arjun Vale is designated the leading PERSON OF INTEREST based on electronic lock log B showing his card accessed the case at 8:23 PM, his departure with a folder at 8:25 PM, and blue velvet fibers consistent with the display cushion."
)

MOCK_SKEPTIC_OUTPUT = SkepticOutput(
    unsupported_assumptions=[
        "Assuming that Arjun Vale personally swiped his card at 8:23 PM without visual confirmation.",
        "Assuming the flat catalogue folder held the diamond rather than standard archival documents.",
        "Assuming the blue velvet fibers uniquely originated from the Aurora Diamond cushion without scientific spectrometry."
    ],
    contradictions=[
        "Arjun's statement that card stayed in jacket contradicts 8:23 PM electronic log.",
        "Lena's print found near case vs her verified card swipe in basement at 8:20 PM."
    ],
    alternative_explanations=[
        "An opportunistic accomplice or third party lifted Arjun's card from his jacket while he was distracted in the archive.",
        "The fibers in the folder may have transferred during prior legitimate handling of museum exhibition materials.",
        "Arjun is being framed by someone aware of his debt and schedule."
    ],
    missing_evidence=[
        "No surveillance camera inside Grand Gallery during the blackout.",
        "No visual recording of the folder's interior contents at 8:25 PM.",
        "No latent fingerprint or DNA recovery from the display case glass or keypad."
    ],
    questions_to_stress_test=[
        "Did any other person enter the archive hallway between 8:12 PM and 8:25 PM?",
        "Does laboratory spectrometry confirm the fibers match the specific dye lot and weave of the display cushion?"
    ]
)

MOCK_CHIEF_OUTPUT_ORIGINAL = ChiefOutput(
    leading_person_of_interest="Arjun Vale",
    confidence_score=78,
    confidence_level="HIGH",
    confidence_explanation=(
        "Arjun Vale is designated the leading PERSON OF INTEREST based on electronic lock logs "
        "demonstrating his authorized card opened the display case at 8:23 PM during the blackout, "
        "combined with his departure with a folder containing blue velvet fibers matching the display cushion. "
        "However, the score is limited to 78/100 (HIGH) because electronic access does not conclusively establish "
        "personal physical possession, folder contents were not visible on camera, and fiber analysis requires formal "
        "comparative spectrometry."
    ),
    supporting_evidence=[
        "Evidence B: Arjun Vale's electronic card opened display case at 8:23 PM during blackout.",
        "Evidence E: Blue velvet fibers found inside folder matching display cushion.",
        "Evidence D: Arjun departed archive carrying flat catalogue folder at 8:25 PM."
    ],
    contradictory_evidence=[
        "Evidence C: Arjun states his card remained in his jacket inside the archive.",
        "Evidence F: Muddy shoeprint near case matches Lena's boots, though she crossed the courtyard earlier."
    ],
    unresolved_uncertainties=[
        "Electronic card swipe establishes card usage, not that Arjun personally swiped it.",
        "Catalogue folder contents were not visible on archive CCTV.",
        "Blue velvet fibers lack scientific comparative spectrometry confirmation.",
        "The 8:30 PM discovery time does not establish the exact moment of theft."
    ],
    alternative_theories=[
        "An opportunistic third party took or cloned Arjun's card from his jacket while he was in the archive.",
        "Velvet fibers transferred during legitimate prior handling of museum display textiles."
    ],
    recommended_next_evidence=[
        "Conduct forensic spectrometry and dye-lot analysis on blue velvet fibers against display cushion.",
        "Audit archive corridor access logs and security footage between 8:12 PM and 8:25 PM.",
        "Examine display case keypad and frame for latent fingerprints or DNA."
    ],
    evidence_citations=[
        EvidenceCitation(
            claim="Arjun Vale is designated the leading PERSON OF INTEREST.",
            evidence_ids=["B", "C", "D", "E"]
        ),
        EvidenceCitation(
            claim="Display case unlocked via authorized card during blackout.",
            evidence_ids=["A", "B"]
        ),
        EvidenceCitation(
            claim="Arjun's statement conflicts with physical access logs.",
            evidence_ids=["B", "C"]
        )
    ],
    human_review_required=True
)

MOCK_CHIEF_OUTPUT_MODIFIED = ChiefOutput(
    leading_person_of_interest="Arjun Vale",
    confidence_score=52,
    confidence_level="MEDIUM",
    confidence_explanation=(
        "Without Evidence E (blue velvet fibers), the physical nexus tying Arjun's folder to the stolen "
        "diamond's container is entirely absent. While Arjun Vale remains the leading PERSON OF INTEREST due to his "
        "card swipe at 8:23 PM, confidence drops to 52/100 (MEDIUM) because alternative theories—particularly that his card "
        "was removed from his jacket without his knowledge during the blackout—become significantly more plausible."
    ),
    supporting_evidence=[
        "Evidence B: Arjun Vale's card opened display case at 8:23 PM."
    ],
    contradictory_evidence=[
        "Evidence C: Arjun claims card remained in jacket inside archive.",
        "Evidence D: Folder contents are completely unverified by CCTV.",
        "Evidence F: Muddy shoeprint with known earlier innocent explanation."
    ],
    unresolved_uncertainties=[
        "No physical evidence connects Arjun or his folder to the display case or diamond.",
        "Identity of card user at 8:23 PM remains uncorroborated by visual surveillance.",
        "Lack of camera coverage in Grand Gallery during the 8:20-8:24 PM blackout."
    ],
    alternative_theories=[
        "Arjun's card was stolen from his jacket inside the archive by an unknown individual who executed the theft.",
        "Opportunistic theft by museum insider during generator blackout."
    ],
    recommended_next_evidence=[
        "Review all entry/exit card records for archive perimeter during the blackout window.",
        "Conduct latent print recovery on display case housing and glass.",
        "Interview museum personnel regarding movements between 8:19 PM and 8:26 PM."
    ],
    evidence_citations=[
        EvidenceCitation(
            claim="Arjun Vale remains a PERSON OF INTEREST based solely on card log.",
            evidence_ids=["B", "C"]
        )
    ],
    human_review_required=True
)


def default_mock_gemini_handler(system_instruction: str, prompt: str, response_model):
    """Dispatcher returning appropriate mock output for Gemini structured calls."""
    name = response_model.__name__
    if name == "ParsedCase":
        from case_data import _heuristic_fallback_parse
        return response_model.model_validate(_heuristic_fallback_parse(prompt))
    elif name == "DetectiveOutput":
        return MOCK_DETECTIVE_OUTPUT
    elif name == "EvidenceOutput":
        if '"id": "E"' in prompt or "'id': 'E'" in prompt or "E1" in prompt:
            return EvidenceOutput(evidence_analysis=MOCK_EVIDENCE_ORIGINAL)
        filtered = [e for e in MOCK_EVIDENCE_ORIGINAL if e.id != "E"]
        return EvidenceOutput(evidence_analysis=filtered)
    elif name == "SuspectOutput":
        return MOCK_SUSPECT_OUTPUT
    elif name == "SkepticOutput":
        return MOCK_SKEPTIC_OUTPUT
    elif name == "ChiefOutput":
        if '"id": "E"' not in prompt and "'id': 'E'" not in prompt and "E1" not in prompt:
            return MOCK_CHIEF_OUTPUT_MODIFIED
        return MOCK_CHIEF_OUTPUT_ORIGINAL
    raise ValueError(f"Unknown response model: {response_model}")
