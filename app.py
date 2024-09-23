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
        background-image: url('bg.jpg'); /* Path to the image in the same folder */
        background-size: cover;
        background-repeat: no-repeat;
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

# Application Title
st.title("Automated Question Builder")

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'role' not in st.session_state:
    st.session_state.role = None

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

    if role == "trainer":
        st.header("Trainer Dashboard")
        page_choice = st.sidebar.selectbox("Select Trainer Page", [
            "Dashboard", "Upload Curriculum", "Generate Question Bank", "Review and Edit Question Bank", "Download Question Bank", "Feedback"
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
            st.subheader("Generate Question Bank Page")
            
            # Option to choose the question input method (PDF or Prompt)
            input_choice = st.selectbox("Choose input method", ["Upload PDF", "Enter Text Prompt"])

            # Option to choose question type (Coding, MCQs, Descriptive, etc.)
            question_type = st.selectbox("Select Question Type", ["Coding", "MCQs", "Descriptive", "True/False"])

            if input_choice == "Upload PDF":
                uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
                if uploaded_file is not None:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        temp_file_path = tmp_file.name

                    loader = PyPDFLoader(temp_file_path)
                    pages = loader.load_and_split()
                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
                    chunks = splitter.split_documents(pages)

                    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                    vectorindex = FAISS.from_documents(chunks, embeddings)
                    os.remove(temp_file_path)

            else:
                topic = st.text_input("Enter the topic for question generation")
                subheadings = st.text_area("Enter subheadings for the topic (one per line)")

                if topic and subheadings:
                    content = f"Topic: {topic}\nSubheadings:\n{subheadings}"
                    chunks = [{'page_content': content}]

            num_questions = st.number_input("Enter the number of questions to generate", min_value=1, value=5)
            difficulty = st.selectbox("Select the difficulty level", ["Easy", "Medium", "Hard"])

            if st.button("Generate Questions"):
                qa_pairs = []
                for i in range(num_questions):
                    chunk = chunks[i % len(chunks)]
                    
                    # Check if 'chunk' is a dictionary or has a 'page_content' attribute
                    if isinstance(chunk, dict):
                        context = chunk['page_content'][:500]
                    else:
                        context = chunk.page_content[:500]  # For PDF chunks

                    # Different prompt template based on the question type
                    if question_type == "Coding":
                        prompt_template = f"Based on the following context, generate a {difficulty.lower()} coding question:\n\nContext: {context}\n\nQuestion:"
                    elif question_type == "MCQs":
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

        elif page_choice == "Review and Edit Question Bank":
            st.subheader("Review and Edit Question Bank Page")
            st.write("View and edit the generated question bank.")

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

    elif role == "trainee":
        st.header("Trainee Dashboard")
        trainee_page_choice = st.sidebar.selectbox("Select Trainee Page", [
            "Dashboard", "Generate Questions from Curriculum"
        ])

        if trainee_page_choice == "Dashboard":
            st.subheader("Trainee Dashboard")
            st.write("Access your learning resources and generated questions.")

        elif trainee_page_choice == "Generate Questions from Curriculum":
            st.subheader("Generate Questions from Curriculum Page")
            topic = st.text_input("Enter Topic")
            num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=5)
            if st.button("Generate"):
                qa_pairs = generate_questions_from_topic(topic, num_questions)
                df = pd.DataFrame({"Questions": qa_pairs})
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(label="Download as CSV", data=csv, file_name='generated_trainee_questions.csv', mime='text/csv')

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
