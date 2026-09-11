"""Mock agent outputs and response generator for offline and testing usage."""

from app.models import (
    DetectiveOutput,
    TimelineItem,
    EvidenceOutput,
    EvidenceItemAnalysis,
    SuspectOutput,
    SuspectAnalysis,
    SkepticOutput,
    ChiefOutput,
    EvidenceCitation
)

MOCK_TIMELINE = [
    TimelineItem(time="8:00 PM", event="Diamond displayed in locked glass case.", category="FACT", source="Exhibition Record"),
    TimelineItem(time="8:12 PM", event="Arjun's card opens archive door.", category="FACT", source="Electronic Lock Log"),
    TimelineItem(time="8:15 PM - 8:29 PM", event="Theo Park seen continuously on stage.", category="FACT", source="Auditorium Camera"),
    TimelineItem(time="8:19 PM - 8:26 PM", event="Lena restarts basement generator.", category="INFERENCE", source="Lena Statement"),
    TimelineItem(time="8:20 PM", event="Lena's card opens basement door.", category="FACT", source="Electronic Lock Log"),
    TimelineItem(time="8:20 PM - 8:24 PM", event="Power failure occurs in museum.", category="FACT", source="Power Monitor"),
    TimelineItem(time="8:23 PM", event="Arjun's card opens display case.", category="FACT", source="Electronic Lock Log"),
    TimelineItem(time="8:25 PM", event="Arjun leaves archive carrying flat catalogue folder.", category="FACT", source="Security Camera"),
    TimelineItem(time="8:30 PM", event="Diamond discovered missing.", category="FACT", source="Grand Gallery Staff")
]

MOCK_DETECTIVE_OUTPUT = DetectiveOutput(
    timeline=MOCK_TIMELINE,
    confirmed_facts=[
        "Electronic lock is battery-backed and recorded valid-card access during blackout.",
        "Arjun Vale's card opened display case at 8:23 PM.",
        "Glass of display case remained completely intact.",
        "Arjun Vale left archive carrying flat catalogue folder at 8:25 PM.",
        "Diamond discovered missing at 8:30 PM."
    ],
    important_time_window="8:20 PM - 8:24 PM (Museum blackout)",
    open_questions=[
        "Who was physically carrying Arjun Vale's card at 8:23 PM?",
        "What was contained within the catalogue folder at 8:25 PM?"
    ]
)

MOCK_EVIDENCE_ANALYSIS_ORIGINAL = [
    EvidenceItemAnalysis(
        id="A",
        observation="Electronic lock is battery-backed and records valid-card access during power failure.",
        classification="FACT",
        strength="STRONG",
        alternative_explanation="System clock sync delay or rare logic fault.",
        contradiction="None."
    ),
    EvidenceItemAnalysis(
        id="B",
        observation="Arjun Vale's card opened display case at 8:23 PM.",
        classification="FACT",
        strength="STRONG",
        alternative_explanation="Card was appropriated or cloned while Arjun remained in archive.",
        contradiction="Directly contradicts Arjun's claim that card remained in his jacket inside archive."
    ),
    EvidenceItemAnalysis(
        id="C",
        observation="Arjun says his card remained in his jacket inside archive.",
        classification="INFERENCE",
        strength="WEAK",
        alternative_explanation="Arjun may be telling the truth regarding leaving his jacket unattended.",
        contradiction="Conflicts with Electronic Lock Log B registering card usage at 8:23 PM."
    ),
    EvidenceItemAnalysis(
        id="D",
        observation="Camera image at 8:25 shows Arjun leaving archive carrying a flat catalogue folder. Contents are not visible.",
        classification="FACT",
        strength="MODERATE",
        alternative_explanation="Folder carried standard museum archival documents.",
        contradiction="Folder departure occurs just two minutes after case unlock."
    ),
    EvidenceItemAnalysis(
        id="E",
        observation="Blue velvet fibers found inside folder. Display cushion is blue velvet.",
        classification="FACT",
        strength="STRONG",
        alternative_explanation="Velvet fibers could originate from other museum display pieces.",
        contradiction="Undermines innocent explanation of folder's contents."
    ),
    EvidenceItemAnalysis(
        id="F",
        observation="Muddy shoeprint near case matches Lena's boot size. Records show she crossed wet courtyard earlier.",
        classification="FACT",
        strength="WEAK",
        alternative_explanation="Print was deposited prior to the blackout during normal operations.",
        contradiction="Lena's card accessed the basement at 8:20 PM."
    ),
    EvidenceItemAnalysis(
        id="G",
        observation="If diamond remains missing, insurance pays museum rather than any named suspect.",
        classification="FACT",
        strength="WEAK",
        alternative_explanation="Institutional policy without specific suspect payout.",
        contradiction="Does not incriminate any individual suspect."
    )
]

MOCK_SUSPECT_OUTPUT = SuspectOutput(
    suspect_comparison={
        "Arjun Vale": SuspectAnalysis(
            name="Arjun Vale",
            motive="Large private debt creates urgent financial pressure.",
            means="Knowledge of museum security and archive access.",
            opportunity="Present inside museum during blackout window.",
            access="His card opened display case at 8:23 PM.",
            alibi_support="Uncorroborated claim of remaining in archive with card in jacket.",
            evidence_against=["Evidence B (card opened case)", "Evidence D (folder at 8:25 PM)", "Evidence E (blue velvet fibers)"],
            evidence_in_favor=["No camera recording inside Grand Gallery itself"]
        ),
        "Lena Ortiz": SuspectAnalysis(
            name="Lena Ortiz",
            motive="Denied promotion, potential grievance.",
            means="Technical facility with electrical and generator systems.",
            opportunity="Card opened basement at 8:20 PM; generator restarted 8:19-8:26 PM.",
            access="No electronic record of display case access.",
            alibi_support="Basement card log at 8:20 PM corroborates generator restart presence.",
            evidence_against=["Evidence F (shoeprint matches boot size)"],
            evidence_in_favor=["Crossed wet courtyard earlier; basement swipe at 8:20 PM"]
        ),
        "Theo Park": SuspectAnalysis(
            name="Theo Park",
            motive="Desire for publicity for museum event.",
            means="Limited clandestine access.",
            opportunity="None during blackout window.",
            access="No unauthorized access recorded.",
            alibi_support="Complete alibi: Stage camera shows him continuously from 8:15 to 8:29 PM.",
            evidence_against=[],
            evidence_in_favor=["Continuous camera footage completely accounts for presence during blackout"]
        ),
        "Sofia Reed": SuspectAnalysis(
            name="Sofia Reed",
            motive="Desire for exclusive investigative story.",
            means="Standard press access.",
            opportunity="Present in lobby area during blackout.",
            access="No electronic access to gallery recorded.",
            alibi_support="Strong alibi: Three guests confirm speaking with her during blackout.",
            evidence_against=[],
            evidence_in_favor=["Three independent witnesses verify presence in lobby"]
        )
    },
    ranking=["Arjun Vale", "Lena Ortiz", "Sofia Reed", "Theo Park"],
    leading_person_of_interest="Arjun Vale",
    reasoning="Arjun Vale is designated as the leading PERSON OF INTEREST due to his card accessing the display case at 8:23 PM, uncorroborated alibi, and departure carrying a folder containing velvet fibers consistent with the cushion."
)

MOCK_SKEPTIC_OUTPUT = SkepticOutput(
    unsupported_assumptions=[
        "Assuming that Arjun Vale was the person who physically swiped the card at 8:23 PM.",
        "Assuming the folder contained the Aurora Diamond without visual proof.",
        "Assuming velvet fibers originate uniquely from the diamond cushion without scientific spectrometry."
    ],
    contradictions=[
        "Arjun's statement that card stayed in jacket vs 8:23 PM electronic log.",
        "Lena's print found near case vs her verified presence in basement at 8:20 PM."
    ],
    alternative_explanations=[
        "An accomplice or second party lifted Arjun's card while he was in the archive.",
        "Fibers in folder could be transferred from routine archive handling of display materials.",
        "Card was cloned or stolen to frame Arjun during the generator blackout."
    ],
    missing_evidence=[
        "Direct visual surveillance of the display case at 8:23 PM.",
        "Clear visual capture of folder contents at 8:25 PM.",
        "Latent fingerprints or biometric analysis from the electronic keypad."
    ],
    questions_that_could_change_conclusion=[
        "Did any other person enter the archive between 8:12 and 8:23 PM?",
        "Does spectrometry confirm the blue velvet fibers match the diamond cushion specifically?"
    ]
)

MOCK_CHIEF_OUTPUT_ORIGINAL = ChiefOutput(
    leading_person_of_interest="Arjun Vale",
    confidence="MEDIUM",
    reasoning=[
        "Arjun Vale's electronic card opened the display case at 8:23 PM during the blackout.",
        "His statement that his card remained in his jacket inside the archive conflicts with electronic logs.",
        "He left the archive at 8:25 PM carrying a flat catalogue folder.",
        "Blue velvet fibers consistent with the display cushion were found inside the folder."
    ],
    strongest_evidence=[
        "Evidence B: Arjun Vale's card opened display case at 8:23 PM.",
        "Evidence E: Blue velvet fibers found inside folder matching display cushion."
    ],
    weakest_evidence=[
        "Evidence F: Bootprint matches Lena's size, but she crossed courtyard earlier.",
        "Evidence G: Insurance payout provides no suspect-specific motive."
    ],
    contradictions=[
        "Arjun's claim that card stayed in jacket contradicts 8:23 PM lock record."
    ],
    alternative_explanation=[
        "Card may have been accessed by a third party in the archive, though folder fibers weaken this defense."
    ],
    uncertainty=[
        "Card usage does not prove Arjun personally opened the case.",
        "Camera does not show folder contents.",
        "Velvet fibers require further scientific comparison."
    ],
    missing_evidence=[
        "Direct footage of who used the card at 8:23 PM.",
        "Fingerprint analysis on display case lock."
    ],
    recommended_next_evidence=[
        "Forensic spectrometry comparison of blue velvet fibers.",
        "Audit archive corridor access records between 8:12 and 8:25 PM."
    ],
    evidence_ids=["B", "C", "D", "E"],
    human_review_required=True,
    evidence_citations=[
        EvidenceCitation(
            claim="Arjun Vale is the leading person of interest.",
            evidence_ids=["B", "C", "D", "E"]
        ),
        EvidenceCitation(
            claim="Display case opened with authorized card during blackout.",
            evidence_ids=["A", "B"]
        ),
        EvidenceCitation(
            claim="Arjun's statement conflicts with electronic access logs.",
            evidence_ids=["B", "C"]
        )
    ]
)

MOCK_CHIEF_OUTPUT_MODIFIED = ChiefOutput(
    leading_person_of_interest="Arjun Vale",
    confidence="LOW",
    reasoning=[
        "Arjun Vale's card opened the display case at 8:23 PM.",
        "He was seen leaving the archive with a folder at 8:25 PM.",
        "However, absent physical fiber evidence connecting the folder to the cushion, the physical link is unproven."
    ],
    strongest_evidence=[
        "Evidence B: Arjun Vale's card opened display case at 8:23 PM."
    ],
    weakest_evidence=[
        "Evidence D: Folder carried by Arjun with completely unverified contents.",
        "Evidence F: Muddy shoeprint with known earlier innocent explanation."
    ],
    contradictions=[
        "Arjun's statement that card stayed in jacket conflicts with lock log."
    ],
    alternative_explanation=[
        "Card was taken or cloned by an opportunistic party during the generator blackout."
    ],
    uncertainty=[
        "Card usage does not prove personal physical access by Arjun.",
        "No physical evidence connects Arjun's folder to the stolen diamond."
    ],
    missing_evidence=[
        "Physical evidence connecting folder to diamond cushion.",
        "Surveillance footage inside Grand Gallery.",
        "Fingerprints on display case keypad."
    ],
    recommended_next_evidence=[
        "Latent fingerprint recovery on the display case.",
        "Corridor badge audits around the archive."
    ],
    evidence_ids=["B", "C", "D"],
    human_review_required=True,
    evidence_citations=[
        EvidenceCitation(
            claim="Arjun Vale remains a person of interest based on card log.",
            evidence_ids=["B", "C"]
        )
    ]
)


def default_mock_handler(instructions: str, input_data: str, response_model):
    """Mock handler mapping response models to mock investigation outputs."""
    name = response_model.__name__
    if name == "DetectiveOutput":
        return MOCK_DETECTIVE_OUTPUT
    elif name == "EvidenceOutput":
        if '"id": "E"' in input_data or "'id': 'E'" in input_data:
            return EvidenceOutput(evidence_analysis=MOCK_EVIDENCE_ANALYSIS_ORIGINAL)
        filtered = [e for e in MOCK_EVIDENCE_ANALYSIS_ORIGINAL if e.id != "E"]
        return EvidenceOutput(evidence_analysis=filtered)
    elif name == "SuspectOutput":
        return MOCK_SUSPECT_OUTPUT
    elif name == "SkepticOutput":
        return MOCK_SKEPTIC_OUTPUT
    elif name == "ChiefOutput":
        if '"id": "E"' not in input_data and "'id': 'E'" not in input_data:
            return MOCK_CHIEF_OUTPUT_MODIFIED
        return MOCK_CHIEF_OUTPUT_ORIGINAL
    raise ValueError(f"Unknown response model: {response_model}")
