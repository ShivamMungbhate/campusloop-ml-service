
import uuid
from datetime import datetime, timezone

import requests
import streamlit as st
from pymongo.errors import PyMongoError

from database import complaints_collection, check_database


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


def save_complaint(title, description, analysis):
    """Save a complaint and its ML analysis to MongoDB."""

    complaint = {
        "complaintId": "CL-" + uuid.uuid4().hex[:8].upper(),
        "title": title,
        "description": description,
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
    return response.json()


def show_analysis(result):
    """Display the ML analysis response."""

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Category",
        result.get("category", "N/A"),
    )

    c2.metric(
        "Priority",
        result.get("priority", "N/A"),
    )

    c3.metric(
        "Duplicate",
        "Yes" if result.get("isDuplicate") else "No",
    )

    c4, c5, c6 = st.columns(3)

    confidence = result.get("confidence")
    similarity = result.get("similarityScore")

    c4.metric(
        "Category score",
        f"{confidence:.4f}"
        if isinstance(confidence, (int, float))
        else "N/A",
    )

    c5.metric(
        "Similarity score",
        f"{similarity:.4f}"
        if isinstance(similarity, (int, float))
        else "N/A",
    )

    c6.metric(
        "Related reports (sample data)",
        result.get("relatedComplaintCount", "N/A"),
    )

    st.markdown("#### Priority assessment")

    st.write(
        "**Source:**",
        result.get("prioritySource", "N/A"),
    )

    st.write(
        "**Reason:**",
        result.get("priorityReason", "N/A"),
    )

    st.write(
        "**Needs review:**",
        result.get("priorityNeedsReview", "N/A"),
    )

    st.markdown("#### Duplicate detection")

    st.write(
        "**Matched complaint:**",
        result.get("matchedComplaintTitle") or "No match returned",
    )

    st.write(
        "**Matched ID:**",
        result.get("matchedComplaintId") or "None",
    )

    st.write(
        "**Similarity threshold:**",
        result.get("duplicateThreshold", "N/A"),
    )

    st.markdown("#### Escalation assessment")

    st.write(
        "**Escalation level:**",
        result.get("escalationLevel", "N/A"),
    )

    st.write(
        "**Reason:**",
        result.get("escalationReason", "N/A"),
    )

    st.write(
        "**Needs review:**",
        result.get("escalationNeedsReview", "N/A"),
    )

    with st.expander("View complete ML response"):
        st.json(result)


with st.sidebar:
    st.title("🎓 CampusLoop")
    st.caption("Your Campus. Your Voice.")

    page = st.radio(
        "Navigation",
        [
            "Student Dashboard",
            "Admin Dashboard",
            "AI Model Tester",
        ],
    )

    st.divider()

    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=2,
        )

        if response.ok:
            st.success("ML Service Connected")
        else:
            st.warning("ML Service returned an error")

    except requests.RequestException:
        st.error("ML Service Offline")


    try:
        check_database()
        st.success("MongoDB Connected")

    except Exception:
        st.error("MongoDB Disconnected")

    st.caption("CampusLoop prototype")




if page == "Student Dashboard":

    st.title("👨‍🎓 Student Dashboard")

    st.write(
        "Submit campus complaints and view their AI assessments."
    )

   

   
    try:
        complaints = get_complaints()

    except PyMongoError:
        st.error(
            "Could not load complaints from MongoDB. "
            "Check your database connection."
        )
        complaints = []

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total complaints",
        len(complaints),
    )

    c2.metric(
        "Pending complaints",
        sum(
            complaint.get("status") == "Pending"
            for complaint in complaints
        ),
    )

    c3.metric(
        "Resolved complaints",
        sum(
            complaint.get("status") == "Resolved"
            for complaint in complaints
        ),
    )

    st.divider()


    st.subheader("📝 Submit a complaint")

    with st.form("student_complaint_form"):

        title = st.text_input(
            "Complaint title",
            placeholder="e.g. Hostel water supply unavailable",
            max_chars=200,
        )

        description = st.text_area(
            "Complaint description",
            placeholder=(
                "Describe the issue, its location, "
                "and how students are affected..."
            ),
            height=150,
            max_chars=10000,
        )

        submitted = st.form_submit_button(
            "Submit and Analyze",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        if not title.strip() or not description.strip():

            st.warning(
                "Please enter both a title and description."
            )

        else:

            try:
                with st.spinner(
                    "Analyzing complaint with CampusLoop AI..."
                ):
                    analysis = analyze_complaint(
                        title.strip(),
                        description.strip(),
                    )

                with st.spinner("Saving complaint to MongoDB..."):
                    complaint = save_complaint(
                        title=title.strip(),
                        description=description.strip(),
                        analysis=analysis,
                    )

                st.success(
                    "Complaint saved successfully! "
                    f"Reference ID: {complaint['complaintId']}"
                )

                st.subheader("🤖 AI analysis results")
                show_analysis(analysis)

            except requests.RequestException:
                st.error(
                    "The ML service could not analyze the complaint. "
                    "Check that FastAPI is running on port 8000."
                )

            except PyMongoError:
                st.error(
                    "The ML analysis completed, but saving to MongoDB "
                    "failed. Check your database connection."
                )

    st.divider()

    st.subheader("📋 Submitted complaints")

    try:
        complaints = get_complaints()

        if not complaints:
            st.info(
                "No complaints found. Submit your first complaint above."
            )

        else:
            for complaint in complaints:

                complaint_id = complaint.get(
                    "complaintId",
                    "Unknown ID",
                )

                analysis = complaint.get("analysis", {})

                created_at = complaint.get("createdAt")

                if isinstance(created_at, datetime):
                    created_text = created_at.strftime(
                        "%d %b %Y, %I:%M %p"
                    )
                else:
                    created_text = "Unknown date"

                with st.expander(
                    f"{complaint_id} · {complaint.get('title', 'Untitled')}"
                ):

                    st.write("**Submitted:**", created_text)
                    st.write(
                        "**Status:**",
                        complaint.get("status", "Pending"),
                    )
                    st.write(
                        "**Category:**",
                        analysis.get("category", "N/A"),
                    )
                    st.write(
                        "**Priority:**",
                        analysis.get("priority", "N/A"),
                    )
                    st.write(
                        "**Description:**",
                        complaint.get("description", ""),
                    )

    except PyMongoError:
        st.error("Could not retrieve complaint history from MongoDB.")



elif page == "Admin Dashboard":

    st.title("🛡️ Admin Dashboard")

    st.write(
        "Review campus complaints, inspect AI assessments "
        "and update complaint statuses."
    )

    

    try:
        complaints = get_complaints()

    except PyMongoError:
        st.error("Could not load complaints from MongoDB.")
        complaints = []

    
    total_count = len(complaints)

    pending_count = sum(
        complaint.get("status") == "Pending"
        for complaint in complaints
    )

    urgent_count = sum(
        complaint.get("analysis", {}).get("priority") == "Urgent"
        for complaint in complaints
    )

    duplicate_count = sum(
        bool(
            complaint.get("analysis", {}).get("isDuplicate")
        )
        for complaint in complaints
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total complaints", total_count)
    c2.metric("Pending", pending_count)
    c3.metric("Urgent", urgent_count)
    c4.metric("Duplicate matches", duplicate_count)

    st.divider()

    st.subheader("📂 Complaint management")

    if not complaints:

        st.info(
            "No complaints found. Submit a complaint from "
            "the Student Dashboard first."
        )

    else:

        categories = sorted({
            complaint.get("analysis", {}).get(
                "category", "Other"
            )
            for complaint in complaints
        })

        f1, f2, f3 = st.columns(3)

        category_filter = f1.selectbox(
            "Filter by category",
            ["All"] + categories,
        )

        priority_filter = f2.selectbox(
            "Filter by priority",
            [
                "All",
                "Urgent",
                "High",
                "Medium",
                "Low",
                "Unknown",
            ],
        )

        status_filter = f3.selectbox(
            "Filter by status",
            ["All"] + STATUS_OPTIONS,
        )

        
        filtered = []

        for complaint in complaints:

            analysis = complaint.get("analysis", {})

            category = analysis.get("category", "Other")
            priority = analysis.get("priority", "Unknown")
            status = complaint.get("status", "Pending")

            if (
                category_filter != "All"
                and category != category_filter
            ):
                continue

            if (
                priority_filter != "All"
                and priority != priority_filter
            ):
                continue

            if (
                status_filter != "All"
                and status != status_filter
            ):
                continue

            filtered.append(complaint)

        st.caption(
            f"Showing {len(filtered)} of {len(complaints)} complaints"
        )

        for complaint in filtered:

            complaint_id = complaint.get(
                "complaintId",
                "Unknown ID",
            )

            analysis = complaint.get("analysis", {})

            with st.expander(
                f"{complaint_id} · "
                f"{complaint.get('title', 'Untitled')} · "
                f"{analysis.get('priority', 'Unknown')}"
            ):

                st.write(
                    "**Description:**",
                    complaint.get("description", ""),
                )

                created_at = complaint.get("createdAt")

                if isinstance(created_at, datetime):
                    st.write(
                        "**Submitted:**",
                        created_at.strftime("%d %b %Y, %I:%M %p"),
                    )

                st.write(
                    "**Category:**",
                    analysis.get("category", "N/A"),
                )

                st.write(
                    "**Priority:**",
                    analysis.get("priority", "N/A"),
                )

                st.write(
                    "**Priority reason:**",
                    analysis.get("priorityReason", "N/A"),
                )

                st.write(
                    "**Duplicate match:**",
                    analysis.get("matchedComplaintTitle") or "None",
                )

                st.write(
                    "**Escalation level:**",
                    analysis.get("escalationLevel", "N/A"),
                )

                st.write(
                    "**Escalation reason:**",
                    analysis.get("escalationReason", "N/A"),
                )

                st.write(
                    "**Human review recommended:**",
                    analysis.get("escalationNeedsReview", "N/A"),
                )

                current_status = complaint.get(
                    "status",
                    "Pending",
                )

                
                if current_status not in STATUS_OPTIONS:
                    current_status = "Pending"

                selected_status = st.selectbox(
                    "Complaint status",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(current_status),
                    key=f"status_{complaint_id}",
                )

                if st.button(
                    "Save status",
                    key=f"save_{complaint_id}",
                    type="primary",
                ):

                    try:
                        update_complaint_status(
                            complaint_id,
                            selected_status,
                        )

                        st.success(
                            f"Status saved to MongoDB: {selected_status}"
                        )

                        st.rerun()

                    except PyMongoError:
                        st.error(
                            "Could not update status in MongoDB."
                        )

                with st.expander("View complete AI assessment"):
                    st.json(analysis)



else:

    st.title("🧪 AI Model Tester")

    st.write(
        "Test the actual FastAPI complaint analysis pipeline "
        "without saving a new complaint to MongoDB."
    )

    examples = {
        "Choose a test complaint": ("", ""),

        "Hostel water shortage": (
            "Hostel water problem",
            "Students are unable to get water in the hostel bathrooms.",
        ),

        "Electrical safety": (
            "Exposed electrical wires",
            "Exposed live electrical wires near the classroom entrance.",
        ),

        "Library Wi-Fi": (
            "Library Wi-Fi not working",
            "Students cannot connect to the internet in the library.",
        ),

        "Library chairs": (
            "More chairs needed",
            "The library needs more chairs for students.",
        ),

        "Cosmetic improvement": (
            "New decoration",
            "The common room could use some new decorations.",
        ),
    }

    selected = st.selectbox(
        "Quick test examples",
        list(examples.keys()),
    )

    default_title, default_text = examples[selected]

    with st.form("ai_test_form"):

        test_title = st.text_input(
            "Complaint title",
            value=default_title,
            max_chars=200,
        )

        test_description = st.text_area(
            "Complaint description",
            value=default_text,
            height=140,
            max_chars=10000,
        )

        test_submitted = st.form_submit_button(
            "Analyze Complaint",
            type="primary",
            use_container_width=True,
        )

    if test_submitted:

        if not test_title.strip() or not test_description.strip():

            st.warning(
                "Please enter both a title and description."
            )

        else:

            try:
                with st.spinner(
                    "Running the actual ML pipeline..."
                ):
                    result = analyze_complaint(
                        test_title.strip(),
                        test_description.strip(),
                    )

                st.success("Analysis completed successfully!")

                show_analysis(result)

                st.info(
                    "The category score is not a calibrated probability. "
                    "Priority and escalation are prototype assessments "
                    "and require human review. Related report counts "
                    "currently use sample data from the ML service."
                )

            except requests.RequestException:
                st.error(
                    "Could not connect to the ML service. "
                    "Check that FastAPI is running on port 8000."
                )




st.divider()

st.caption(
    "CampusLoop · Your Campus. Your Voice. Better Together."
)
