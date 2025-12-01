<div align="center">

# 🎓 Student Result Analyzer Pro
### 🚀 The Next-Gen Academic Performance Tracker

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

<p align="center">
  <b>Analyze. Visualize. Archive.</b><br>
  Transform static PDF result sheets into dynamic, searchable, and visualized student profiles.
</p>

</div>

---

## 🌟 Overview

**Student Result Analyzer Pro** is an advanced web application designed to solve the chaos of managing university result PDFs. It parses complex PDF marksheets (optimized for SPPU), extracts granular student data, stores it in the cloud, and generates insightful analytics.

Unlike simple parsers, this tool builds a **Student Timeline**, aggregating results from multiple exams using the student's **PRN (Permanent Registration Number)** to show academic progression over time.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🔐 Role-Based Access** | Secure authentication for **Teachers** (Upload/Analyze) and **Students** (View History). |
| **📄 Smart Parsing Engine** | Uses Regex to extract Seat No, PRN, SGPA, and Subject Grades from unstructured PDF text. |
| **📈 Dynamic Analytics** | Interactive histograms, pie charts, and trend lines using **Plotly**. |
| **🌍 Global Search** | Search a PRN once and see results aggregated from **every PDF** ever uploaded. |
| **🧠 Intelligent Logic** | Auto-corrects Result Status based on valid SGPA (Handles University logic nuances). |
| **☁️ Cloud Persistence** | Powered by **Google Firestore**, ensuring data is safe and available anytime. |

---

## 🏗️ Architecture & Logic

### 1. The Parsing Engine (`AdvancedResultAnalyzer`)
The core logic resides in how we treat the PDF text.
*   **Block Segmentation:** The PDF is treated as a continuous stream of text. We use `Regex` to split this stream into "Student Blocks" using the `SEAT NO.:` pattern as a delimiter.
*   **Data Extraction:** Within each block, we extract:
    *   **Identity:** Name, Mother's Name, PRN.
    *   **Scores:** SGPA, Total Credits.
    *   **Subject Grid:** A sub-parser iterates through lines starting with Course Codes (e.g., `210241`) to grab grades.
*   **Validation Logic:**
    > **Pass/Fail Rule:** If `SGPA > 0`, the student is marked **Pass**. If SGPA is `0.0`, `--`, or missing, the status is **Fail**. This overrides individual 'F' grades in non-mandatory subjects.

2. Firestore Database Schema
Collection: users

Stores profile + role (teacher/student):

{
  "email": "teacher@college.edu",
  "role": "teacher",
  "name": "Prof. X",
  "last_login": "2024-10-27T10:00:00Z"
}

Collection: results

Stores uploaded result sets:

{
  "file_name": "SE_Computer_May2024.pdf",
  "exam_tag": "SE 2024",
  "students_data": [
    {
      "Name": "Adithyan K S",
      "PRN": "72266975F",
      "SGPA": 8.5,
      "Subjects": [
        {
          "Code": "210251",
          "Name": "Data Structures",
          "Grade": "A+",
          "Credits": 4
        }
      ]
    }
  ]
}

🚀 Installation & Setup
Prerequisites

Python 3.8+

Firebase Project (Authentication + Firestore enabled)

1. Clone the Repository
git clone https://github.com/yourusername/student-result-analyzer.git
cd student-result-analyzer

2. Create Virtual Environment
Windows:
python -m venv venv
venv\Scripts\activate

Mac/Linux:
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install streamlit pandas PyPDF2 plotly requests

4. Configure Firebase

Edit app.py and update:

FIREBASE_CONFIG = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "your-project.firebaseapp.com",
    "projectId": "your-project",
    "storageBucket": "your-project.appspot.com",
    "messagingSenderId": "...",
    "appId": "..."
}

5. Run the Application
streamlit run app.py

📖 Usage Guide
👨‍🏫 For Teachers

Sign up selecting Teacher role.

Open Upload & Analyze.

Upload the result PDF.

Enter an Exam Tag (e.g., "TE 2024").

Save the parsed results to Firestore.

Use Global Search to view any student’s aggregated academic report.

🎓 For Students

Sign up selecting Student role.

Enter your PRN.

Instantly view:

Your SGPA timeline

Subject-wise grades

Pass/Fail overview

🛠️ Troubleshooting
Issue	Solution
"Role Mismatch"	Ensure you're logging in with the same role selected during sign-up.
"Token Missing"	Session expired → Log out and log in again.
White Text (Invisible)	App is optimized for dark mode; CSS auto-adjusts on light mode.
Upload Fails	Ensure the PDF is text-readable (not scanned) and follows SPPU format.
🤝 Contributing

Fork the repo

Create a branch

git checkout -b feature/AmazingFeature


Commit your changes

git commit -m "Add some AmazingFeature"


Push your branch

git push origin feature/AmazingFeature


Open a Pull Request

📜 License

This project is licensed under the MIT License.

❤️ Made with Love using Streamlit
