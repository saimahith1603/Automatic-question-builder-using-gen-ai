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

# Set up the LLM
api_key = "YOUR_API_KEY"
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=1.0)
os.environ["GOOGLE_API_KEY"] = api_key

# Streamlit UI with Enhanced CSS (CSS Code Remains the Same)
# Streamlit UI with Enhanced CSS
st.markdown(
    """
    <style>
    /* General App Styling */
    .stApp {
        background-image: url("YOUR_BACKGROUND_IMAGE");
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
            "Manage Users", "Generate Reports", "Issue Resolution"
        ])

        if admin_page_choice == "Manage Users":
            st.subheader("User Management")
            action_choice = st.selectbox("Select Action", ["Add New User", "Remove User", "Update User Roles"])
            if action_choice == "Add New User":
                new_user = st.text_input("New User Username")
                new_password = st.text_input("New User Password", type="password")
                new_role = st.selectbox("Assign Role", ["trainer", "employee"])
                if st.button("Add User"):
                    # Logic to add user
                    st.success(f"User {new_user} added successfully with role {new_role}.")
            elif action_choice == "Remove User":
                user_to_remove = st.selectbox("Select User to Remove", ["User1", "User2"])  # Replace with actual user list
                if st.button("Remove User"):
                    # Logic to remove user
                    st.success(f"User {user_to_remove} removed successfully.")
            elif action_choice == "Update User Roles":
                user_to_update = st.selectbox("Select User to Update", ["User1", "User2"])  # Replace with actual user list
                new_user_role = st.selectbox("New Role", ["trainer", "employee"])
                if st.button("Update Role"):
                    # Logic to update user role
                    st.success(f"User {user_to_update}'s role updated to {new_user_role}.")
            # Placeholder for performance metrics
        elif admin_page_choice == "Generate Reports":
            st.subheader("Generate Reports")
            report_type = st.selectbox("Select Report Type", ["Usage Statistics", "Question Bank Summaries", "System Health"])
            if st.button("Generate Report"):
                st.success(f"{report_type} generated successfully.")

        elif admin_page_choice == "Issue Resolution":
            st.subheader("Issue Resolution")
            reported_issue = st.text_area("Describe the Issue")
            if st.button("Submit Issue"):
                st.success("Issue submitted for investigation.")

    elif role == "trainer":
        st.header("Trainer Dashboard")
        page_choice = st.sidebar.selectbox("Select Trainer Page", [
            "Dashboard", "Upload Curriculum", "Generate Question Bank","Download Question Bank", "Feedback"
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
        elif page_choice == "Download Question Bank":
            st.subheader("Download Question Bank Page")
            format_choice = st.selectbox("Select format", ["Excel", "PDF"])
            if st.button("Download"):
                st.success(f"Question bank downloaded as {format_choice}.")
        elif page_choice == "Feedback":
            st.subheader("Feedback Page")
            feedback = st.text_area("Provide feedback on the generated questions.")
            if st.button("Submit Feedback"):
                st.success("Feedback submitted.")

    elif role == "employee":
        st.header("Employee Dashboard")
        emp_page_choice = st.sidebar.selectbox("Select Employee Page", [
            "Dashboard",  "Feedback Submission", "Learning and Development", "Request Learning Plan"
        ])

        if emp_page_choice == "Dashboard":
            st.subheader("Employee Dashboard")
            st.write("Access your assigned curriculum and feedback options.")

        elif emp_page_choice == "Feedback Submission":
            st.subheader("Feedback Submission")
            feedback = st.text_area("Provide feedback on the question bank.")
            if st.button("Submit Feedback"):
                st.success("Feedback submitted.")

        elif emp_page_choice == "Learning and Development":
            st.subheader("Learning and Development")
            st.write("Access learning materials and track progress.")

        elif emp_page_choice == "Request Learning Plan":
            st.subheader("Request Learning Plan for Technical Upskill")
            technology = st.text_input("Desired Technology")
            areas_of_improvement = st.text_area("Specific Areas for Improvement")
            learning_goals = st.text_area("Learning Goals")
            if st.button("Submit Request"):
                st.success("Request for personalized learning plan submitted successfully.")

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
