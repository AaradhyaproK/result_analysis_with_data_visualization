import streamlit as st
import pandas as pd
import PyPDF2
import re
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import io

# Page configuration
st.set_page_config(
    page_title="Advanced Student Result Analyzer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .top-student {
        background-color: #e8f5e8;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    .failed-student {
        background-color: #ffe8e8;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

class AdvancedResultAnalyzer:
    def __init__(self):
        self.students_data = []
        self.raw_text = ""
    
    def extract_text_from_pdf(self, uploaded_file):
        """Extract text from uploaded PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            self.raw_text = text
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return None
    
    def is_valid_sgpa(self, sgpa_value):
        """Check if SGPA is valid and present"""
        if isinstance(sgpa_value, str):
            return sgpa_value not in ['N/A', '--', '', 'FF', 'AB', 'IC', 'ABS']
        elif isinstance(sgpa_value, (int, float)):
            return sgpa_value > 0
        return False
    
    def parse_comprehensive_data(self, text):
        """Parse comprehensive student data including subject grades"""
        students = []
        
        # Split by student sections using seat numbers
        seat_pattern = r'SEAT NO\.: (T\d+)'
        student_sections = re.split(seat_pattern, text)
        
        for i in range(1, len(student_sections), 2):
            try:
                if i + 1 < len(student_sections):
                    seat_no = student_sections[i]
                    section_text = student_sections[i + 1]
                    
                    # Extract basic info
                    name_match = re.search(r'NAME : ([A-Z\s]+) MOTHER', section_text)
                    name = name_match.group(1).strip() if name_match else "Unknown"
                    
                    mother_match = re.search(r'MOTHER : ([A-Z\s]+) PRN', section_text)
                    mother = mother_match.group(1).strip() if mother_match else "Unknown"
                    
                    prn_match = re.search(r'PRN :([A-Z0-9]+)', section_text)
                    prn = prn_match.group(1).strip() if prn_match else "Unknown"
                    
                    # Extract SGPA - handle various formats
                    sgpa_match = re.search(r'THIRD YEAR SGPA : ([\d.-]+|N/A|--)', section_text)
                    sgpa_raw = sgpa_match.group(1) if sgpa_match else "0.0"
                    
                    # Convert SGPA to float, handle invalid cases
                    try:
                        sgpa = float(sgpa_raw) if self.is_valid_sgpa(sgpa_raw) else 0.0
                    except (ValueError, TypeError):
                        sgpa = 0.0
                    
                    # Extract credits
                    credits_match = re.search(r'TOTAL CREDITS EARNED : (\d+)', section_text)
                    credits = credits_match.group(1) if credits_match else "0"
                    
                    # Parse subject grades
                    subjects = self.parse_subject_grades(section_text)
                    
                    # Calculate passed/failed subjects
                    passed_subjects = sum(1 for sub in subjects if sub['Grade'] not in ['F', 'FF', 'AB', 'IC', 'ABS'])
                    total_subjects = len(subjects)
                    
                    # Determine result status - FAIL if SGPA is not valid/present
                    has_valid_sgpa = self.is_valid_sgpa(sgpa_raw) and sgpa > 0
                    all_subjects_passed = passed_subjects == total_subjects if total_subjects > 0 else False
                    
                    result_status = 'Pass' if (has_valid_sgpa and all_subjects_passed) else 'Fail'
                    
                    students.append({
                        'Seat No': seat_no,
                        'Name': name,
                        "Mother's Name": mother,
                        'PRN': prn,
                        'SGPA': sgpa,
                        'SGPA_Raw': sgpa_raw,  # Keep original value for display
                        'Credits': int(credits),
                        'Subjects': subjects,
                        'Passed Subjects': passed_subjects,
                        'Total Subjects': total_subjects,
                        'Result Status': result_status,
                        'Has Valid SGPA': has_valid_sgpa
                    })
            except Exception as e:
                st.warning(f"Error parsing student {i//2 + 1}: {str(e)}")
                continue
        
        return students
    
    def parse_subject_grades(self, section_text):
        """Parse subject-wise grades for a student"""
        subjects = []
        
        # Pattern to match subject entries
        subject_pattern = r'(\d{6}[A-Z]?)\s+([A-Z\s&\.]+)\s+(?:\d+/\d+\s+){2}(\d+/\d+)\s+(?:.*?){0,5}?(\b[A-Z\+]+\b)'
        matches = re.findall(subject_pattern, section_text)
        
        for match in matches:
            course_code, course_name, total_marks, grade = match
            subjects.append({
                'Course Code': course_code.strip(),
                'Course Name': course_name.strip(),
                'Total Marks': total_marks.strip(),
                'Grade': grade.strip()
            })
        
        return subjects
    
    def get_top_students(self, n=10):
        """Get top n students by SGPA (only those with valid SGPA)"""
        valid_students = [s for s in self.students_data if s['Has Valid SGPA']]
        return sorted(valid_students, key=lambda x: x['SGPA'], reverse=True)[:n]
    
    def get_failed_students(self):
        """Get all failed students"""
        return [s for s in self.students_data if s['Result Status'] == 'Fail']
    
    def get_result_summary(self):
        """Get overall result summary"""
        total_students = len(self.students_data)
        passed_students = sum(1 for s in self.students_data if s['Result Status'] == 'Pass')
        failed_students = total_students - passed_students
        
        # Students with valid SGPA
        students_with_sgpa = [s for s in self.students_data if s['Has Valid SGPA']]
        students_without_sgpa = total_students - len(students_with_sgpa)
        
        # Average SGPA only for students with valid SGPA
        sgpas = [s['SGPA'] for s in students_with_sgpa]
        avg_sgpa = sum(sgpas) / len(sgpas) if sgpas else 0
        
        return {
            'total_students': total_students,
            'passed_students': passed_students,
            'failed_students': failed_students,
            'students_with_sgpa': len(students_with_sgpa),
            'students_without_sgpa': students_without_sgpa,
            'pass_percentage': (passed_students / total_students * 100) if total_students > 0 else 0,
            'average_sgpa': avg_sgpa
        }

def main():
    st.markdown('<h1 class="main-header">🎓 Advanced Student Result Analyzer</h1>', unsafe_allow_html=True)
    
    # Initialize analyzer
    analyzer = AdvancedResultAnalyzer()
    
    # File upload
    uploaded_file = st.file_uploader("📁 Upload Student Result PDF", type="pdf")
    
    if uploaded_file is not None:
        with st.spinner("🔍 Analyzing PDF content..."):
            text = analyzer.extract_text_from_pdf(uploaded_file)
            
            if text:
                analyzer.students_data = analyzer.parse_comprehensive_data(text)
                
                if analyzer.students_data:
                    st.success(f"✅ Successfully processed {len(analyzer.students_data)} students!")
                    
                    # Create sidebar for navigation
                    st.sidebar.title("📊 Navigation")
                    analysis_option = st.sidebar.selectbox(
                        "Choose Analysis Type",
                        ["📈 Overview Dashboard", "🎓 Student Search", "🏆 Top Performers", 
                         "📊 Detailed Analysis", "❌ Failed Students", "📋 Raw Data"]
                    )
                    
                    if analysis_option == "📈 Overview Dashboard":
                        show_overview_dashboard(analyzer)
                    elif analysis_option == "🎓 Student Search":
                        show_student_search(analyzer)
                    elif analysis_option == "🏆 Top Performers":
                        show_top_performers(analyzer)
                    elif analysis_option == "📊 Detailed Analysis":
                        show_detailed_analysis(analyzer)
                    elif analysis_option == "❌ Failed Students":
                        show_failed_students(analyzer)
                    elif analysis_option == "📋 Raw Data":
                        show_raw_data(analyzer)
                    
                else:
                    st.error("❌ No student data found in the PDF")
            else:
                st.error("❌ Failed to extract text from PDF")

def show_overview_dashboard(analyzer):
    """Display overview dashboard with key metrics and visualizations"""
    st.header("📈 Overview Dashboard")
    
    # Key metrics
    summary = analyzer.get_result_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Students", summary['total_students'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Passed Students", summary['passed_students'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Pass Percentage", f"{summary['pass_percentage']:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Average SGPA", f"{summary['average_sgpa']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Students with SGPA", summary['students_with_sgpa'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Students without SGPA", summary['students_without_sgpa'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # SGPA Distribution (only for students with valid SGPA)
        students_with_sgpa = [s for s in analyzer.students_data if s['Has Valid SGPA']]
        sgpas = [s['SGPA'] for s in students_with_sgpa]
        if sgpas:
            fig_sgpa = px.histogram(
                x=sgpas, 
                nbins=20,
                title="📊 SGPA Distribution (Valid SGPA Only)",
                labels={'x': 'SGPA', 'y': 'Number of Students'},
                color_discrete_sequence=['#2E86AB']
            )
            fig_sgpa.update_layout(showlegend=False)
            st.plotly_chart(fig_sgpa, use_container_width=True)
        else:
            st.info("No valid SGPA data available for visualization")
    
    with col2:
        # Result Status Pie Chart
        status_counts = {
            'Pass': summary['passed_students'],
            'Fail': summary['failed_students']
        }
        colors = ['#4CAF50', '#F44336']  # Green for Pass, Red for Fail
        
        fig_pie = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="🎯 Result Status Distribution",
            color=list(status_counts.keys()),
            color_discrete_map={'Pass': '#4CAF50', 'Fail': '#F44336'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # SGPA Range Analysis (only for students with valid SGPA)
    st.subheader("📋 SGPA Range Analysis (Valid SGPA Only)")
    ranges = {
        '9.0+ (Excellent)': 0,
        '8.0-8.9 (Very Good)': 0,
        '7.0-7.9 (Good)': 0,
        '6.0-6.9 (Average)': 0,
        'Below 6.0': 0
    }
    
    for student in analyzer.students_data:
        if student['Has Valid SGPA']:
            sgpa = student['SGPA']
            if sgpa >= 9.0:
                ranges['9.0+ (Excellent)'] += 1
            elif sgpa >= 8.0:
                ranges['8.0-8.9 (Very Good)'] += 1
            elif sgpa >= 7.0:
                ranges['7.0-7.9 (Good)'] += 1
            elif sgpa >= 6.0:
                ranges['6.0-6.9 (Average)'] += 1
            else:
                ranges['Below 6.0'] += 1
    
    # Display range analysis
    range_cols = st.columns(5)
    range_colors = ['#2E8B57', '#3CB371', '#90EE90', '#FFD700', '#FF6347']  # Different greens to red
    
    for i, (range_name, count) in enumerate(ranges.items()):
        with range_cols[i]:
            total_valid = sum(ranges.values())
            percentage = (count / total_valid * 100) if total_valid > 0 else 0
            st.metric(range_name, f"{count} ({percentage:.1f}%)")

def show_student_search(analyzer):
    """Display student search functionality"""
    st.header("🎓 Student Search")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_type = st.selectbox("Search by", ["Seat Number", "Name", "PRN"])
    
    with col2:
        if search_type == "Seat Number":
            search_term = st.selectbox("Select Seat Number", 
                                     [s['Seat No'] for s in analyzer.students_data])
        elif search_type == "Name":
            search_term = st.selectbox("Select Name", 
                                     [s['Name'] for s in analyzer.students_data])
        else:  # PRN
            search_term = st.selectbox("Select PRN", 
                                     [s['PRN'] for s in analyzer.students_data])
    
    # Find student
    if search_type == "Seat Number":
        student = next((s for s in analyzer.students_data if s['Seat No'] == search_term), None)
    elif search_type == "Name":
        student = next((s for s in analyzer.students_data if s['Name'] == search_term), None)
    else:
        student = next((s for s in analyzer.students_data if s['PRN'] == search_term), None)
    
    if student:
        st.subheader(f"Student Details: {student['Name']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Seat No:** {student['Seat No']}")
            st.info(f"**PRN:** {student['PRN']}")
        
        with col2:
            sgpa_display = f"{student['SGPA']}" if student['Has Valid SGPA'] else f"{student['SGPA_Raw']} ❌"
            st.info(f"**SGPA:** {sgpa_display}")
            st.info(f"**Credits:** {student['Credits']}")
        
        with col3:
            status_color = "🟢" if student['Result Status'] == 'Pass' else "🔴"
            sgpa_status = "✅" if student['Has Valid SGPA'] else "❌"
            st.info(f"**Result:** {status_color} {student['Result Status']}")
            st.info(f"**SGPA Status:** {sgpa_status} {'Valid' if student['Has Valid SGPA'] else 'Invalid/Missing'}")
            st.info(f"**Subjects Passed:** {student['Passed Subjects']}/{student['Total Subjects']}")
        
        # Display subject grades
        st.subheader("📚 Subject-wise Grades")
        if student['Subjects']:
            subjects_df = pd.DataFrame(student['Subjects'])
            
            # Add color coding for failed subjects
            def color_failed_subjects(row):
                if row['Grade'] in ['F', 'FF', 'AB', 'IC', 'ABS']:
                    return ['background-color: #ffcccc'] * len(row)
                return [''] * len(row)
            
            styled_df = subjects_df.style.apply(color_failed_subjects, axis=1)
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.warning("No subject data available for this student")
    else:
        st.error("Student not found")

def show_top_performers(analyzer):
    """Display top performers"""
    st.header("🏆 Top Performers")
    
    top_n = st.slider("Number of top students to show", 5, 20, 10)
    top_students = analyzer.get_top_students(top_n)
    
    if not top_students:
        st.warning("❌ No students with valid SGPA found for ranking")
        return
    
    # Create ranking table
    ranking_data = []
    for i, student in enumerate(top_students, 1):
        ranking_data.append({
            'Rank': i,
            'Seat No': student['Seat No'],
            'Name': student['Name'],
            'SGPA': student['SGPA'],
            'Credits': student['Credits'],
            'Result': student['Result Status'],
            'Subjects Passed': f"{student['Passed Subjects']}/{student['Total Subjects']}"
        })
    
    ranking_df = pd.DataFrame(ranking_data)
    st.dataframe(ranking_df, use_container_width=True)
    
    # Visualize top performers
    fig = px.bar(
        ranking_df,
        x='Name',
        y='SGPA',
        title=f"🏅 Top {top_n} Students by SGPA",
        color='SGPA',
        color_continuous_scale='viridis',
        text='SGPA'
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis_range=[0, 10]  # SGPA typically out of 10
    )
    st.plotly_chart(fig, use_container_width=True)

def show_failed_students(analyzer):
    """Display failed students analysis"""
    st.header("❌ Failed Students Analysis")
    
    failed_students = analyzer.get_failed_students()
    
    if not failed_students:
        st.success("🎉 All students passed!")
        return
    
    st.metric("Total Failed Students", len(failed_students))
    
    # Analyze failure reasons
    no_sgpa_count = sum(1 for s in failed_students if not s['Has Valid SGPA'])
    failed_subjects_count = sum(1 for s in failed_students if s['Has Valid SGPA'] and s['Passed Subjects'] < s['Total Subjects'])
    both_reasons_count = sum(1 for s in failed_students if not s['Has Valid SGPA'] and s['Passed Subjects'] < s['Total Subjects'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("No Valid SGPA", no_sgpa_count)
    
    with col2:
        st.metric("Failed Subjects", failed_subjects_count)
    
    with col3:
        st.metric("Both Reasons", both_reasons_count)
    
    # Display failed students table
    failed_data = []
    for student in failed_students:
        failure_reason = []
        if not student['Has Valid SGPA']:
            failure_reason.append("No Valid SGPA")
        if student['Passed Subjects'] < student['Total Subjects']:
            failure_reason.append("Failed Subjects")
        
        failed_data.append({
            'Seat No': student['Seat No'],
            'Name': student['Name'],
            'SGPA': student['SGPA_Raw'],
            'Subjects Passed': f"{student['Passed Subjects']}/{student['Total Subjects']}",
            'Failure Reason': ', '.join(failure_reason)
        })
    
    failed_df = pd.DataFrame(failed_data)
    st.dataframe(failed_df, use_container_width=True)
    
    # Failure reasons pie chart
    failure_reasons = {
        'No Valid SGPA': no_sgpa_count,
        'Failed Subjects': failed_subjects_count,
        'Both Reasons': both_reasons_count
    }
    
    fig = px.pie(
        values=list(failure_reasons.values()),
        names=list(failure_reasons.keys()),
        title="📊 Failure Reasons Distribution",
        color_discrete_sequence=['#FF6B6B', '#FFA726', '#EF5350']
    )
    st.plotly_chart(fig, use_container_width=True)

def show_detailed_analysis(analyzer):
    """Display detailed analysis"""
    st.header("📊 Detailed Analysis")
    
    # Create comprehensive dataframe
    students_df = pd.DataFrame([
        {k: v for k, v in student.items() if k != 'Subjects'} 
        for student in analyzer.students_data
    ])
    
    # Interactive filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_sgpa = st.slider("Minimum SGPA", 0.0, 10.0, 0.0, 0.1)
    
    with col2:
        result_filter = st.selectbox("Result Status", ["All", "Pass", "Fail"])
    
    with col3:
        sgpa_status = st.selectbox("SGPA Status", ["All", "Valid SGPA", "Invalid/Missing SGPA"])
    
    # Apply filters
    filtered_df = students_df[students_df['SGPA'] >= min_sgpa]
    
    if result_filter != "All":
        filtered_df = filtered_df[filtered_df['Result Status'] == result_filter]
    
    if sgpa_status == "Valid SGPA":
        filtered_df = filtered_df[filtered_df['Has Valid SGPA'] == True]
    elif sgpa_status == "Invalid/Missing SGPA":
        filtered_df = filtered_df[filtered_df['Has Valid SGPA'] == False]
    
    st.subheader(f"📋 Filtered Students ({len(filtered_df)} found)")
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download option
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_student_data.csv",
        mime="text/csv"
    )

def show_raw_data(analyzer):
    """Display raw data and extraction information"""
    st.header("📋 Raw Data & Extraction Info")
    
    tab1, tab2 = st.tabs(["Student Data", "Raw Text"])
    
    with tab1:
        st.subheader("All Student Data")
        students_df = pd.DataFrame([
            {k: v for k, v in student.items() if k != 'Subjects'} 
            for student in analyzer.students_data
        ])
        st.dataframe(students_df, use_container_width=True)
        
        # Statistics
        st.subheader("Data Statistics")
        st.write(students_df.describe())
    
    with tab2:
        st.subheader("Raw Extracted Text")
        st.text_area("PDF Text", analyzer.raw_text, height=400)

if __name__ == "__main__":
    main()