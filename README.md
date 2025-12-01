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

### 2. Database Schema (NoSQL)

We use two primary collections in Firestore:

<details>
<summary><b>📂 Collection: users</b> (Click to expand)</summary>

Stores authentication profiles and roles.
```json
{
  "documentId": "firebase_uid",
  "email": "professor@college.edu",
  "name": "Dr. Smith",
  "role": "teacher",
  "created_at": "2023-10-27T10:00:00Z"
}
</details>
<details>
<summary><b>📂 Collection: result_files</b> (Click to expand)</summary>
Stores the raw parsed data from every PDF upload.
code
JSON
{
  "file_name": "SE_Computer_May2024.pdf",
  "exam_tag": "SE 2024",
  "uploaded_by": "Dr. Smith",
  "students_data": [
    {
      "Name": "Adithyan K S",
      "PRN": "72266975F",
      "SGPA": 8.5,
      "Result Status": "Pass",
      "Subjects": [...]
    }
  ]
}
</details>
3. The Aggregation Algorithm
When you search for a student in the Global Search:
The app fetches ALL documents from result_files.
It iterates through thousands of student records in memory.
It filters by PRN (Unique Identifier).
It groups these records into a StudentHistory object, sorts them by date, and generates a Timeline Graph.
🚀 Installation & Setup
Follow these steps to get the system running locally.
Prerequisites
Python 3.8+
A Firebase Project (Firestore & Auth enabled)
Step 1: Clone the Repo
code
Bash
git clone https://github.com/yourusername/student-result-analyzer.git
cd student-result-analyzer
Step 2: Virtual Environment
code
Bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
Step 3: Install Dependencies
code
Bash
pip install streamlit pandas PyPDF2 plotly requests
Step 4: Configure Firebase
Open app.py and find the FIREBASE_CONFIG dictionary. Replace the values with your project's credentials:
code
Python
FIREBASE_CONFIG = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "your-project.firebaseapp.com",
    "projectId": "your-project",
    "storageBucket": "your-project.appspot.com",
    "messagingSenderId": "...",
    "appId": "..."
}
Step 5: Run the App
code
Bash
streamlit run app.py
📖 Usage Guide
👨‍🏫 For Teachers
Register: Create an account selecting the Teacher role.
Upload: Navigate to "Upload & Analyze".
Tag: Upload a PDF and give it an Exam Name (e.g., "TE 2023").
Save: Click "Save to Database" to archive the results.
Search: Use "Global Search" to see the full history of any student.
🎓 For Students
Register: Create an account selecting the Student role.
Search: Enter your PRN.
View: See your Academic Progression graph and detailed subject breakdowns for every exam recorded in the system.
🛠️ Troubleshooting
Issue	Solution
"Role Mismatch"	Ensure you are logging in with the same role (Student/Teacher) you selected during registration.
"Authentication Token Missing"	This happens if the session resets. Log out and Log in again to refresh the token.
White Text / Invisible Text	The app is optimized for Dark Mode. If using Light Mode, the custom CSS in the code handles the Profile Card visibility.
Upload Fails	Ensure the PDF is text-readable (not a scanned image) and follows the standard SPPU format.
🤝 Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.
Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request
<div align="center">
Made with ❤️ using Streamlit
</div>
