
from sentence_transformers import SentenceTransformer, util

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Initial threshold: evaluate it using real examples before production.
SIMILARITY_THRESHOLD = 0.75


SAMPLE_COMPLAINTS = [
    {
        "id": "CMP001",
        "issueId": "ISSUE_WATER_01",
        "title": "No water supply in hostel",
        "text": "There is no water supply in the hostel bathrooms."
    },
    {
        "id": "CMP002",
        "issueId": "ISSUE_WATER_01",
        "title": "Hostel drinking water unavailable",
        "text": "Students cannot get drinking water in the hostel."
    },
    {
        "id": "CMP003",
        "issueId": "ISSUE_WIFI_01",
        "title": "Library Wi-Fi not working",
        "text": "The internet connection in the library is down."
    },
    {
        "id": "CMP004",
        "issueId": "ISSUE_FAN_01",
        "title": "Broken classroom fan",
        "text": "The ceiling fan in our classroom is not working."
    },
    {
        "id": "CMP005",
        "issueId": "ISSUE_PIPE_01",
        "title": "Hostel bathroom leaking",
        "text": "Water is leaking from a pipe in the hostel bathroom."
    },
    {
        "id": "CMP006",
        "issueId": "ISSUE_WIRES_01",
        "title": "Exposed electrical wires",
        "text": "Dangerous exposed electrical wires are present in the hostel."
    },
    {
        "id": "CMP007",
        "issueId": "ISSUE_CHAIRS_01",
        "title": "Library needs more chairs",
        "text": "There are not enough chairs for students in the library."
    },
    {
        "id": "CMP008",
        "issueId": "ISSUE_WINDOWS_01",
        "title": "Broken classroom windows",
        "text": "Several classroom windows are damaged."
    }
]


print("Loading duplicate detection model...")
model = SentenceTransformer(MODEL_NAME)

sample_texts = [
    f"{item['title']}. {item['text']}"
    for item in SAMPLE_COMPLAINTS
]

sample_embeddings = model.encode(
    sample_texts,
    convert_to_tensor=True,
    normalize_embeddings=True
)

print("Duplicate detection model loaded!")


def detect_duplicate(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Complaint text cannot be empty")

    query_embedding = model.encode(
        text.strip(),
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    similarities = util.cos_sim(
        query_embedding,
        sample_embeddings
    )[0]

    best_index = int(similarities.argmax().item())
    best_score = float(similarities[best_index].item())
    best_match = SAMPLE_COMPLAINTS[best_index]

    is_duplicate = best_score >= SIMILARITY_THRESHOLD

    return {
        "isDuplicate": is_duplicate,
        "similarityScore": round(best_score, 4),
        "duplicateThreshold": SIMILARITY_THRESHOLD,
        "matchedComplaintId": (
            best_match["id"] if is_duplicate else None
        ),
        "matchedComplaintTitle": (
            best_match["title"] if is_duplicate else None
        )
    }


if __name__ == "__main__":
    test_complaints = [
        "There is no water in my hostel bathroom.",
        "The library internet connection is not working.",
        "Please install more benches in the college garden."
    ]

    for complaint in test_complaints:
        print(f"\nComplaint: {complaint}")
        print(detect_duplicate(complaint))

def count_related_sample_reports(matched_complaint_id: str | None) -> int:
    """
    Count existing sample reports for the matched issue,
    then include the incoming complaint as one new report.

    If there is no duplicate match, the new issue starts at 1.
    """

    if not matched_complaint_id:
        return 1

    matched_complaint = next(
        (
            complaint
            for complaint in SAMPLE_COMPLAINTS
            if complaint["id"] == matched_complaint_id
        ),
        None,
    )

    if matched_complaint is None:
        return 1

    issue_id = matched_complaint["issueId"]

    existing_reports = sum(
        1
        for complaint in SAMPLE_COMPLAINTS
        if complaint["issueId"] == issue_id
    )

    # Include the new incoming complaint.
    return existing_reports + 1
