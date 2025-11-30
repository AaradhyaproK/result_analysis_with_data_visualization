# 🎓 Student Result Analyzer Pro

**Student Result Analyzer Pro** is a comprehensive web application built with **Streamlit** and **Firebase**. It allows educational institutions to automate the extraction of student results from PDF marksheets (specifically optimized for SPPU format), analyze batch performance, store data securely in the cloud, and track student academic progression over time using PRN (Permanent Registration Number).

---

## 🚀 Features

### 🔐 Authentication & Roles
*   **Secure Login/Registration:** Firebase Authentication system.
*   **Role-Based Access:** 
    *   **Teachers:** Can upload PDFs, view batch analytics, and search global records.
    *   **Students:** Can view their own specific results and academic history.

### 📄 PDF Parsing & Automation
*   **Automated Extraction:** Uses `PyPDF2` and `Regex` to extract Seat No, PRN, Name, SGPA, and Subject Grades from complex PDF layouts.
*   **Intelligent Logic:** Automatically determines Pass/Fail status based on valid SGPA availability.
*   **Batch Processing:** Handles PDFs containing hundreds of student records in seconds.

### 📊 Analytics & Visualization
*   **Batch Analysis:** Histograms for SGPA distribution, Pie charts for Pass/Fail ratios.
*   **Grade Analysis:** Bar charts showing subject-wise grade distribution.
*   **Top Performers:** Automatically calculates and displays the top 10 students.
*   **Failure Analysis:** Categorizes failures (Invalid SGPA vs. Backlogs).

### 🌍 Global Search & History
*   **Student Profile:** Aggregates data from multiple uploaded files based on **PRN**.
*   **Academic Timeline:** Generates line graphs showing SGPA progression across different semesters/exams.
*   **Unified View:** View all marksheets for a specific student in one place.

### 💾 Cloud Storage
*   **Firestore Database:** Stores parsed data, exam tags, and user profiles securely.
*   **Persistence:** Data remains available across sessions and logins.

---

## 🛠️ Tech Stack

*   **Frontend/UI:** [Streamlit](https://streamlit.io/)
*   **Language:** Python 3.x
*   **Backend/Database:** Google Firebase (Firestore & Authentication)
*   **PDF Processing:** PyPDF2
*   **Visualization:** Plotly Express & Graph Objects
*   **Data Manipulation:** Pandas

---

## ⚙️ Logic & Data Models

### 1. Parsing Logic (`AdvancedResultAnalyzer`)
The application processes raw text extracted from PDFs using Python Regular Expressions (Regex):
*   **Block Splitting:** The text is split into blocks using `SEAT NO.:` as a delimiter.
*   **Field Extraction:**
    *   **SGPA:** Looks for patterns like `SECOND YEAR SGPA : 6.43` or `SGPA : --`.
    *   **Pass/Fail:** If `SGPA > 0`, the student is marked as **Pass**. If `SGPA` is `0.0`, `--`, or missing, they are marked as **Fail**.
*   **Subject Grids:** Iterates through lines starting with course codes (5+ digits) to extract Grades and Credits.

### 2. Database Schema (Firestore)

The application uses a NoSQL structure with two main collections:

#### **Collection: `users`**
Stores user profile data and roles.
```json
{
  "documentId": "uid_from_auth",
  "email": "teacher@example.com",
  "name": "John Doe",
  "role": "teacher",  // or "student"
  "created_at": "timestamp",
  "last_login": "timestamp"
}
Collection: result_files
Stores the parsed batch data from a specific PDF upload.
code
JSON
{
  "documentId": "unique_generated_id",
  "file_name": "SE_Computer_2024.pdf",
  "exam_tag": "SE 2024",
  "uploaded_by": "Teacher Name",
  "uploaded_at": "timestamp",
  "total_students": 150,
  "summary": {
    "average_sgpa": 7.5,
    "pass_percentage": 85.5
  },
  "students_data": [
    {
      "Name": "Student Name",
      "PRN": "72267...",
      "Seat No": "S123...",
      "SGPA": 8.5,
      "Result Status": "Pass",
      "Subjects": [
        {"Course Name": "Maths", "Grade": "A"}
      ]
    }
    // ... more students
  ]
}
3. Aggregation Logic
When searching globally:
The app fetches all documents from result_files.
It iterates through every student entry in every file.
It matches the input PRN or Name.
It groups matches into a dictionary keyed by PRN, sorting results by upload date to create the Academic Progression timeline.
📦 Installation & Setup
Prerequisites
Python 3.8 or higher installed.
A Google Firebase Project (configured in the code).
1. Clone the Repository
code
Bash
git clone <your-repository-url>
cd student-result-analyzer
2. Create a Virtual Environment (Recommended)
code
Bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
Create a file named requirements.txt with the following content:
code
Text
streamlit
pandas
PyPDF2
plotly
requests
Then run:
code
Bash
pip install -r requirements.txt
4. Firebase Configuration
The app.py file contains a dictionary named FIREBASE_CONFIG.
Current State: The code includes a configuration. Ensure this matches your active Firebase project settings.
Security Note: In a production environment, never hardcode API keys. Use Streamlit Secrets (.streamlit/secrets.toml) or Environment Variables.
5. Run the Application
code
Bash
streamlit run app.py
📖 Usage Guide
For Teachers
Register/Login: Select "Teacher" role.
Upload & Analyze:
Go to "Upload & Analyze".
Upload a Result PDF.
Important: Enter an "Exam Name" (e.g., "SE May 2024"). This tag is used for history tracking.
Review the analysis and click "Save to Database".
Global Search:
Go to "Global Search".
Enter a PRN (e.g., 72267170K).
View the student's unified profile, graphs, and marksheets from all semesters uploaded.
For Students
Register/Login: Select "Student" role.
Check Results:
Enter your PRN or Name.
View your personal academic history and progression chart.
🎨 Troubleshooting
"Role Mismatch" Error: Ensure you are logging in with the same role you selected during registration.
White Text on White Background: The app is optimized for Dark Mode. If using Light Mode, Streamlit settings might need adjustment, though CSS fixes have been applied for the Profile Card.
Database Save Failed: Ensure your Firebase Firestore rules allow reading/writing. For testing, rules can be set to allow read, write: if true;.
🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request.
📜 License
This project is open-source.
