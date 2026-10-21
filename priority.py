
import re


RULES = [
    # URGENT: Immediate safety hazards
    (
        "Urgent",
        [
            r"\bexposed electrical wires?\b",
            r"\blive wires?\b",
            r"\blive electrical wires?\b",
            r"\belectric shock\b",
            r"\belectrical sparks?\b",
            r"\bsparking\b",
            r"\bburning smell\b",
            r"\belectrical fire\b",
            r"\bfire\b",
            r"\bgas leak\b",
            r"\bimmediate danger\b",
            r"\blife.?threatening\b",
        ],
    ),

    # HIGH: Electricity or essential services unavailable
    (
        "High",
        [
            r"\bno electricity\b",
            r"\bno electric(?:ity)? supply\b",
            r"\bno power\b",
            r"\bpower outage\b",
            r"\bpower cut\b",
            r"\belectricity.{0,40}\b(unavailable|not available|not working|cut off|cut)\b",
            r"\b(?:does not|doesn't|do not|don't)\s+have electricity\b",
            r"\bwithout electricity\b",
            r"\belectricity supply.{0,30}\b(stopped|failed|unavailable|not working)\b",
            r"\bpower supply.{0,30}\b(stopped|failed|unavailable|not working)\b",
            r"\b(?:staff room|classroom|laboratory|lab|hostel|library|building|campus)\b.{0,40}\b(no electricity|no power|without electricity)\b",
            r"\bno drinking water\b",
            r"\bno water supply\b",
            r"\bwater supply.{0,30}\b(stopped|unavailable|not working)\b",
            r"\b(?:unable|cannot|can't)\b.{0,40}\bwater\b",
            r"\bwater\b.{0,30}\b(unavailable|not available|not working|stopped)\b",
            r"\bdrinking water\b.{0,30}\b(unavailable|not available|not working)\b",
            r"\bwater supply\b",
            r"\bsevere sanitation\b",
            r"\bmajor sewage\b",
            r"\bmultiple (students|classrooms|hostels)\b",
            r"\bdoes not have electricity\b",
        ],
    ),

    # MEDIUM: Disruptions that need attention
    (
        "Medium",
        [
            r"\belectricity problem\b",
            r"\belectrical problem\b",
            r"\belectricity issue\b",
            r"\belectrical issue\b",
            r"\blights?\b.{0,30}\b(not working|broken|not turning on)\b",
            r"\b(?:fan|fans)\b.{0,30}\b(not working|broken|not turning on)\b",
            r"\bwi.?fi\b",
            r"\binternet.{0,20}\b(not working|unavailable|down)\b",
            r"\bprojector\b",
            r"\bbroken fan\b",
            r"\broutine maintenance\b",
        ],
    ),

    # LOW: Non-urgent improvements and suggestions
    (
        "Low",
        [
            r"\bpainting suggestion\b",
            r"\bcosmetic improvement\b",
            r"\bnew decoration\b",
            r"\bfeature suggestion\b",
            r"\bnon.?essential\b",
            r"\bneeds? more chairs\b",
            r"\bnot enough chairs\b",
            r"\bneeds? more benches\b",
            r"\bnot enough benches\b",
        ],
    ),
]


def assess_priority(text: str) -> dict:
    """
    Assess complaint priority using initial keyword-based rules.

    This is a prototype, not a trained priority prediction model.
    Results should be reviewed by a human.
    """
    if not text or not text.strip():
        raise ValueError("Complaint text cannot be empty")

    normalized = re.sub(r"\s+", " ", text.lower()).strip()

    for priority, patterns in RULES:
        for pattern in patterns:
            if re.search(pattern, normalized):
                return {
                    "priority": priority,
                    "prioritySource": "RuleBased",
                    "priorityReason": (
                        f"Matched an initial {priority.lower()}-priority "
                        "keyword rule. Please review the assessment."
                    ),
                    "priorityNeedsReview": True,
                }

    # If no rule matches, leave priority unassigned and request review.
    return {
        "priority": None,
        "prioritySource": None,
        "priorityReason": "No priority rule matched. Human review is required.",
        "priorityNeedsReview": True,
    }


if __name__ == "__main__":
    examples = [
        "There are exposed electrical wires in the hostel.",
        "There is no drinking water in the hostel.",
        "The library Wi-Fi is not working.",
        "I suggest new decoration for the classroom.",
        "The library needs more chairs.",
        "Hostel water problem. Students are unable to get water in the hostel bathrooms.",
        "Staff room does not have electricity.",
        "There is no power in the classroom.",
        "The staff room lights are not working.",
        "There is sparking from an electrical socket.",
        "The classroom needs a new notice board.",
    ]

    for complaint in examples:
        print(f"\nComplaint: {complaint}")
        print(assess_priority(complaint))
