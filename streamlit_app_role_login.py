
import uuid
import os
import hmac
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()

import requests
import streamlit as st
from pymongo.errors import PyMongoError

from database import complaints_collection, check_database


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

API_URL = "http://127.0.0.1:8000"

STATUS_OPTIONS = [
    "Pending",
    "In Progress",
    "Resolved",
    "Rejected",
]

st.set_page_config(
    page_title="CampusLoop",
    page_icon="🎓",
    layout="wide",
)


# --------------------------------------------------
# DATABASE FUNCTIONS
# --------------------------------------------------

def save_complaint(title, description, analysis, submitted_by=None):
    """Save a complaint and its ML analysis to MongoDB."""

    complaint = {
        "complaintId": "CL-" + uuid.uuid4().hex[:8].upper(),
        "title": title,
        "description": description,
        "submittedBy": submitted_by,
        "createdAt": datetime.now(timezone.utc),
        "status": "Pending",
        "analysis": analysis,
    }

    complaints_collection.insert_one(complaint)
    return complaint


def get_complaints():
    """Fetch complaints from MongoDB, newest first."""

    return list(
        complaints_collection.find(
            {},
            {"_id": 0},
        ).sort("createdAt", -1)
    )


def update_complaint_status(complaint_id, new_status):
    """Update the status of a complaint in MongoDB."""

    result = complaints_collection.update_one(
        {"complaintId": complaint_id},
        {"$set": {"status": new_status}},
    )

    return result.matched_count > 0


# --------------------------------------------------
# FASTAPI / ML FUNCTIONS
# --------------------------------------------------

def analyze_complaint(title, description):
    """Call the existing CampusLoop FastAPI ML service."""

    response = requests.post(
        f"{API_URL}/analyze",
        json={
            "title": title,
            "text": description,
        },
        timeout=120,
    )

    response.raise_for_status()