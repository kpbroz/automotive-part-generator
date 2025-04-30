import streamlit as st
import requests

# Backend API URLs
UPLOAD_API_URL = "http://localhost:8000/upload-csv/"
ASK_API_URL = "http://localhost:8000/ask-me/"

# Load external CSS file
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load and apply the CSS
load_css("styles.css")

# Add the title
st.markdown('<h1 class="title">Parts generator</h1>', unsafe_allow_html=True)

# File Upload Section
st.header("Upload a CSV File")
uploaded_file = st.file_uploader("Choose a .csv file", type=["csv"])

if st.button("Upload File"):
    if uploaded_file is not None:
        try:
            # Send the file to the upload-csv API
            files = {"file": uploaded_file.getvalue()}
            response = requests.post(UPLOAD_API_URL, files={"file": uploaded_file})
            
            if response.status_code == 200:
                st.success("File uploaded successfully!")
                st.json(response.json())
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload a file before clicking 'Upload File'.")

# Question Section
st.header("Generate parts")
question = st.text_input("Enter part name/ description:")

if st.button("Generate"):
    if question.strip():
        try:
            # Send the question to the ask-me API
            response = requests.post(ASK_API_URL, json={"question": question})
            
            if response.status_code == 200:
                answer = response.json().get("response", "No response")
                st.success("5 Parts generated!")
                st.write(f"{answer}")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a part name/ description before clicking 'Generate'.")

