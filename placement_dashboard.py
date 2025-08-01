import streamlit as st
import mysql.connector
import pandas as pd
DB_CONFIG={
    'host':'localhost',
    'user':'root',
    'password':'12345',
    'database':'placement_db'
    }
class DataBaseManager:
    def __init__(self,**kwargs):
        self.conn=mysql.connector.connect(
            host=kwargs['host'],
            user=kwargs['user'],
            password=kwargs['password'],
            database=kwargs['database']
            )
        self.cursor=self.conn.cursor()
    def run_query(self,query,params=None):
        if params:
            self.cursor.execute(query,params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()
    def close(self):
        self.conn.close()
    
st.title('Welcome To GUVI Placement Dashboard')
options=[
    'Placement Data Filter',
    'Students Who Got Placed',
    'Students Not Placed',
    'Top Packages',
    'Company Wise Placed Student Count',
    'Students With Minimum Problems Solved in Python',
    'Students With Minimum Problems Solved In SQL',
    'Students With Minimum Average Softskill Score',
    'Students With Minimum Teamwork',
    'Students With Good Communication Skill',
    'Students With Minimum Mock Interview Scores'
]
select=st.sidebar.selectbox('Choose a Query',options)
db=DataBaseManager(**DB_CONFIG)
if select=='Placement Data Filter':
    min_problems_solved_in_python=st.number_input('Minimum Problems Solved In python',0,500,50)
    min_problems_solved_in_sql=st.number_input('Minimum Problems Solved In Python',0,100,10)
    min_softskills=st.number_input('Minimum Average Softskill',0,100,60)
    min_mockinterview_score=st.number_input('Minimum Mock Interview Score',0,100,60)
    min_mini_projects_completed=st.number_input('Minimum Mini Projects Completed',1,5,1)
    min_latest_project_score=st.number_input('Minimum Latest Project Score',50,100,60)
    min_package=st.number_input('Minimum Package (Rupees - Lakhs Per Anum)',0,1500000,0)

    if st.button('Run Filter'):
        query='''SELECT s.student_id,s.name,p.programs_solved_in_py,p.programs_solved_in_sql,ss.Average_score,pl.mock_interview_score,p.mini_projects,p.latest_project_score,pl.placement_package
        FROM students s 
        JOIN programs p ON s.student_id=p.student_id
        JOIN softskills ss ON s.student_id=ss.student_id
        JOIN placements pl ON s.student_id=pl.student_id
        WHERE p.programs_solved_in_py >=%s
        AND p.programs_solved_in_sql >= %s
        AND ss.Average_score>=%s
        AND pl.mock_interview_score>=%s
        AND p.mini_projects >= %s
        AND p.latest_project_score>=%s
        AND pl.placement_package>=%s ORDER BY pl.placement_package DESC;'''
        results=db.run_query(query,(min_problems_solved_in_python,min_problems_solved_in_sql,min_softskills,min_mockinterview_score,min_mini_projects_completed,min_latest_project_score,min_package))
        df=pd.DataFrame(results,columns=['Student ID','Name','Python Solved','SQL Solved','Average Softskill Score','Mock Interview','Mini Projects','Latest Projects','Placement Package (₹)'])
        st.data_editor(df)
elif select=="Students Who Got Placed":
    results=db.run_query('''SELECT s.student_id,s.name,s.gender,p.company_name,p.placement_package,p.placement_date from students s
                          JOIN placements p ON s.student_id=p.student_id WHERE p.placement_status='Placed' Order by p.placement_package DESC; ''')
    df=pd.DataFrame(results,columns=(['Student ID','Name','Gender','Company Name','Package (₹)','Placed Date']))
    st.dataframe(df)
elif select=='Students Not Placed':
    results=db.run_query('''SELECT s.student_id,s.name,s.gender,p.mock_interview_score,p.internships_completed,p.interview_rounds_cleared FROM students s 
                         JOIN placements p on s.student_id=p.student_id
                         WHERE p.placement_status!='Placed'; ''')
    df=pd.DataFrame(results,columns=(['Sudent ID','Name','Gender','Mock Score','Internship Count','Interview Round Cleared']))
    st.dataframe(df)
elif select=='Top Packages':
    top_placement=st.number_input('Top packages',1,500,10)
    if st.button('Provide List'):
        query='''SELECT s.student_id,s.name,s.gender,p.company_name,p.placement_package FROM students s
                JOIN placements p ON s.student_id=p.student_id WHERE p.placement_status='Placed' ORDER BY p.placement_package DESC LIMIT %s ;'''
        results=db.run_query(query,(top_placement,))
        df=pd.DataFrame(results,columns=(['Student ID','Name','Gender','Company Name','Package(₹)']))
        st.dataframe(df)
elif select=='Company Wise Placed Student Count':
    query='''SELECT company_name, COUNT(*) AS Total_students, AVG(placement_package) AS averagesalary,MAX(placement_package) AS max_salary,MIN(placement_package) AS min_salary
            FROM placements WHERE placement_status='Placed' GROUP BY company_name ORDER BY averagesalary DESC;'''
    results=db.run_query(query)
    df=pd.DataFrame(results,columns=(['Company Name','Placed Students Count','Average CTC','Highest Package','Minimum Package']))

    st.dataframe(df)
elif select=='Students With Minimum Problems Solved in Python':
    minimum_problems=st.number_input('Minimum Problems Solved In python',1,500,50)
    if st.button('Provide List'):
        query='''SELECT s.student_id,s.name,p.programs_solved_in_py from students s
        JOIN programs p on s.student_id=p.student_id WHERE p.programs_solved_in_py>=%s ORDER BY p.programs_solved_in_py DESC'''
        results=db.run_query(query,(minimum_problems,))
        df=pd.DataFrame(results,columns=(['Student ID','Name','Programs Solved In Python']))
        st.dataframe(df)
elif select=='Students With Minimum Problems Solved In SQL':
    minimum_problems=st.number_input('Minimum Problems Solved In SQL',1,100,10)
    if st.button('Provide List'):
        query='''SELECT s.student_id,s.name,p.programs_solved_in_sql from students s
        JOIN programs p on s.student_id=p.student_id WHERE p.programs_solved_in_sql>=%s ORDER BY p.programs_solved_in_sql DESC'''
        results=db.run_query(query,(minimum_problems,))
        df=pd.DataFrame(results,columns=(['Student ID','Name','Programs Solved In SQL']))
        st.dataframe(df)
elif select=='Students With Minimum Average Softskill Score':
    minimum_score=st.number_input('Minimum Average Softskill Score',1,100,50)
    if st.button('Provide List'):
        query='''SELECT s.student_id,s.name,ss.communication,ss.presentation,ss.critical_thinking,ss.average_score FROM students s
        JOIN softskills ss on s.student_id=ss.student_id WHERE ss.Average_score>=%s ORDER BY ss.average_score DESC'''
        results=db.run_query(query,(minimum_score,))
        df=pd.DataFrame(results,columns=(['Student ID','Name','Communication','Presentation','Critical Thinking','Average Score']))
        st.dataframe(df)
elif select=='Students With Minimum Teamwork':
    minimum_score=st.number_input('Minimum Average Teamwork Score',1,100,50)
    if st.button('Provide List'):
        query='''SELECT s.student_id,s.name,ss.teamwork FROM students s
        JOIN softskills ss on s.student_id=ss.student_id WHERE ss.teamwork>=%s ORDER BY ss.teamwork DESC'''
        results=db.run_query(query,(minimum_score,))
        df=pd.DataFrame(results,columns=(['Student ID','Name','Teamwork']))
        st.dataframe(df)
elif select=='Students With Good Communication Skill':
    minimum_score=st.number_input('Minimum Average Communication Score',1,100,50)
    if st.button('Provide List'):
        query='''SELECT s.student_id,s.name,ss.communication FROM students s
        JOIN softskills ss on s.student_id=ss.student_id WHERE ss.communication>=%s ORDER BY ss.communication DESC'''
        results=db.run_query(query,(minimum_score,))
        df=pd.DataFrame(results,columns=(['Student ID','Name','Communication']))
        st.dataframe(df)
elif select=='Students With Minimum Mock Interview Scores':
    minimum_score=st.number_input('Minimum Mock Interview Score',1,100,50)
    if st.button('Provide List'):
        query='''SELECT s.student_id,s.name,p.mock_interview_score FROM students s
        JOIN placements p on s.student_id=p.student_id WHERE p.mock_interview_score>=%s ORDER BY p.mock_interview_score DESC'''
        results=db.run_query(query,(minimum_score,))
        df=pd.DataFrame(results,columns=(['Student ID','Name','Mock Interview Score']))
        st.dataframe(df)