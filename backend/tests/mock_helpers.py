"""Mock data and handlers for offline test execution."""

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
    TimelineItem(time="8:00 PM", event="Diamond locked in glass display case.", category="FACT", source="Exhibition Log"),
    TimelineItem(time="8:12 PM", event="Arjun's card opens archive.", category="FACT", source="Electronic Lock Log"),
    TimelineItem(time="8:15 PM - 8:29 PM", event="Theo Park seen continuously on stage.", category="FACT", source="Video Camera"),
    TimelineItem(time="8:19 PM - 8:26 PM", event="Lena restarts basement generator.", category="INFERENCE", source="Lena Statement"),
    TimelineItem(time="8:20 PM", event="Lena's card opens basement door.", category="FACT", source="Electronic Lock Log"),
    TimelineItem(time="8:20 PM - 8:24 PM", event="Power failure in museum.", category="FACT", source="Power Monitor"),
    TimelineItem(time="8:23 PM", event="Arjun's card opens display case.", category="FACT", source="Electronic Lock Log"),
    TimelineItem(time="8:25 PM", event="Arjun leaves archive carrying flat catalogue folder.", category="FACT", source="Security Camera"),
    TimelineItem(time="8:30 PM", event="Diamond discovered missing.", category="FACT", source="Curator Report")
]

MOCK_DETECTIVE_OUTPUT = DetectiveOutput(
    timeline=MOCK_TIMELINE,
    confirmed_facts=[
        "Electronic lock is battery-backed and recorded valid card access during blackout.",
        "Arjun Vale's card opened display case at 8:23 PM.",
        "Arjun was recorded leaving archive with a folder at 8:25 PM.",
        "Diamond missing at 8:30 PM with glass intact."
    ],
    important_time_window="8:20 PM - 8:24 PM (Museum power failure)",
    open_questions=[
        "Who was physically in possession of Arjun's card at 8:23 PM?",
        "What was inside the folder Arjun carried at 8:25 PM?"
    ]
)

MOCK_EVIDENCE_ANALYSIS_ORIGINAL = [
    EvidenceItemAnalysis(
        id="A",
        observation="Electronic lock is battery-backed and records valid-card access during power failure.",
        classification="FACT",
        strength="STRONG",
        alternative_explanation="Lock system hardware malfunction could record erroneous data, though highly improbable.",
        contradiction="None."
    ),
    EvidenceItemAnalysis(
        id="B",
        observation="Arjun Vale's card opened display case at 8:23 PM.",
        classification="FACT",
        strength="STRONG",
        alternative_explanation="Card was taken or cloned without Arjun's immediate knowledge while he was in the archive.",
        contradiction="Contradicts Arjun's claim that card remained in his jacket inside archive."
    ),
    EvidenceItemAnalysis(
        id="C",
        observation="Arjun says his card remained in his jacket inside archive.",
        classification="INFERENCE",
        strength="WEAK",
        alternative_explanation="Arjun is being truthful and someone took the card, or Arjun is being untruthful.",
        contradiction="Directly contradicts electronic lock log B recording card swipe at 8:23 PM."
    ),
    EvidenceItemAnalysis(
        id="D",
        observation="Camera image at 8:25 shows Arjun leaving archive carrying a flat catalogue folder. Contents not visible.",
        classification="FACT",
        strength="MODERATE",
        alternative_explanation="Folder contained routine museum research papers or catalogues.",
        contradiction="Timing (2 minutes after case opened) creates suspicion."
    ),
    EvidenceItemAnalysis(
        id="E",
        observation="Blue velvet fibers found inside folder. Display cushion is blue velvet.",
        classification="FACT",
        strength="STRONG",
        alternative_explanation="Blue velvet is common in museum archives and display materials.",
        contradiction="Strongly challenges claim of folder holding only unrelated papers."
    ),
    EvidenceItemAnalysis(
        id="F",
        observation="Muddy shoeprint near case matches Lena's boot size. Records show she crossed wet courtyard earlier.",
        classification="FACT",
        strength="WEAK",
        alternative_explanation="Shoeprint was deposited during earlier regular gallery maintenance before the event.",
        contradiction="Lena's verified card log shows her in basement at 8:20 PM."
    ),
    EvidenceItemAnalysis(
        id="G",
        observation="If diamond remains missing, insurance pays museum rather than any named suspect.",
        classification="FACT",
        strength="WEAK",
        alternative_explanation="General financial context; could indicate museum board interest but no suspect direct payout.",
        contradiction="Does not directly exonerate or convict any specific individual."
    )
]

MOCK_SUSPECT_OUTPUT = SuspectOutput(
    suspect_comparison={
        "Arjun Vale": SuspectAnalysis(
            name="Arjun Vale",
            motive="Large private debt creates urgent financial pressure.",
            means="Has access to archive and knowledge of museum security.",
            opportunity="Within museum during the 8:20-8:24 PM blackout.",
            access="His card opened display case at 8:23 PM.",
            alibi_support="Uncorroborated statement that he stayed in archive and card remained in jacket.",
            evidence_against=["Evidence B (card opened case)", "Evidence D (folder at 8:25 PM)", "Evidence E (blue velvet fibers)"],
            evidence_in_favor=["No direct camera footage of him inside Grand Gallery"]
        ),
        "Lena Ortiz": SuspectAnalysis(
            name="Lena Ortiz",
            motive="Recently denied a promotion; possible grievance against museum administration.",
            means="Technical knowledge to manipulate museum power systems.",
            opportunity="Card opened basement at 8:20 PM; generator restarted 8:19-8:26 PM.",
            access="No record of her card opening Grand Gallery or display case.",
            alibi_support="Basement card swipe at 8:20 PM corroborates generator restart location.",
            evidence_against=["Evidence F (muddy bootprint matches her size)"],
            evidence_in_favor=["Records confirm crossing wet courtyard earlier; was in basement at 8:20 PM"]
        ),
        "Theo Park": SuspectAnalysis(
            name="Theo Park",
            motive="Wanted publicity for museum event.",
            means="High profile, but limited clandestine technical access.",
            opportunity="None during blackout window.",
            access="No unauthorized card logs.",
            alibi_support="Very strong: Continuous stage camera footage from 8:15 to 8:29 PM.",
            evidence_against=[],
            evidence_in_favor=["Continuous camera footage completely accounts for his presence during blackout"]
        ),
        "Sofia Reed": SuspectAnalysis(
            name="Sofia Reed",
            motive="Wanted exclusive breaking news story.",
            means="Standard visitor/press access.",
            opportunity="Present in lobby area during blackout.",
            access="No record of gallery access.",
            alibi_support="Strong: Three guests confirm speaking with her during the blackout.",
            evidence_against=[],
            evidence_in_favor=["Three independent witnesses verify presence in lobby"]
        )
    },
    ranking=["Arjun Vale", "Lena Ortiz", "Sofia Reed", "Theo Park"],
    leading_person_of_interest="Arjun Vale",
    reasoning="Arjun Vale is the leading PERSON OF INTEREST due to his card accessing the display case at 8:23 PM, an uncorroborated alibi, and leaving the archive with a folder containing velvet fibers."
)

MOCK_SKEPTIC_OUTPUT = SkepticOutput(
    unsupported_assumptions=[
        "Assuming that Arjun Vale personally swiped his card at 8:23 PM.",
        "Assuming the flat catalogue folder held the diamond rather than standard documents.",
        "Assuming blue velvet fibers are uniquely traceable to the Aurora Diamond cushion without spectrometry."
    ],
    contradictions=[
        "Arjun states card never left his jacket inside the archive, yet lock log records use at 8:23 PM.",
        "Lena's shoeprint was near the case, but she was recorded in the basement at 8:20 PM."
    ],
    alternative_explanations=[
        "An accomplice or unknown third party stole Arjun's card from his jacket in the archive between 8:12 and 8:23 PM.",
        "The power outage was orchestrated by someone else, and Arjun was framed.",
        "The fibers in the folder may be from handling museum exhibition materials during regular duties."
    ],
    missing_evidence=[
        "No visual recording inside the Grand Gallery showing who swiped the card at 8:23 PM.",
        "No visual recording of the folder's interior contents at 8:25 PM.",
        "No latent fingerprint or DNA analysis from the glass case or electronic keypad."
    ],
    questions_that_could_change_conclusion=[
        "Was anyone else seen entering or leaving the archive corridor between 8:12 and 8:25 PM?",
        "Do forensic tests confirm the fibers match the specific dye lot and fiber blend of the diamond cushion?"
    ]
)

MOCK_CHIEF_OUTPUT_ORIGINAL = ChiefOutput(
    leading_person_of_interest="Arjun Vale",
    confidence="MEDIUM",
    reasoning=[
        "Arjun Vale's electronic access card opened the display case at 8:23 PM during the blackout.",
        "His statement that the card stayed in his jacket conflicts directly with access records.",
        "He departed the archive two minutes later carrying a catalogue folder.",
        "Blue velvet fibers consistent with the display cushion were recovered from the folder."
    ],
    strongest_evidence=[
        "Evidence B: Arjun Vale's card opened display case at 8:23 PM.",
        "Evidence E: Blue velvet fibers found inside folder matching display cushion."
    ],
    weakest_evidence=[
        "Evidence F: Bootprint matches Lena's size but she crossed courtyard earlier and was logged in basement.",
        "Evidence G: Insurance payout provides no suspect-specific motive."
    ],
    contradictions=[
        "Arjun's claim that card remained in his jacket contradicts electronic lock records."
    ],
    alternative_explanation=[
        "Third party may have taken Arjun's card from his jacket to open the case, though folder fibers undermine this defense."
    ],
    uncertainty=[
        "Card usage does not prove Arjun personally opened the case.",
        "Camera does not reveal folder contents.",
        "Velvet fibers require rigorous comparative scientific spectrometry."
    ],
    missing_evidence=[
        "Grand Gallery interior surveillance during blackout.",
        "Forensic fingerprint/DNA recovery from display case lock."
    ],
    recommended_next_evidence=[
        "Execute forensic spectrometry on blue velvet fibers against display cushion.",
        "Audit archive corridor access cameras between 8:12 and 8:25 PM."
    ],
    evidence_ids=["B", "C", "D", "E"],
    human_review_required=True,
    evidence_citations=[
        EvidenceCitation(
            claim="Arjun Vale is the leading person of interest.",
            evidence_ids=["B", "C", "D", "E"]
        ),
        EvidenceCitation(
            claim="Display case accessed via authorized card during blackout.",
            evidence_ids=["A", "B"]
        ),
        EvidenceCitation(
            claim="Arjun's statement conflicts with physical access logs.",
            evidence_ids=["B", "C"]
        )
    ]
)

MOCK_CHIEF_OUTPUT_MODIFIED = ChiefOutput(
    leading_person_of_interest="Arjun Vale",
    confidence="LOW",
    reasoning=[
        "Arjun Vale's card opened the display case at 8:23 PM during the blackout.",
        "He was seen leaving the archive with a flat folder at 8:25 PM.",
        "However, without physical fiber evidence connecting the folder to the cushion, the physical link is unproven."
    ],
    strongest_evidence=[
        "Evidence B: Arjun Vale's card opened display case at 8:23 PM."
    ],
    weakest_evidence=[
        "Evidence D: Folder carried by Arjun with completely unknown contents.",
        "Evidence F: Bootprint near case with innocent explanation."
    ],
    contradictions=[
        "Arjun's statement that card remained in jacket conflicts with lock log."
    ],
    alternative_explanation=[
        "Card was stolen or cloned from Arjun's jacket while he worked in the archive.",
        "Lena Ortiz or another individual took advantage of the generator blackout."
    ],
    uncertainty=[
        "Card usage does not prove personal physical access by Arjun.",
        "Complete absence of physical evidence linking Arjun's folder to the diamond."
    ],
    missing_evidence=[
        "Direct physical evidence connecting Arjun's folder to the display case.",
        "Camera footage inside Grand Gallery.",
        "Fingerprint forensics on display case."
    ],
    recommended_next_evidence=[
        "Dust display case for latent fingerprints to identify actual cardholder.",
        "Interview all personnel with archive corridor access."
    ],
    evidence_ids=["B", "C", "D"],
    human_review_required=True,
    evidence_citations=[
        EvidenceCitation(
            claim="Arjun Vale remains a person of interest based on electronic card swipe.",
            evidence_ids=["B", "C"]
        )
    ]
)


def mock_openai_handler(instructions: str, input_data: str, response_model):
    """Dispatcher returning appropriate mock output based on requested response model."""
    if response_model.__name__ == "DetectiveOutput":
        return MOCK_DETECTIVE_OUTPUT
    elif response_model.__name__ == "EvidenceOutput":
        # Check if Evidence E is in the input
        if '"id": "E"' in input_data or "'id': 'E'" in input_data:
            return EvidenceOutput(evidence_analysis=MOCK_EVIDENCE_ANALYSIS_ORIGINAL)
        else:
            filtered = [e for e in MOCK_EVIDENCE_ANALYSIS_ORIGINAL if e.id != "E"]
            return EvidenceOutput(evidence_analysis=filtered)
    elif response_model.__name__ == "SuspectOutput":
        return MOCK_SUSPECT_OUTPUT
    elif response_model.__name__ == "SkepticOutput":
        return MOCK_SKEPTIC_OUTPUT
    elif response_model.__name__ == "ChiefOutput":
        # If Evidence E is omitted in input
        if '"id": "E"' not in input_data and "'id': 'E'" not in input_data:
            return MOCK_CHIEF_OUTPUT_MODIFIED
        return MOCK_CHIEF_OUTPUT_ORIGINAL
    raise ValueError(f"Unknown response model: {response_model}")
