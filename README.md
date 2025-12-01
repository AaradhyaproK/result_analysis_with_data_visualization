<div align="center">

# 🎓 <span style="color:#ff4b4b; font-weight:800;">Student Result Analyzer Pro</span>  
### 🚀 <span style="color:#0099ff;">The Next-Gen Academic Performance Tracker</span>

<br>

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

<br>

### <b>Analyze · Visualize · Archive</b>  
Transform static PDFs into intelligent academic dashboards.

---

</div>

---

## 🌟 **Overview**

**Student Result Analyzer Pro** is a smart PDF-processing platform that reads SPPU-style university result sheets and converts them into structured, searchable, and visual student profiles.

It builds an **Academic Timeline** for each PRN, showing semester-wise performance and analytics.

---

## ✨ **Key Features**

| Feature | Description |
|--------|-------------|
| 🔐 **Role-Based Access** | Teachers upload PDFs; students view their performance. |
| 📄 **Smart PDF Parser** | Extracts PRN, SGPA, subjects, grades with Regex. |
| 📈 **Analytics Engine** | Trendlines, histograms, pie charts (Plotly). |
| 🌍 **Global PRN Search** | View complete academic history across all uploads. |
| 🧠 **Logic Engine** | SGPA-based Pass/Fail validator (SPPU rule-aware). |
| ☁️ **Firestore Cloud DB** | Fast, secure, real-time database. |

---

## 🏗️ **Architecture & Parsing Logic**

### 🔍 1. **Parsing Engine (`AdvancedResultAnalyzer`)**

- Splits PDF text using:

```
SEAT NO.:
```

- Extracts:
  - Student Name  
  - Mother’s Name  
  - PRN  
  - Subject List  
  - SGPA & Credits  

### 🧠 Result Logic

```
IF SGPA > 0  → PASS  
ELSE         → FAIL
```

This overrides subject-level F grades to match actual university logic.

---

## 🗂️ **Firestore Schema**

### **📁 Collection: users**
```json
{
  "email": "teacher@college.edu",
  "role": "teacher",
  "name": "Prof. X",
  "last_login": "2024-10-27T10:00:00Z"
}
```

### **📁 Collection: results**
```json
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
```

---

## 🚀 **Installation & Setup**

### 1️⃣ Clone the Repo
```bash
git clone https://github.com/yourusername/student-result-analyzer.git
cd student-result-analyzer
```

### 2️⃣ Create Virtual Environment
**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install streamlit pandas PyPDF2 plotly requests
```

### 4️⃣ Configure Firebase  
Update in `app.py`:

```python
FIREBASE_CONFIG = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "your-project.firebaseapp.com",
    "projectId": "your-project",
    "storageBucket": "your-project.appspot.com",
    "messagingSenderId": "...",
    "appId": "..."
}
```

### 5️⃣ Run App
```bash
streamlit run app.py
```

---

## 📖 **Usage Guide**

### 👨‍🏫 **Teacher Dashboard**
- Upload PDF  
- Tag exam (e.g., TE 2024)  
- Parse & store in Firestore  
- Global PRN search  

### 🎓 **Student Dashboard**
- Login → Enter PRN  
- View SGPA timeline  
- Subjects + grades  
- Pass/Fail summary  

---

## 🛠️ **Troubleshooting**

| Issue | Fix |
|------|-----|
| ❗ Role Mismatch | Re-login with correct role. |
| ❗ Token Missing | Log out & log in again. |
| ❗ White Text | Light mode → Auto CSS applies. |
| ❗ PDF Upload Error | Ensure PDF is text-readable (not scanned). |

---

## 🤝 **Contributing**

```bash
git checkout -b feature/AmazingFeature
git commit -m "Add AmazingFeature"
git push origin feature/AmazingFeature
```
Then open a Pull Request.

---

## 📜 **License**

Released under the **MIT License**.

---

<div align="center">

### ❤️ Made with Passion using Streamlit & Python  

</div>
