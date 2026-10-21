
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from classifier import categorize_complaint
from priority import assess_priority
from duplicate_detector import (
    detect_duplicate,
    count_related_sample_reports,
)
from escalation import assess_escalation


app = FastAPI(title="CampusLoop ML Service")


class ComplaintRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=10000)


@app.get("/")
def root():
    return {
        "service": "CampusLoop ML Service",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: ComplaintRequest):
    try:
        # Combine title and description for analysis.
        complaint_text = f"{request.title}. {request.text}".strip()

        # 1. Category classification
        category_result = categorize_complaint(complaint_text)

        # 2. Priority assessment
        priority_result = assess_priority(complaint_text)

        # 3. Duplicate detection
        duplicate_result = detect_duplicate(complaint_text)

        # 4. Related complaint count (currently sample-data based)
        related_count = count_related_sample_reports(
            duplicate_result.get("matchedComplaintId")
        )

        # 5. Escalation assessment
        escalation_result = assess_escalation(
            related_complaint_count=related_count,
            current_priority=priority_result["priority"],
        )

        # Debug logs for the terminal
        print("Complaint:", complaint_text)
        print("Category result:", category_result)
        print("Priority result:", priority_result)
        print("Duplicate result:", duplicate_result)
        print("Related complaint count:", related_count)
        print("Escalation result:", escalation_result)

        return {
            **category_result,
            **priority_result,
            **duplicate_result,
            "relatedComplaintCount": related_count,
            **escalation_result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    except Exception as error:
        
        print("Analysis error:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Complaint analysis failed. Check the server terminal.",
        )
