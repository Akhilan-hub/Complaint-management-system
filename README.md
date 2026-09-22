# 🏛️ Thaagam Foundations - Complaint Management System

A modern, full-stack **Django Complaint Management System** with **AI-powered verification** using Google Gemini API. Built for community organizations, NGOs, and municipal tracking.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Django](https://img.shields.io/badge/Django-6.1-green.svg)
![AI](https://img.shields.io/badge/AI-Google_Gemini_3.6-orange.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 🌟 Features

### 👤 User Dashboard
- **Single-Field Registration**: Simple registration with Full Name, Email, and Password.
- **Complaint Submission**: File new complaints with title, description, and proof image upload.
- **Real-Time Status Tracking**: Track submitted complaints across `NEW`, `PENDING`, and `RESOLVED` statuses.
- **AI Verification Feedback**: View AI verification badges (`PASS`, `FAIL`, `UNCERTAIN`) and AI reasoning for submitted evidence.

### 🛡️ Admin Dashboard
- **Summary Metrics**: Real-time stats for Total, New, Pending, and Resolved complaints.
- **Status Filter Pills**: Quick tabs for All, New, Pending, and Resolved views.
- **Bulk Delete Mode**: Toggle Delete Mode to select and batch-delete outdated complaints.
- **2-Step AI Resolution Workflow**:
  1. Take complaint into resolution queue (`PENDING`).
  2. Upload resolution proof image & description.
  3. AI automatically verifies if the fix matches the original complaint before resolving.
  4. Manual confirmation fallback with admin password verification if AI fails/flagged.

### 🤖 AI-Powered Multimodal Verification
- Uses **Google Gemini 3.6 Flash** to analyze uploaded complaint photos and resolution proof photos.
- Provides automated verification status (`PASS`, `FAIL`, `UNCERTAIN`) and detailed reasoning.

---

## 💻 Tech Stack

- **Backend**: Python 3.13, Django 6.1
- **Database**: SQLite3
- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), Vanilla JS
- **AI Engine**: Google Gemini API (`google-genai` SDK)

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher installed.

### 2. Clone the Repository
```bash
git clone https://github.com/Akhilan-hub/Complaint-management-system.git
cd Complaint-management-system
```

### 3. Setup Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
SECRET_KEY=your_django_secret_key_here
DEBUG=True
```

### 6. Run Database Migrations
```bash
python manage.py migrate
```

### 7. Seed Initial Demo Accounts
```bash
python manage.py create_initial_accounts
```
*(Creates Admin account `admin`/`admin123` and User account `user1`/`user123`)*

### 8. Start the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Tests

Run the automated Django test suite:
```bash
python manage.py test
```

---

## 📄 License
This project is open-source under the MIT License.
