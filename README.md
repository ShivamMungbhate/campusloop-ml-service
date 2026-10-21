# 🎓 CampusLoop — AI-Powered Campus Complaint Management System

**Your Campus. Your Voice.**

CampusLoop is an AI-powered college complaint management system designed to help students report campus issues and help administrators manage, prioritize, and resolve complaints efficiently.

The system uses machine learning to classify complaints, determine their priority, detect similar complaints, and support escalation based on complaint volume.

## ✨ Features

- **Complaint Submission:** Students can submit a complaint title and detailed description.
- **AI Complaint Classification:** Automatically categorizes complaints into departments such as Electrical Maintenance, Plumbing, Housekeeping, IT Support, Hostel Administration, Library Administration, Laboratory Maintenance, Campus Security, and Civil Maintenance.
- **Priority Detection:** Assigns priority levels based on complaint details and urgency.
- **Duplicate Detection:** Identifies complaints that may describe the same issue using semantic similarity.
- **Escalation Support:** Helps identify recurring issues that may require administrative attention.
- **Admin Dashboard:** Provides an interface for administrators to review submitted complaints.
- **MongoDB Integration:** Stores complaint information in a database.
- **AI API:** Uses FastAPI to expose machine-learning functionality to other parts of the application.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Prototype UI | Streamlit |
| Frontend | React (if enabled in your project) |
| Backend | Node.js, Express.js |
| AI Microservice | Python, FastAPI |
| Database | MongoDB Atlas |
| NLP Classification | Hugging Face Transformers |
| Semantic Similarity | Sentence Transformers |
| Model API | Uvicorn |
| AI Deployment | Hugging Face Spaces |

## 🏗️ System Architecture

1. A student submits a complaint through the CampusLoop interface.
2. The backend receives the complaint.
3. The AI service analyzes the complaint text.
4. The service predicts a category and priority and checks for similar complaints.
5. The backend stores the complaint and its analysis in MongoDB.
6. Administrators can review complaints and take appropriate action.

**Note:** The AI-to-Express integration and cloud deployment must be configured and verified before the entire workflow can be considered operational.

## 📁 Project Structure

```text
CampusLoop/
├── ml-service/
│   ├── main.py
│   ├── classifier.py
│   ├── priority.py
│   ├── duplicate_detector.py
│   ├── escalation.py
│   ├── database.py
│   ├── requirements.txt
│   └── Dockerfile
├── backend/
│   ├── server.js
│   ├── routes/
│   └── models/
├── frontend/
│   └── React application files
└── README.md
```

*The backend and frontend paths above are illustrative; adjust them to match your actual repository structure.*

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or later
- Node.js and npm
- MongoDB Atlas account or a local MongoDB instance
- Git

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd CampusLoop
```

Replace `<YOUR_REPOSITORY_URL>` with your repository's actual URL.

### 2. Set Up the AI Service

Navigate to the AI service folder:

```bash
cd ml-service
```

Create and activate a virtual environment.

**Windows:**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI service:

```bash
uvicorn main:app --reload --port 8000
```

Open the API documentation:

http://127.0.0.1:8000/docs

### 3. Configure Environment Variables

Create a `.env` file in the appropriate backend directory and configure the variables required by your application.

Example:

```env
PORT=5000
MONGODB_URI=<YOUR_MONGODB_CONNECTION_STRING>
AI_SERVICE_URL=http://127.0.0.1:8000
```

Replace placeholder values with your actual configuration. Never commit `.env` files, database credentials, or API secrets to Git.

### 4. Start the Node.js Backend

Navigate to your backend directory:

```bash
npm install
npm start
```

If your project does not have a `start` script, use the startup command configured in its `package.json`, such as `node server.js`.

### 5. Start the Frontend

Navigate to your frontend directory:

```bash
npm install
npm run dev
```

Use the local URL displayed by your frontend development server.

## 🤖 AI Modules

### Complaint Classification

Uses a Hugging Face zero-shot classification model to predict a relevant campus department.

### Priority Detection

Applies complaint rules to determine the urgency of reported issues.

### Duplicate Detection

Uses Sentence Transformers to compare complaint descriptions semantically and identify potentially related complaints.

### Escalation Support

Uses complaint-count thresholds to flag issues that may need additional attention. The thresholds should be configured and validated for the actual deployment.

## 🌐 API Endpoints

The exact endpoints depend on the implementation in `main.py`.

| Endpoint | Purpose |
|---|---|
| `GET /docs` | Interactive FastAPI documentation |
| `POST /analyze` | Analyze a complaint using the AI service |
| `GET /health` | Health check, if implemented |

For local testing, use:

```text
http://127.0.0.1:8000/docs
```

## 🔐 Security

- Keep database credentials and API keys in environment variables.
- Validate and sanitize incoming complaint data.
- Configure authentication and authorization for administrative operations.
- Restrict CORS to trusted frontend origins in production.
- Protect publicly accessible AI endpoints against unauthorized usage.

## 🔮 Future Enhancements

- Complaint status tracking and notifications
- Email or in-app alerts for administrators
- Complaint analytics and trend visualization
- Multilingual complaint classification
- Role-based access control
- Production monitoring and audit logs

## 🎯 Project Goal

CampusLoop aims to make campus issue reporting more accessible, transparent, and efficient by combining complaint management with AI-assisted analysis.

**CampusLoop — Your Campus. Your Voice.**

## 👥 Contributors

Add your team members and their respective roles here.

## 📄 License

Add the license applicable to your project before distributing it publicly.
