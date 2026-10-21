
import re
from transformers import pipeline

MODEL_NAME = "facebook/bart-large-mnli"

CATEGORIES = [
    "Electrical Maintenance",
    "Plumbing and Water Supply",
    "Housekeeping and Sanitation",
    "IT Support",
    "Hostel Administration",
    "Library Administration",
    "Laboratory Maintenance",
    "Campus Security",
    "Civil Maintenance",
    "Other",
]

# Keyword rules for clear electrical complaints.
ELECTRICAL_PATTERNS = [
    r"\bno electricity\b",
    r"\bdoes not have electricity\b",
    r"\bdoesn't have electricity\b",
    r"\bwithout electricity\b",
    r"\bno power\b",
    r"\bpower outage\b",
    r"\bpower cut\b",
    r"\belectricity (problem|issue|failure)\b",
    r"\belectrical (problem|issue|failure)\b",
    r"\bpower supply (failure|problem|issue)\b",
    r"\belectricity supply (failure|problem|issue)\b",
    r"\b(power|electricity) is (unavailable|down|not working)\b",
    r"\b(lights?|fans?) (are|is) not working\b",
]

print("Loading classification model...")

classifier = pipeline(
    "zero-shot-classification",
    model=MODEL_NAME,
)

print("Model loaded successfully!")


def categorize_complaint(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Complaint text cannot be empty")

    normalized = re.sub(r"\s+", " ", text.lower()).strip()

    # Explicit keyword override for clear electrical issues.
    if any(
        re.search(pattern, normalized)
        for pattern in ELECTRICAL_PATTERNS
    ):
        return {
            "category": "Electrical Maintenance",
            "confidence": None,
            "all_scores": {},
            "classificationSource": "KeywordRule",
            "needsReview": True,
        }

    # Use the ML classifier for all other complaints.
    result = classifier(
        text.strip(),
        candidate_labels=CATEGORIES,
    )

    return {
        "category": result["labels"][0],
        "confidence": round(float(result["scores"][0]), 4),
        "all_scores": {
            label: round(float(score), 4)
            for label, score in zip(
                result["labels"], result["scores"]
            )
        },
        "classificationSource": "ZeroShotModel",
        "needsReview": True,
    }


if __name__ == "__main__":
    examples = [
        "Staff room does not have electricity",
        "There is no water supply in the hostel bathroom.",
        "The library Wi-Fi is not working.",
        "There are exposed electrical wires in the classroom.",
    ]

    for complaint in examples:
        print(f"\nComplaint: {complaint}")
        print(categorize_complaint(complaint))
