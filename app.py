import streamlit as st
import pandas as pd
import PyPDF2
import re
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import io
import json
import datetime
from typing import Dict, List, Optional
import hashlib
import requests
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Student Result Analyzer Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FIXED CSS: Added explicit text colors for the profile card to handle Dark Mode
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin-bottom: 1rem;
        color: #333; /* Ensure text is dark in metric cards */
    }
    .role-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        margin-left: 1rem;
        font-size: 1rem;
    }
    .teacher-badge { background-color: #4CAF50; color: white; }
    .student-badge { background-color: #2196F3; color: white; }
    
    /* PROFILE CARD CSS FIXED FOR DARK MODE */
    .profile-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #2196F3;
    }
    /* Force text colors inside the card to be dark */
    .profile-card h2 {
        color: #1f77b4 !important;
        margin-top: 0;
        margin-bottom: 10px;
    }
    .profile-card p {
        color: #444444 !important;
        font-size: 1.1rem;
        margin: 0;
    }
    .profile-card strong {
        color: #2c3e50 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. FIREBASE CONFIGURATION & MANAGER
# -----------------------------------------------------------------------------
FIREBASE_CONFIG = {}

FIREBASE_REST_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['projectId']}/databases/(default)/documents"

class FirebaseManager:
    def __init__(self):
        self.id_token = st.session_state.get('id_token')
        self.user_id = st.session_state.get('user_id')
        self.initialize_firebase()
    
    def initialize_firebase(self):
        try:
            requests.get(f"{FIREBASE_REST_URL}/test_connection")
        except Exception:
            pass
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _set_session_token(self, token, uid):
        self.id_token = token
        self.user_id = uid
        st.session_state['id_token'] = token
        st.session_state['user_id'] = uid

    def sign_in_with_email_password(self, email: str, password: str):
        try:
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_CONFIG['apiKey']}"
            auth_data = {"email": email, "password": password, "returnSecureToken": True}
            response = requests.post(auth_url, json=auth_data)
            result = response.json()
            if response.status_code == 200:
                self._set_session_token(result.get('idToken'), result.get('localId'))
                return True, result
            else:
                return False, result.get('error', {}).get('message', 'Unknown error')
        except Exception as e:
            return False, str(e)
    
    def create_user_with_email_password(self, email: str, password: str, name: str):
        try:
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_CONFIG['apiKey']}"
            auth_data = {"email": email, "password": password, "displayName": name, "returnSecureToken": True}
            response = requests.post(auth_url, json=auth_data)
            result = response.json()
            if response.status_code == 200:
                self._set_session_token(result.get('idToken'), result.get('localId'))
                return True, result
            else:
                return False, result.get('error', {}).get('message', 'Unknown error')
        except Exception as e:
            return False, str(e)
    
    def firestore_request(self, method, path, data=None):
        if not self.id_token: return None
        url = f"{FIREBASE_REST_URL}/{path}"
        headers = {"Authorization": f"Bearer {self.id_token}", "Content-Type": "application/json"}
        try:
            if method == "GET": response = requests.get(url, headers=headers)
            elif method == "POST": response = requests.post(url, headers=headers, json=data)
            elif method == "PATCH": response = requests.patch(url, headers=headers, json=data)
            elif method == "DELETE": response = requests.delete(url, headers=headers)
            else: return None
            
            if response.status_code not in [200, 201, 409]:
                if response.status_code != 404:
                    st.error(f"DB Error {response.status_code}: {response.text}")
                return None
            return response.json()
        except Exception as e:
            st.error(f"Request Exception: {str(e)}")
            return None
    
    def _to_firestore_value(self, value):
        if value is None: return {"nullValue": None}
        elif isinstance(value, bool): return {"booleanValue": value}
        elif isinstance(value, int): return {"integerValue": str(value)}
        elif isinstance(value, float): return {"doubleValue": value}
        elif isinstance(value, str): return {"stringValue": value}
        elif isinstance(value, datetime.datetime): return {"timestampValue": value.isoformat() + "Z"}
        elif isinstance(value, list): return {"arrayValue": {"values": [self._to_firestore_value(v) for v in value]}}
        elif isinstance(value, dict): return {"mapValue": {"fields": {k: self._to_firestore_value(v) for k, v in value.items()}}}
        else: return {"stringValue": str(value)}

    def create_user(self, email: str, password: str, role: str, name: str):
        success, result = self.create_user_with_email_password(email, password, name)
        if not success:
            st.error(f"❌ Auth Creation Failed: {result}")
            return None
        
        user_id = result.get('localId')
        user_data = {
            "fields": {
                "email": self._to_firestore_value(email),
                "role": self._to_firestore_value(role.lower()),
                "name": self._to_firestore_value(name),
                "user_id": self._to_firestore_value(user_id),
                "created_at": self._to_firestore_value(datetime.datetime.utcnow()),
                "last_login": self._to_firestore_value(datetime.datetime.utcnow())
            }
        }
        
        response = self.firestore_request("POST", f"users?documentId={user_id}", user_data)
        if not response or 'error' in response:
             response = self.firestore_request("PATCH", f"users/{user_id}", user_data)

        if response:
            return user_id
        return None
    
    def verify_user(self, email: str, password: str):
        success, result = self.sign_in_with_email_password(email, password)
        if not success: return False, f"Login failed: {result}"
        
        user_doc = self.firestore_request("GET", f"users/{self.user_id}")
        if not user_doc: return False, "User profile not found."
        
        role = user_doc.get('fields', {}).get('role', {}).get('stringValue', '')
        if not role: return False, "User role missing."

        user_data = {
            'email': user_doc.get('fields', {}).get('email', {}).get('stringValue', ''),
            'role': role,
            'name': user_doc.get('fields', {}).get('name', {}).get('stringValue', ''),
            'uid': self.user_id
        }
        return True, user_data

    def save_result_data(self, file_name: str, exam_tag: str, students_data: List[Dict], uploaded_by: str, summary: Dict):
        if not self.id_token: return None
        
        batch_data = {
            "fields": {
                "file_name": self._to_firestore_value(file_name),
                "exam_tag": self._to_firestore_value(exam_tag),
                "uploaded_by": self._to_firestore_value(uploaded_by),
                "uploaded_at": self._to_firestore_value(datetime.datetime.utcnow()),
                "total_students": self._to_firestore_value(len(students_data)),
                "students_data": self._to_firestore_value(students_data),
                "summary": self._to_firestore_value(summary)
            }
        }
        
        doc_id = f"result_{int(time.time())}_{hashlib.md5(file_name.encode()).hexdigest()[:10]}"
        with st.spinner("Saving data to Cloud..."):
            result = self.firestore_request("POST", f"result_files?documentId={doc_id}", batch_data)
        
        if result:
            st.success("✅ Saved successfully!")
            return doc_id
        return None

    def get_all_result_files(self):
        if not self.id_token: return []
        result = self.firestore_request("GET", "result_files")
        if not result or 'documents' not in result: return []
        
        files = []
        for doc in result['documents']:
            file_data = self._convert_from_firestore(doc)
            file_data['id'] = doc['name'].split('/')[-1]
            files.append(file_data)
        return sorted(files, key=lambda x: x.get('uploaded_at', ''), reverse=True)

    def get_student_history(self, search_term: str):
        files = self.get_all_result_files()
        student_history = {}
        
        search_term = search_term.lower().strip()
        
        for file_data in files:
            exam_tag = file_data.get('exam_tag', file_data.get('file_name', 'Unknown Exam'))
            upload_date = file_data.get('uploaded_at')
            
            for student in file_data.get('students_data', []):
                s_name = student.get('Name', '').lower()
                s_prn = student.get('PRN', '').strip()
                
                if search_term in s_name or search_term == s_prn.lower():
                    if s_prn not in student_history:
                        student_history[s_prn] = {
                            'Name': student.get('Name'),
                            'PRN': s_prn,
                            'Mother': student.get('Mother Name'),
                            'Results': []
                        }
                    
                    result_entry = {
                        'Exam': exam_tag,
                        'Date': upload_date,
                        'SGPA': student.get('SGPA', 0),
                        'Result': student.get('Result Status'),
                        'Credits': student.get('Credits'),
                        'Seat': student.get('Seat No'),
                        'Subjects': student.get('Subjects', [])
                    }
                    student_history[s_prn]['Results'].append(result_entry)
        
        for prn in student_history:
            student_history[prn]['Results'].sort(key=lambda x: x['Date'] if isinstance(x['Date'], datetime.datetime) else datetime.datetime.min)
            
        return list(student_history.values())

    def _convert_from_firestore(self, doc):
        fields = doc.get('fields', {})
        result = {}
        for key, value in fields.items():
            if 'stringValue' in value: result[key] = value['stringValue']
            elif 'integerValue' in value: result[key] = int(value['integerValue'])
            elif 'doubleValue' in value: result[key] = float(value['doubleValue'])
            elif 'booleanValue' in value: result[key] = value['booleanValue']
            elif 'timestampValue' in value:
                try: result[key] = datetime.datetime.fromisoformat(value['timestampValue'].replace('Z', '+00:00'))
                except: result[key] = value['timestampValue']
            elif 'arrayValue' in value:
                vals = value['arrayValue'].get('values', [])
                result[key] = [self._convert_single_value(i) for i in vals]
            elif 'mapValue' in value:
                result[key] = self._convert_from_firestore({'fields': value['mapValue']['fields']})
        return result

    def _convert_single_value(self, value):
        if 'stringValue' in value: return value['stringValue']
        elif 'integerValue' in value: return int(value['integerValue'])
        elif 'doubleValue' in value: return float(value['doubleValue'])
        elif 'booleanValue' in value: return value['booleanValue']
        elif 'mapValue' in value: return self._convert_from_firestore({'fields': value['mapValue']['fields']})
        return None

# -----------------------------------------------------------------------------
# 3. ADVANCED RESULT ANALYZER
# -----------------------------------------------------------------------------
class AdvancedResultAnalyzer:
    def __init__(self):
        self.students_data = []
        self.raw_text = ""
    
    def extract_text_from_pdf(self, uploaded_file):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            self.raw_text = text
            return text
        except Exception as e:
            st.error(f"❌ Error reading PDF: {str(e)}")
            return None
    
    def is_valid_sgpa(self, sgpa_value):
        try: return float(sgpa_value) > 0
        except: return False
    
    def parse_comprehensive_data(self, text):
        students = []
        blocks = re.split(r'(?=SEAT NO\.:)', text)
        
        for block in blocks:
            if "SEAT NO.:" not in block: continue
            try:
                seat_match = re.search(r'SEAT NO\.:\s*([A-Z0-9]+)', block)
                seat_no = seat_match.group(1) if seat_match else "Unknown"
                name_match = re.search(r'NAME\s*:\s*(.*?)\s+MOTHER', block)
                name = name_match.group(1).strip() if name_match else "Unknown"
                mother_match = re.search(r'MOTHER\s*:\s*(.*?)\s+PRN', block)
                mother = mother_match.group(1).strip() if mother_match else "Unknown"
                prn_match = re.search(r'PRN\s*:\s*([A-Z0-9]+)', block)
                prn = prn_match.group(1).strip() if prn_match else "Unknown"
                sgpa_match = re.search(r'(?:FIRST|SECOND|THIRD|FOURTH)?\s*YEAR\s*SGPA\s*:\s*([0-9\.]+|--)', block)
                sgpa_raw = sgpa_match.group(1) if sgpa_match else "0.0"
                try: sgpa = float(sgpa_raw)
                except: sgpa = 0.0
                credits_match = re.search(r'TOTAL CREDITS EARNED\s*:\s*(\d+)', block)
                credits = int(credits_match.group(1)) if credits_match else 0
                
                subjects = self.parse_subject_grades(block)
                passed_subjects = sum(1 for sub in subjects if sub['Grade'] not in ['F', 'FF', 'AB', 'IC', 'ABS', 'Fail'])
                total_subjects = len(subjects)
                has_valid_sgpa = sgpa > 0
                result_status = 'Pass' if has_valid_sgpa else 'Fail'
                
                students.append({
                    'Seat No': seat_no, 'Name': name, 'Mother Name': mother, 'PRN': prn,
                    'SGPA': sgpa, 'SGPA_Raw': sgpa_raw, 'Credits': credits,
                    'Subjects': subjects, 'Passed Subjects': passed_subjects,
                    'Total Subjects': total_subjects, 'Result Status': result_status,
                    'Has Valid SGPA': has_valid_sgpa
                })
            except Exception: continue
        return students
    
    def parse_subject_grades(self, block_text):
        subjects = []
        lines = block_text.split('\n')
        for line in lines:
            line = line.strip()
            if re.match(r'^\d{5,}[A-Z]?', line):
                parts = line.split()
                if len(parts) > 6:
                    grade = parts[-5]
                    course_code = parts[0]
                    course_name = " ".join(parts[1:min(len(parts), 4)]) 
                    subjects.append({'Course Code': course_code, 'Course Name': course_name, 'Grade': grade})
        return subjects
    
    def get_result_summary(self):
        if not self.students_data: return {}
        total = len(self.students_data)
        passed = sum(1 for s in self.students_data if s['Result Status'] == 'Pass')
        valid_sgpa_students = [s for s in self.students_data if s.get('Has Valid SGPA')]
        avg_sgpa = sum(s['SGPA'] for s in valid_sgpa_students) / len(valid_sgpa_students) if valid_sgpa_students else 0
        return {
            'total_students': total, 'passed_students': passed,
            'failed_students': total - passed, 'average_sgpa': round(avg_sgpa, 2),
            'pass_percentage': round((passed / total * 100) if total > 0 else 0, 1)
        }

    def get_top_students(self, n=10):
        valid = [s for s in self.students_data if s.get('Has Valid SGPA')]
        return sorted(valid, key=lambda x: x['SGPA'], reverse=True)[:n]
    
    def get_failed_students(self):
        return [s for s in self.students_data if s['Result Status'] == 'Fail']

# -----------------------------------------------------------------------------
# 4. VISUALIZATIONS & PROFILE RENDERER
# -----------------------------------------------------------------------------
def render_student_profile(student_history):
    # FIXED: Added color classes to h2 and p to make them visible in dark mode
    st.markdown(f"""
    <div class="profile-card">
        <h2>👤 {student_history['Name']}</h2>
        <p><strong>PRN:</strong> {student_history['PRN']} | <strong>Mother:</strong> {student_history['Mother']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if len(student_history['Results']) > 0:
        results_df = pd.DataFrame(student_history['Results'])
        
        if not results_df.empty:
            st.subheader("📈 Academic Progression")
            fig = px.line(results_df, x='Exam', y='SGPA', markers=True, 
                          title="SGPA Progression", range_y=[0, 10])
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📚 Result History")
            summary_df = results_df[['Exam', 'Seat', 'SGPA', 'Result', 'Credits']].copy()
            st.dataframe(summary_df, use_container_width=True)
            
            st.subheader("📝 Detailed Marksheets")
            for result in student_history['Results']:
                with st.expander(f"{result['Exam']} - SGPA: {result['SGPA']} ({result['Result']})"):
                    col1, col2 = st.columns(2)
                    with col1: st.write(f"**Seat No:** {result['Seat']}")
                    with col2: st.write(f"**Credits:** {result['Credits']}")
                        
                    if result['Subjects']:
                        sub_df = pd.DataFrame(result['Subjects'])
                        st.dataframe(sub_df, use_container_width=True)
    else:
        st.info("No detailed result history available.")

def render_overview_dashboard(analyzer):
    st.markdown("### 📈 Performance Overview")
    summary = analyzer.get_result_summary()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Students", summary['total_students'])
    m2.metric("Passed", summary['passed_students'], f"{summary['pass_percentage']}%")
    m3.metric("Failed", summary['failed_students'], delta_color="inverse")
    m4.metric("Avg SGPA", summary['average_sgpa'])
    
    c1, c2 = st.columns(2)
    with c1:
        valid_students = [s for s in analyzer.students_data if s.get('Has Valid SGPA')]
        sgpas = [s['SGPA'] for s in valid_students]
        if sgpas:
            fig = px.histogram(x=sgpas, nbins=20, title="📊 SGPA Distribution", color_discrete_sequence=['#1f77b4'])
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        labels = ['Pass', 'Fail']
        values = [summary['passed_students'], summary['failed_students']]
        fig = px.pie(values=values, names=labels, title="🎯 Result Status", color=labels, color_discrete_map={'Pass':'#4CAF50', 'Fail':'#F44336'})
        st.plotly_chart(fig, use_container_width=True)

def render_top_performers(analyzer):
    st.markdown("### 🏆 Top Performers")
    top_students = analyzer.get_top_students(10)
    if top_students:
        df = pd.DataFrame(top_students)
        st.dataframe(df[['Seat No', 'Name', 'SGPA', 'Result Status', 'Passed Subjects']], use_container_width=True)

def render_failed_analysis(analyzer):
    st.markdown("### ❌ Failure Analysis")
    failed = analyzer.get_failed_students()
    if not failed:
        st.success("🎉 All students passed!")
        return
    df = pd.DataFrame(failed)
    st.dataframe(df[['Seat No', 'Name', 'SGPA_Raw', 'Passed Subjects']], use_container_width=True)

def render_detailed_data(analyzer):
    st.markdown("### 📋 Student List")
    df = pd.DataFrame([ {k:v for k,v in s.items() if k!='Subjects'} for s in analyzer.students_data ])
    
    c1, c2, c3 = st.columns(3)
    with c1: min_sgpa = st.slider("Min SGPA", 0.0, 10.0, 0.0)
    with c2: status = st.selectbox("Status", ["All", "Pass", "Fail"])
    with c3: sort_order = st.selectbox("Sort", ["High to Low", "Low to High"])
        
    filtered = df[df['SGPA'] >= min_sgpa]
    if status != "All": filtered = filtered[filtered['Result Status'] == status]
    if sort_order == "High to Low": filtered = filtered.sort_values(by='SGPA', ascending=False)
    else: filtered = filtered.sort_values(by='SGPA', ascending=True)
    
    st.write(f"Showing {len(filtered)} students")
    st.dataframe(filtered, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. AUTHENTICATION & MAIN FLOW
# -----------------------------------------------------------------------------
class AuthenticationManager:
    def __init__(self, firebase_manager):
        self.fm = firebase_manager

    def show_login_page(self):
        st.markdown('<h1 class="main-header">🎓 Student Result Portal</h1>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with t1:
            with st.form("login"):
                email = st.text_input("Email")
                pwd = st.text_input("Password", type="password")
                role = st.selectbox("Role", ["Teacher", "Student"])
                if st.form_submit_button("Login"):
                    success, result = self.fm.verify_user(email, pwd)
                    if success:
                        if result['role'] == role.lower():
                            st.session_state.user = result
                            st.session_state.logged_in = True
                            st.session_state.role = role.lower()
                            st.rerun()
                        else:
                            st.error(f"Role mismatch. Registered as '{result['role']}'.")
                    else:
                        st.error(result)
        
        with t2:
            with st.form("reg"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                pwd = st.text_input("Password", type="password")
                role = st.selectbox("Role", ["Teacher", "Student"])
                if st.form_submit_button("Register"):
                    if len(pwd) >= 6:
                        uid = self.fm.create_user(email, pwd, role.lower(), name)
                        if uid:
                            success, result = self.fm.verify_user(email, pwd)
                            if success:
                                st.session_state.user = result
                                st.session_state.logged_in = True
                                st.session_state.role = role.lower()
                                st.rerun()
                    else:
                        st.error("Password must be > 6 chars")

def show_teacher_dashboard(fm):
    st.markdown(f'<h1 class="main-header">👨‍🏫 Teacher Dashboard <span class="role-badge teacher-badge">TEACHER</span></h1>', unsafe_allow_html=True)
    menu = ["📤 Upload & Analyze", "📁 Saved Results", "👥 Global Search (History)"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "📤 Upload & Analyze":
        st.header("Upload New Result PDF")
        uploaded = st.file_uploader("Choose PDF", type="pdf")
        exam_tag = st.text_input("Exam Name (e.g., 'SE 2024', 'TE 2025')", placeholder="SE May 2024")
        
        if uploaded and exam_tag:
            analyzer = AdvancedResultAnalyzer()
            text = analyzer.extract_text_from_pdf(uploaded)
            if text:
                data = analyzer.parse_comprehensive_data(text)
                if data:
                    analyzer.students_data = data
                    st.success(f"Processed {len(data)} students")
                    t1, t2, t3, t4 = st.tabs(["Overview", "Top Performers", "Failures", "Detailed List"])
                    with t1: render_overview_dashboard(analyzer)
                    with t2: render_top_performers(analyzer)
                    with t3: render_failed_analysis(analyzer)
                    with t4: render_detailed_data(analyzer)
                    
                    if st.button("💾 Save to Database", type="primary"):
                        summary = analyzer.get_result_summary()
                        fm.save_result_data(uploaded.name, exam_tag, data, st.session_state.user['name'], summary)
                else:
                    st.error("No data found")
        elif uploaded and not exam_tag:
            st.warning("⚠️ Please enter an Exam Name (e.g., 'SE 2023') to enable saving.")

    elif choice == "📁 Saved Results":
        st.header("Previous Uploads")
        files = fm.get_all_result_files()
        if not files: st.info("No saved results found.")
        for f in files:
            time_str = f.get('uploaded_at', datetime.datetime.now())
            if isinstance(time_str, datetime.datetime): time_str = time_str.strftime('%Y-%m-%d %H:%M')
            
            with st.expander(f"📄 {f['file_name']} | 🏷️ {f.get('exam_tag', 'N/A')} | 📅 {time_str}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Total Students:** {f.get('total_students', 0)}")
                with col2:
                    if st.button(f"Load Analysis", key=f['id']):
                        st.session_state.current_analysis = f
                
                if st.session_state.get('current_analysis', {}).get('id') == f['id']:
                    analyzer = AdvancedResultAnalyzer()
                    analyzer.students_data = f['students_data']
                    st.markdown("---")
                    t1, t2, t3, t4 = st.tabs(["Overview", "Top Performers", "Failures", "Detailed List"])
                    with t1: render_overview_dashboard(analyzer)
                    with t2: render_top_performers(analyzer)
                    with t3: render_failed_analysis(analyzer)
                    with t4: render_detailed_data(analyzer)

    elif choice == "👥 Global Search (History)":
        st.header("🌍 Global Student Search & History")
        st.info("Enter PRN or Name to see aggregated history from all uploaded files.")
        search_term = st.text_input("Enter PRN (Recommended) or Name")
        
        if search_term:
            with st.spinner("Searching database..."):
                history_results = fm.get_student_history(search_term)
                
                if history_results:
                    st.success(f"Found {len(history_results)} student profile(s)!")
                    for student_history in history_results:
                        render_student_profile(student_history)
                else:
                    st.warning("No student found.")

def show_student_dashboard(fm):
    st.markdown(f'<h1 class="main-header">🎓 Student Portal <span class="role-badge student-badge">STUDENT</span></h1>', unsafe_allow_html=True)
    st.header("🔍 Check Your Results History")
    search_term = st.text_input("Enter your PRN (Preferred) or Name")
    
    if search_term:
        with st.spinner("Searching records..."):
            history_results = fm.get_student_history(search_term)
            
            if history_results:
                for student_history in history_results:
                    render_student_profile(student_history)
            else:
                st.error("No records found. Check PRN.")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
    
    fm = FirebaseManager()
    auth = AuthenticationManager(fm)
    
    if not st.session_state.logged_in:
        auth.show_login_page()
    else:
        with st.sidebar:
            st.write(f"👤 **{st.session_state.user['name']}**")
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.pop('id_token', None)
                st.session_state.pop('user_id', None)
                st.session_state.user = None
                st.rerun()
        
        if st.session_state.role == 'teacher':
            show_teacher_dashboard(fm)
        else:
            show_student_dashboard(fm)

if __name__ == "__main__":
    main()
