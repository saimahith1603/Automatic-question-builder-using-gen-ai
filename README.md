# Automated Question Builder

## Overview
The Automated Question Builder is a web application designed to help users generate questions from uploaded PDF documents or text prompts. It supports user authentication and provides various question types, allowing for a customizable experience tailored to trainers and trainees.

## Features
- Automated Question Generation: Generate questions from input PDFs or manually entered topics.
- PDF Export: Save generated questions and answers in a downloadable PDF.
- Database Storage: Store questions in AWS DynamoDB for later access and retrieval.
- User Management: Role-based login and registration system.
- Feedback System: Trainers can submit feedback, which admins can view and respond to.
- Issue Resolution: Admins can add resolutions to common issues for employees to view.
## Installation

### Prerequisites
Before you begin, ensure you have the following installed on your system:
- Python 3.7 or later
- pip (Python package installer)
- Python 3.x
- Streamlit
- FPDF
- AWS SDK (for DynamoDB integration)

### Step 1: Clone the Repository
Open your terminal or command prompt and run the following command:
```bash
git clone https://github.com/yourusername/automated-question-builder.git
cd automated-question-builder
```
### Step 2: Create a Virtual Environment (Optional but Recommended)
Creating a virtual environment helps manage dependencies for your project.
```bash
Copy code
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```
### Step 3: Install Required Packages
Install the necessary packages using the following command:
```bash
pip install -r requirements.txt
```
### Step 4: Run the Application
To start the application, execute:
```bash

streamlit run app.py
```
### Step 5: Access the Application
Open your web browser and navigate to http://localhost:8501 to access the application.

### Step 6: User Authentication
Choose to Login or Register.
If registering, fill in the new username, password, and select a role.
If logging in, provide your username and password.
### Step 7: Generating Questions
After logging in, select the appropriate page from the sidebar.
Choose whether to upload a PDF or enter a text prompt.
Select the type of questions you wish to generate.
Specify the number of questions and their difficulty level.
Click on Generate Questions to view the generated questions.
Download the questions as a CSV file if desired.
Working Procedure
Login/Register: Users authenticate to gain access to the system.
Curriculum Upload: Trainers can upload curricula in CSV/Excel format for question generation.
Question Generation: Users can generate questions from either uploaded PDFs or text prompts.
Review and Download: Users can review, edit, and download the generated question bank.
Contributing
We welcome contributions! Feel free to submit issues or pull requests.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgments
Streamlit
LangChain
Google Generative AI
markdown

### Instructions:
- Replace `yourusername` in the cloning section with your actual GitHub username.
- Ensure you have a `requirements.txt` file that lists all the dependencies used in your project.
- Adjust any details specific to your project as necessary.
