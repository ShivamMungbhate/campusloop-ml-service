
def assess_escalation(
    related_complaint_count: int,
    current_priority: str | None,
) -> dict:
    """
    Prototype escalation policy.

    related_complaint_count includes the original complaint
    and all reports linked to the same issue.
    """

    if related_complaint_count < 1:
        raise ValueError(
            "Related complaint count must be at least 1"
        )

    valid_priorities = {"Urgent", "High", "Medium", "Low"}

    if current_priority not in valid_priorities:
        current_priority = None

    if related_complaint_count >= 10:
        escalation_level = "High"
        needs_review = True
        reason = (
            "10 or more related reports: "
            "high-level admin review recommended."
        )

    elif related_complaint_count >= 3:
        escalation_level = "Medium"
        needs_review = True
        reason = (
            "3 or more related reports: "
            "admin review recommended."
        )

    else:
        escalation_level = "None"
        needs_review = current_priority == "Urgent"
        reason = (
            "No report-count escalation threshold reached."
        )

    return {
        "relatedComplaintCount": related_complaint_count,
        "currentPriority": current_priority,
        "escalationLevel": escalation_level,
        "escalationNeedsReview": needs_review,
        "escalationReason": reason,
        "escalationSource": "RuleBasedPrototype",
    }


if __name__ == "__main__":
    test_cases = [
        (1, "High"),
        (3, "High"),
        (5, "Medium"),
        (10, "High"),
    ]

    for count, priority in test_cases:
        print(
            f"\nReports: {count}, Priority: {priority}"
        )
        print(assess_escalation(count, priority))
