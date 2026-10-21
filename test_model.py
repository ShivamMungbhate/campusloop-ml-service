from transformers import pipeline

MODEL_NAME = "facebook/bart-large-mnli"

classifier = pipeline(
    task="zero-shot-classification",
    model=MODEL_NAME
)

categories = [
    "Electrical Maintenance",
    "Plumbing and Water Supply",
    "Housekeeping and Sanitation",
    "IT Support",
    "Hostel Administration",
    "Library Administration",
    "Laboratory Maintenance",
    "Campus Security",
    "Civil Maintenance",
    "Other"
]

complaint = """
There is no water supply in the hostel bathroom
and students are facing difficulties.
"""

result = classifier(
    complaint,
    candidate_labels=categories
)

print("\nComplaint:", complaint.strip())
print("\nPredicted categories:")

for label, score in zip(result["labels"], result["scores"]):
    print(f"{label}: {score:.4f}")

print("\nTop predicted category:", result["labels"][0])
print("Top model score:", round(float(result["scores"][0]), 4))
