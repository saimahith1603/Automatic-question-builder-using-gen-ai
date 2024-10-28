import os
import streamlit as st
import pandas as pd
import tempfile
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from login_register import check_login, register_user  # Import login/register functions
import pickle
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import uuid
from datetime import datetime
import json
import csv
import io
import base64
from fpdf import FPDF 
# Set up the LLM
api_key = "YOUR_API_KEY"
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=1.0)
os.environ["GOOGLE_API_KEY"] = api_key


# creating the dynamo tables 
dynamodb = boto3.resource('dynamodb', 
    aws_access_key_id='YOUR_ACCESS_KEY', 
    aws_secret_access_key='YOUR_SECRET_ACCESS_KEY', 
    region_name='us-east-1'
)
feedback_table = dynamodb.Table('FeedbackTable')  # Feedback table
user_table = dynamodb.Table('User')
learning_table = dynamodb.Table('learning')
issue_table = dynamodb.Table('Issue')
questions_table = dynamodb.Table('Question')


def create_pdf(qa_pairs):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=12)

    print(qa_pairs)  # Check the structure of qa_pairs

    for pair in qa_pairs:
        if len(pair) == 2:
            question, answer = pair
            pdf.multi_cell(0, 10, f"Q: {question}")
            pdf.multi_cell(0, 10, f"A: {answer}\n")
        else:
            print(f"Unexpected pair structure: {pair}")

    return pdf.output(dest='S').encode('utf-8')
 # Change latin1 to utf-8


def submit_issue_resolution(resolution, data):
    try:
        issue_id = str(uuid.uuid4())
        issue_table.put_item(Item={
            'Resolution': resolution,
            'Data': data,
            'IssueID': issue_id
        })
        st.success("Resolution submitted successfully.")
    except ClientError as e:
        st.error(f"Error submitting issue resolution: {e.response['Error']['Message']}")

def fetch_issue_resolutions():
    try:
        response = issue_table.scan()
        items = response.get('Items', [])
        return items
    except ClientError as e:
        st.error(f"Error fetching issue resolutions: {e}")
        return []


def submit_learning_request(technology, areas):
    # Initialize a session using Amazon DynamoDB
    session = boto3.Session()
    dynamodb = session.resource('dynamodb')
    
    # Select your DynamoDB table
    table = dynamodb.Table('learning')

    # Create a dictionary for the item to be inserted
    item = {
        'technology': technology,
        'areas': areas
    }

    try:
        # Insert the item into the DynamoDB table
        table.put_item(Item=item)
        print("Learning request submitted successfully.")
    
    except ClientError as e:
        print(f"Error submitting learning request: {e.response['Error']['Message']}")

# Function to fetch learning requests for trainers
def fetch_learning_requests():
    try:
        response = learning_table.scan()  # Use scan to get all items if no specific condition
        items = response.get('Items', [])
        if not items:
            st.write("No learning requests found in the database.")
        return items
    except Exception as e:
        st.error(f"Error retrieving learning requests: {e}")
        return []


# Function to submit feedback
def submit_feedback(username, feedback):
    feedback_id = str(uuid.uuid4())  # Generate a unique FeedbackID
    try:
        feedback_table.put_item(Item={
            'FeedbackID': feedback_id,
            'Username': username,
            'Feedback': feedback,
            # Add other attributes as necessary
        })
        print("Feedback submitted successfully!")
    except Exception as e:
        print(f"Error submitting feedback: {e}")
# Function to get feedback for admin
def fetch_feedback():
    try:
        response = feedback_table.scan()  # Use scan to get all items if no specific condition
        items = response.get('Items', [])
        if not items:
            st.write("No feedback data found in the database.")
        return items
    except Exception as e:
        st.error(f"Error retrieving feedback data: {e}")
        return []

def update_admin_response(username, feedback_id, admin_response):
    feedback_table.update_item(
        Key={'FeedbackID': feedback_id},
        UpdateExpression='SET AdminResponse = :response',
        ExpressionAttributeValues={':response': admin_response}
    )


def fetch_users():
    try:
        # Scan the table to get all users
        response = user_table.scan()
        users = response['Items']
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []   


def add_user(username, password, role):
    user_table.put_item(
    Item={
            'Name': username,
            'Password': password,
            'Role': role              # Add other required attributes as per your table schema
    }
)

def remove_user(name, password):
    try:
        response = user_table.delete_item(
            Key={
                'Name': name,
                'Password': password
            }
        )
        return True
    except ClientError as e:
        st.error(e.response['Error']['Message'])
        return False

# Function to update a user's role
def update_user(name, password, new_role):
    try:
        response = user_table.update_item(
            Key={
                'Name': name,
                'Password': password
            },
            UpdateExpression='SET #r = :val1',
            ExpressionAttributeNames={
                '#r': 'Role'  # Using #r to refer to the reserved keyword
            },
            ExpressionAttributeValues={
                ':val1': new_role
            }
        )
        return True
    except ClientError as e:
        st.error(e.response['Error']['Message'])
        return False

# Streamlit UI with Enhanced CSS (CSS Code Remains the Same)
# Streamlit UI with Enhanced CSS
st.markdown(
    """
    <style>
    /* General App Styling */
    .stApp {
        background-image: url("https://img.freepik.com/free-photo/questioning-concept-with-question-mark_23-2150408203.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        filter: brightness(0.8); /* Slight dim for better visibility */
    }
    
    /* Importing Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;700&display=swap');
    
    /* Font Styling for Body */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        color: #FFFFFF;
    }
    
    /* Title Styling */
    .stTitle {
        color: #FFD700;
        text-align: center;
        font-size: 2.8em;
        margin-top: 20px;
        font-weight: 700;
        text-shadow: 2px 2px 6px #000000;
    }
    
    /* Markdown Text Styling */
    .stMarkdown {
        color: #F5F5F5;
        font-size: 1.2em;
        line-height: 1.6;
        text-align: justify;
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: #FF5733;
        color: white;
        border-radius: 12px;
        font-size: 1.3em;
        padding: 10px 25px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #C70039;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
        transform: scale(1.05);
    }
    
    /* DataFrame Styling */
    .stDataFrame {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 12px;
        padding: 10px;
        font-size: 1.1em;
        color: #000;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Input Styling with Image Background */
    input[type="text"] {
        width: 100%;
        padding: 12px;
        font-size: 1.2em;
        border-radius: 10px;
        border: 2px solid #ccc;
        color: #fff;
        font-weight: 400;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    
    input[type="text"]:focus {
        border-color: #6c63ff;
        outline: none;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* Styling the Sidebar */
    .css-1lcbmhc {
        background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent background for the sidebar */
        padding: 15px;
    }

    /* Sidebar button styling */
    .css-1l02zno {
        background-color: #FF5733 !important;
        border: none;
        color: white !important;
        font-size: 1.2em;
    }
    
    .css-1l02zno:hover {
        background-color: #C70039 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Automated Question Builder")

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'role' not in st.session_state:
    st.session_state.role = None

# Authentication Section (Remains unchanged)

# Admin/Employee roles with the necessary dashboard options
if not st.session_state.authenticated:
    auth_choice = st.selectbox("Login or Register", ["Login", "Register"])
    if auth_choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            role = check_login(username, password)
            if role:
                st.session_state.authenticated = True
                st.session_state.role = role
                st.success(f"Logged in as {role}.")
            else:
                st.error("Login failed. Please check your credentials.")
    else:
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        role = st.selectbox("Select Role", ["admin", "trainer", "employee"])
        if st.button("Register"):
            register_user(new_username, new_password, role)
            st.success("Registration successful! Please log in.")
else:
    role = st.session_state.role

    # Logout button
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.success("You have been logged out.")

    if role == "admin":
        st.header("Administrator Dashboard")
        admin_page_choice = st.sidebar.selectbox("Select Admin Page", [
            "Manage Users", "Generate Reports", "Issue Resolution", "Feedback Management", "Learning Requests"
        ])

        if admin_page_choice == "Manage Users":
            st.subheader("User Management")
            action_choice = st.selectbox("Select Action", ["Add New User", "Remove User", "Update User Roles"])
            if action_choice == "Add New User":
                new_user = st.text_input("New User Username")
                new_password = st.text_input("New User Password", type="password")
                new_role = st.selectbox("Assign Role", ["trainer", "employee"])
                if st.button("Add User"):
                    add_user(new_user, new_password, new_role)
            elif action_choice == "Remove User":
                users = fetch_users()
                remove_name = st.text_input("Enter Name to Remove")
                remove_password = st.text_input("Enter Password to Remove", type="password")
                if st.button("Remove User"):
                    if remove_user(remove_name, remove_password):
                        st.success("User removed successfully!")
            elif action_choice == "Update User Roles":
                users = fetch_users()
                update_name = st.text_input("Enter Name to Update")
                update_password = st.text_input("Enter Password to Update", type="password")
                new_user_role = st.selectbox("Select New Role", ["Admin", "employee"])  # Adjust roles as needed
                if st.button("Update User"):
                    if update_user(update_name, update_password, new_user_role):
                        st.success("User role updated successfully!")

            # Placeholder for performance metrics
        elif admin_page_choice == "Generate Reports":
            st.subheader("Generate Reports")
            report_type = st.selectbox("Select Report Type", ["Usage Statistics", "Question Bank Summaries", "System Health"])
            if st.button("Generate Report"):
                st.success(f"{report_type} generated successfully.")

        elif admin_page_choice == "Issue Resolution":
            st.header("Issue Resolution")
            resolution = st.text_area("Enter Issue Resolution")
            data = st.text_area("Enter Issue Data")
            if st.button("Submit Resolution"):
                submit_issue_resolution(resolution, data)

        elif admin_page_choice == "Feedback Management":
            st.subheader("Feedback from Trainers")
            feedback_items = fetch_feedback()
            if feedback_items: 
                for item in feedback_items:
                    st.write(f"User: {item['Username']}, Feedback: {item['Feedback']}")
                    
            else:
                st.write("No feedback data found.")
        elif admin_page_choice == "Learning Requests":
            st.header("Learning Requests")
            learning_requests = fetch_learning_requests()
            if learning_requests:
                for request in learning_requests:
                    st.write(f"Technology: {request['technology']}, Areas of Interest: {request['areas']}")
            else:
                st.write("No learning requests found.")        

    elif role == "trainer":
        st.header("Trainer Dashboard")
        page_choice = st.sidebar.selectbox("Select Trainer Page", [
            "Dashboard", "Upload Curriculum", "Generate Question Bank", "Feedback", "Learning Requests"
        ])

        if page_choice == "Dashboard":
            st.subheader("Trainer Dashboard")
            st.write("Quick access to curriculum uploads, question bank generation, and reviews.")

        elif page_choice == "Upload Curriculum":
            st.subheader("Upload Curriculum Page")
            technology = st.selectbox("Select Technology", ["Python", "Java", "JavaScript"])
            uploaded_file = st.file_uploader("Upload curriculum (CSV/Excel)", type=["csv", "xlsx"])
            if uploaded_file:
                st.write(f"File uploaded: {uploaded_file.name}")
                st.success("Upload complete.")

        elif page_choice == "Generate Question Bank":
            st.subheader("Generate Questions")
            generation_method = st.radio("Select Question Generation Method", ("Upload PDF", "Enter Prompt"))

            if generation_method == "Upload PDF":
                uploaded_pdf = st.file_uploader("Upload PDF", type="pdf")
                if uploaded_pdf:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(uploaded_pdf.read())
                        tmp_file_path = tmp_file.name
                    
                    # Process the PDF
                    loader = PyPDFLoader(tmp_file_path)
                    documents = loader.load()
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                    chunks = text_splitter.split_documents(documents)
                    context = " ".join(chunk.page_content for chunk in chunks)

                    question_type = st.selectbox("Select Question Type", ["MCQs", "True/False", "Descriptive"])
                    difficulty = st.selectbox("Select Difficulty Level", ["Easy", "Medium", "Hard"])
                    num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=5)
                    if st.button("Generate Questions"):
                        qa_pairs = []
                        for _ in range(num_questions):
                            if question_type == "MCQs":
                                prompt_template = f"Based on the following context, generate a {difficulty.lower()} multiple-choice question with options:\n\nContext: {context}\n\nQuestion:"
                            elif question_type == "True/False":
                                prompt_template = f"Based on the following context, generate a {difficulty.lower()} true/false question:\n\nContext: {context}\n\nQuestion:"
                            else:  # Descriptive questions
                                prompt_template = f"Based on the following context, generate a {difficulty.lower()} descriptive question and provide a detailed answer:\n\nContext: {context}\n\nQuestion:"
                            
                            try:
                                response = llm.generate([prompt_template])
                                qa_pair = response.generations[0][0].text.strip() if response and len(response.generations) > 0 else "No question generated."
                                qa_pairs.append(qa_pair)
                            except Exception as e:
                                qa_pairs.append(f"Error generating question: {e}")

                        # Save questions to a DataFrame and allow download
                        df = pd.DataFrame({"Questions": qa_pairs})
                        st.dataframe(df)
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(label="Download as CSV", data=csv, file_name='generated_questions_and_answers.csv', mime='text/csv')
                        pdf_data = create_pdf(qa_pairs)
                        st.download_button(label="Download as PDF", data=pdf_data, file_name='generated_questions_and_answers.pdf', mime='application/pdf')

            elif generation_method == "Enter Prompt":
                context = st.text_area("Enter context for question generation")
                question_type = st.selectbox("Select Question Type", ["MCQs", "True/False", "Descriptive"])
                difficulty = st.selectbox("Select Difficulty Level", ["Easy", "Medium", "Hard"])
                num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=5)
                if st.button("Generate Questions"):
                    qa_pairs = []
                    for _ in range(num_questions):
                        if question_type == "MCQs":
                            prompt_template = f"Based on the following context, generate a {difficulty.lower()} multiple-choice question with options:\n\nContext: {context}\n\nQuestion:"
                        elif question_type == "True/False":
                            prompt_template = f"Based on the following context, generate a {difficulty.lower()} true/false question:\n\nContext: {context}\n\nQuestion:"
                        else:  # Descriptive questions
                            prompt_template = f"Based on the following context, generate a {difficulty.lower()} descriptive question and provide a detailed answer:\n\nContext: {context}\n\nQuestion:"
                        
                        try:
                            response = llm.generate([prompt_template])
                            qa_pair = response.generations[0][0].text.strip() if response and len(response.generations) > 0 else "No question generated."
                            qa_pairs.append(qa_pair)
                        except Exception as e:
                            qa_pairs.append(f"Error generating question: {e}")

                    # Save questions to a DataFrame and allow download
                    df = pd.DataFrame({"Questions": qa_pairs})
                    st.dataframe(df)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(label="Download as CSV", data=csv, file_name='generated_questions_and_answers.csv', mime='text/csv')
                    pdf_data = create_pdf(qa_pairs)
                    st.download_button(label="Download as PDF", data=pdf_data, file_name='generated_questions_and_answers.pdf', mime='application/pdf')
        
        elif page_choice == "Feedback":
            st.subheader("Feedback Page")
            feedback_items = fetch_feedback()
            if feedback_items: 
                for item in feedback_items:
                    st.write(f"User: {item['Username']}, Feedback: {item['Feedback']}")
                    
        elif page_choice == "Learning Requests":
            st.header("Learning Requests")
            learning_requests = fetch_learning_requests()
            if learning_requests:
                for request in learning_requests:
                    st.write(f"Technology: {request['technology']}, Areas of Interest: {request['areas']}")
            else:
                st.write("No learning requests found.")

    elif role == "employee":
        st.header("Employee Dashboard")
        emp_page_choice = st.sidebar.selectbox("Select Employee Page", [
            "Dashboard",  "Feedback Submission", "Generate Question Bank", "Learning and Development", "Request Learning Plan", "Issue Resolutions"
        ])

        if emp_page_choice == "Dashboard":
            st.subheader("Employee Dashboard")
            st.write("Access your assigned curriculum and feedback options.")

        elif emp_page_choice == "Feedback Submission":
            st.header("Feedback Submission")
            username = st.text_input("Username")
            feedback = st.text_area("Provide feedback on the generated questions.")
            if st.button("Submit Feedback"):
                submit_feedback(username, feedback)
                st.success("Feedback submitted successfully.")

        elif emp_page_choice == "Generate Question Bank":
            generation_method = st.radio("Select Question Generation Method", ("Upload PDF", "Enter Prompt"))

            if generation_method == "Upload PDF":
                uploaded_pdf = st.file_uploader("Upload PDF", type="pdf")
                if uploaded_pdf:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(uploaded_pdf.read())
                        tmp_file_path = tmp_file.name
                    
                    # Process the PDF
                    loader = PyPDFLoader(tmp_file_path)
                    documents = loader.load()
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                    chunks = text_splitter.split_documents(documents)
                    context = " ".join(chunk.page_content for chunk in chunks)

                    question_type = st.selectbox("Select Question Type", ["MCQs", "True/False", "Descriptive"])
                    difficulty = st.selectbox("Select Difficulty Level", ["Easy", "Medium", "Hard"])
                    num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=5)
                    if st.button("Generate Questions"):
                        qa_pairs = []
                        for _ in range(num_questions):
                            if question_type == "MCQs":
                                prompt_template = f"Based on the following context, generate a {difficulty.lower()} multiple-choice question with options:\n\nContext: {context}\n\nQuestion:"
                            elif question_type == "True/False":
                                prompt_template = f"Based on the following context, generate a {difficulty.lower()} true/false question:\n\nContext: {context}\n\nQuestion:"
                            else:  # Descriptive questions
                                prompt_template = f"Based on the following context, generate a {difficulty.lower()} descriptive question and provide a detailed answer:\n\nContext: {context}\n\nQuestion:"
                            
                            try:
                                response = llm.generate([prompt_template])
                                qa_pair = response.generations[0][0].text.strip() if response and len(response.generations) > 0 else "No question generated."
                                qa_pairs.append(qa_pair)
                            except Exception as e:
                                qa_pairs.append(f"Error generating question: {e}")

                        # Save questions to a DataFrame and allow download
                        df = pd.DataFrame({"Questions": qa_pairs})
                        st.dataframe(df)
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(label="Download as CSV", data=csv, file_name='generated_questions_and_answers.csv', mime='text/csv')
                        pdf_data = create_pdf(qa_pairs)
                        st.download_button(label="Download as PDF", data=pdf_data, file_name='generated_questions_and_answers.pdf', mime='application/pdf')
            elif generation_method == "Enter Prompt":
                context = st.text_area("Enter context for question generation")
                question_type = st.selectbox("Select Question Type", ["MCQs", "True/False", "Descriptive"])
                difficulty = st.selectbox("Select Difficulty Level", ["Easy", "Medium", "Hard"])
                num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=5)
                if st.button("Generate Questions"):
                    qa_pairs = []
                    for _ in range(num_questions):
                        if question_type == "MCQs":
                            prompt_template = f"Based on the following context, generate a {difficulty.lower()} multiple-choice question with options:\n\nContext: {context}\n\nQuestion:"
                        elif question_type == "True/False":
                            prompt_template = f"Based on the following context, generate a {difficulty.lower()} true/false question:\n\nContext: {context}\n\nQuestion:"
                        else:  # Descriptive questions
                            prompt_template = f"Based on the following context, generate a {difficulty.lower()} descriptive question and provide a detailed answer:\n\nContext: {context}\n\nQuestion:"
                        
                        try:
                            response = llm.generate([prompt_template])
                            qa_pair = response.generations[0][0].text.strip() if response and len(response.generations) > 0 else "No question generated."
                            qa_pairs.append(qa_pair)
                        except Exception as e:
                            qa_pairs.append(f"Error generating question: {e}")

                    # Save questions to a DataFrame and allow download
                    df = pd.DataFrame({"Questions": qa_pairs})
                    st.dataframe(df)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(label="Download as CSV", data=csv, file_name='generated_questions_and_answers.csv', mime='text/csv')
                    pdf_data = create_pdf(qa_pairs)
                    st.download_button(label="Download as PDF", data=pdf_data, file_name='generated_questions_and_answers.pdf', mime='application/pdf')
        elif emp_page_choice == "Learning and Development":
            st.subheader("Learning and Development")
            st.write("Access learning materials and track progress.")

        elif emp_page_choice == "Request Learning Plan":
            st.subheader("Request Learning Plan for Technical Upskill")
            technology = st.text_input("Desired Technology")
            areas = st.text_input("Specific Area of Interest")
            if st.button("Submit Request"):
                submit_learning_request(technology, areas)
        elif emp_page_choice == "Issue Resolutions":
            st.header("Issue Resolutions")
            resolutions = fetch_issue_resolutions()
            if resolutions:
                for item in resolutions:
                    st.write(f"Resolution: {item['Resolution']}")
                    st.write(f"Data: {item['Data']}")
                    st.write("---")
            else:
                st.write("No resolutions found.")

# Function to generate questions from topic
def generate_questions_from_topic(topic, num_questions):
    qa_pairs = []
    # Dummy question generation logic, replace with your own
    for i in range(num_questions):
        qa_pairs.append(f"{topic} question {i + 1}")
    return qa_pairs   

# Closing the Streamlit app
if __name__ == "__main__":
    st.write("Thank you for using the Automated Question Builder!")

