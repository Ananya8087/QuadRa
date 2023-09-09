import yaml
import boto3
import pandas
import streamlit as st
from langchain import OpenAI
from pdf_loaders import PdfToTextLoader
from dataset_vectorizers import DatasetVectorizer
from langchain import OpenAI, VectorDBQA, LLMChain
from PyPDF2 import PdfReader
from io import BytesIO
import PyPDF2
import tempfile
import os

# Creating the low level functional client
client = boto3.client(
    's3',
    aws_access_key_id = '',
    aws_secret_access_key = '',
    region_name = ''
)

    
# Creating the high level object oriented interface
resource = boto3.resource(
    's3',
    aws_access_key_id = '',
    aws_secret_access_key = '',
    region_name = ''
)

# Fetch the list of existing buckets
clientResponse = client.list_buckets()
    
# Print the bucket names one by one
print('Printing bucket names...')
for bucket in clientResponse['Buckets']:
    print(f'Bucket Name: {bucket["Name"]}')
    
obj = client.get_object(
    Bucket = '',
    Key = ''
)
pdf_data = obj['Body'].read()

# Create a PdfReader object
pdf = PdfReader(BytesIO(pdf_data))

# Read data from the PDF fields if needed
# Note: PdfReader does not support form fields directly, so this may not be applicable
data = None  # Replace with code to process form fields if needed

# Read data from the PDF text content (if it's a text-based PDF)
text_content = ""
for page in pdf.pages:
    text_content += page.extract_text()

# Print the text content for debugging
#print('Printing the text content...')
#print(text_content)  

    
# Read data from the S3 object
#data = pandas.read_csv(obj['Body'])
#print('Printing the data frame...')
#print(data)

with open("/Users/ananya/Desktop/pdfs_question_answering/config.yml", "r") as f:
    config = yaml.safe_load(f)

OPENAI_API_KEY = config['OPENAI_KEY']
PDFS, NAMES, TXTS = [], [], []
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 500

# ----- Header of the app -----
st.title("Insurance Policy Summarization")
st.write("Simplify complex insurance policies with our cutting-edge AI tool. Instantly extract and condense key information, including coverage details, deductibles, and exclusions, into concise and easy-to-understand summaries. Make informed decisions and save time reading lengthy policy documents with our efficient summarization solution.")

# ----- Select and upload the file -----

# Create a Streamlit app title
st.write("Choose your policy from cloud")

session = boto3.Session(aws_access_key_id='', aws_secret_access_key='')
s3 = session.resource('s3')
s3_folder = 'user1/'

my_bucket = s3.Bucket('quadra1')

list_bucket = [""]
for my_bucket_object in my_bucket.objects.filter(Prefix="user1/"):
    #print(my_bucket_object.key)
    list_bucket.append(my_bucket_object.key)

selected_option = st.selectbox(
    "Select an option:",
    list_bucket
)
print(selected_option)

# Display the selected option
st.write("You selected:", selected_option)
st.header("Select the file to Summarize")
st.write("The file should be in PDF format.")
#file_1 = st.file_uploader("File 1")
#name_1 = st.text_input("Name of the file", value="Plan 1")




#Dropdown-Box Retrieval
if selected_option:
    obj = client.get_object(
    Bucket = '',
    Key = selected_option
    )
    pdf_data = obj['Body'].read()

    # Create a PdfReader object
    pdf = PdfReader(BytesIO(pdf_data))
    print("pdf name", pdf)

    # Read data from the PDF fields if needed
    # Note: PdfReader does not support form fields directly, so this may not be applicable
    data = None  # Replace with code to process form fields if needed

    # Read data from the PDF text content (if it's a text-based PDF)
    text_content = ""
    for page in pdf.pages:
        text_content += page.extract_text()
    text_contents = [text_content]
    
    # Create a temporary directory to store the temporary text file
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create a temporary text file
        tmp_txt_file = os.path.join(tmpdirname, "temp_text.txt")

        # Write the extracted text content to the temporary text file
        with open(tmp_txt_file, "w", encoding="utf-8") as txt_file:
            txt_file.write(text_content)

        # Convert the temporary text file to a list (as expected by the vectorize method)
        tmp_txt_file_contents = [tmp_txt_file]


        dataset_vectorizer = DatasetVectorizer()
        documents_1, texts_1, docsearch_1 = dataset_vectorizer.vectorize(tmp_txt_file_contents, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, openai_key=OPENAI_API_KEY)
        llm = OpenAI(model_name='gpt-3.5-turbo', temperature=0, openai_api_key=OPENAI_API_KEY)
        qa_chain_1 = VectorDBQA.from_chain_type(llm=llm, chain_type='stuff', vectorstore=docsearch_1)
        st.write("File vectorized successfully.")

        # ----- Generate the summary for the document -----
        st.header("Summary of the document")
        summary = ""
        
        # Example: Generate a summary by asking multiple questions and concatenate answers
        questions = [
             "What are the key benefits of this insurance plan?",
        "How does the deductible work?",
        "Tell me about the coverage for pre-existing conditions.",
        "What are standard definitions",
        #"What are the additional benefits offered",
        #"Could you explain the value-added benefits provided",
        #"What critical illnesses are covered under this policy",
        #"Could you clarify what permanent exclusions are under this insurance policy",
        ]
    
        
        for question in questions:
            answer = qa_chain_1.run(question)
            summary += f"{answer}\n"

        # Print the summary
        st.write(summary)

        # Create an input element for user questions
        user_question = st.text_input("Ask a question about the document")

        # Generate answers when the user clicks a button
        if st.button("Generate Answer"):
            if user_question:
                # Generate an answer to the user's question
                answer = qa_chain_1.run(user_question)
                st.write("Answer: ", answer)
            else:
                st.write("Please enter a question.")




file_1 = st.file_uploader("File 1")
name_1 = st.text_input("Name of the file", value="Plan 1")


# ----- Load the file -----
if file_1:
    # Save the uploaded PDF file
    pdf_path = "./data/" + file_1.name
    with open(pdf_path, "wb") as f:
        f.write(file_1.getbuffer())

    PDFS = [pdf_path]
    NAMES = [name_1]

    for pdf_path in PDFS:
        txt_path = pdf_path.replace(".pdf", ".txt")

        try:
            # Open the PDF using PdfReader
            pdf_reader = PyPDF2.PdfReader(pdf_path)

            # Extract text from the PDF
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            # Save the extracted text to a text file
            with open(txt_path, "w", encoding="utf-8") as text_file:
                text_file.write(text)

            # Append the text file path to the TXTS list
            TXTS.append(txt_path)

            st.write("File loaded and text extracted successfully.")
        except Exception as e:
            st.write(f"Error: {str(e)}")

    s3_folder = 'user1/'
    name = file_1.name
    s3_key = f'{s3_folder}{name}'# Replace with the desired S3 key

    # Create an S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id='',
        aws_secret_access_key='',
        region_name=''
    )

    # Upload the file to the S3 bucket
    try:
        s3_client.upload_file(pdf_path, '', s3_key)
        #print(f"Successfully uploaded {pdf_path} to S3 bucket {} with key {s3_key}")
    except Exception as e:
        print(f"Error uploading file to S3: {str(e)}")
        
    st.write("File loaded successfully.")

    dataset_vectorizer = DatasetVectorizer()
    documents_1, texts_1, docsearch_1 = dataset_vectorizer.vectorize([TXTS[0]], chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, openai_key=OPENAI_API_KEY)
    llm = OpenAI(model_name='gpt-3.5-turbo', temperature=0, openai_api_key=OPENAI_API_KEY)
    qa_chain_1 = VectorDBQA.from_chain_type(llm=llm, chain_type='stuff', vectorstore=docsearch_1)
    st.write("File vectorized successfully.")

    # ----- Generate the summary for the document -----
    st.header("Summary of the document")
    summary = ""
    
    # Example: Generate a summary by asking multiple questions and concatenate answers
    questions = [
        "What are the key benefits of this insurance plan?",
        "How does the deductible work?",
        "Tell me about the coverage for pre-existing conditions.",
        "What are standard definitions",
        #"What are the additional benefits offered",
        #"Could you explain the value-added benefits provided",
        
        #"What critical illnesses are covered under this policy",
        
        
    ]
 
    
    for question in questions:
        answer = qa_chain_1.run(question)
        summary += f"{answer}\n"

    # Print the summary
    st.write(summary)

    # Create an input element for user questions
    user_question = st.text_input("Ask a question about the document")

    # Generate answers when the user clicks a button
    if st.button("Generate Answer"):
        if user_question:
            # Generate an answer to the user's question
            answer = qa_chain_1.run(user_question)
            st.write("Answer: ", answer)
        else:
            st.write("Please enter a question.")
